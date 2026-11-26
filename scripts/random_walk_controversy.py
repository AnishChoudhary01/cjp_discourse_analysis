"""
Step 10: Random walk controversy between Pro-CJP and Anti-CJP users.

Steps 8 and 9 already show that communities point inward while Anti-CJP users
still talk to Pro-CJP users. This step asks the follow-up: if you start on one
side and keep moving along interactions, do you reach the other side?

The score is the random walk controversy measure of Garimella et al. (2016).
High-degree users on each side are stopping points. Everyone else is a starting
point or a corridor, including users with no stance. The walk follows an
undirected version of the interaction graph, because a mention on X points at
famous accounts and would otherwise end on those accounts almost every time.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.linalg import spsolve

sys.stdout.reconfigure(encoding="utf-8")

PRO = "Pro-CJP"
ANTI = "Anti-CJP"
ABSORB_TOLERANCE = 1e-6


def project_root():
    """Repository root, one level above this scripts/ file."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def dominant_stance_map(items_df):
    """
    One stance per user: the stance they express most often.

    The same rule is used in the step 9 mixing matrices, so these sides match
    that table. Neutral is left off both sides.
    """
    labeled = items_df.copy()
    labeled["Id"] = labeled["Id"].astype(str).str.strip().str.lower()
    labeled = labeled[labeled["stance_category"].isin([PRO, ANTI, "Neutral"])]
    return (
        labeled.groupby("Id")["stance_category"]
        .agg(lambda values: values.value_counts().index[0])
        .to_dict()
    )


def undirected_graph(edges_df):
    """Collapse directed, weighted interactions into one undirected weighted graph."""
    graph = nx.Graph()
    for row in edges_df.itertuples(index=False):
        source = str(row.Source).strip().lower()
        target = str(row.Target).strip().lower()
        if source == "" or target == "" or source == target:
            continue
        weight = float(row.Weight) if pd.notna(row.Weight) else 1.0
        if weight <= 0:
            continue
        if graph.has_edge(source, target):
            graph[source][target]["weight"] += weight
        else:
            graph.add_edge(source, target, weight=weight)
    return graph


def largest_mixed_component(graph, pro_users, anti_users):
    """Largest connected piece that contains at least one user from each side."""
    candidates = []
    for component in nx.connected_components(graph):
        has_pro = any(node in pro_users for node in component)
        has_anti = any(node in anti_users for node in component)
        if has_pro and has_anti:
            candidates.append(component)
    if not candidates:
        return None
    return max(candidates, key=len)


def authority_count(side_size):
    """
    How many high-degree users stop the walk on one side.

    Ten percent of that side, and never more than 10. A side must keep enough
    non-stopping users to start walks from.
    """
    if side_size <= 1:
        return 0
    return min(10, max(1, side_size // 10))


def top_authorities(component, side_members, count):
    """Highest weighted-degree users on a side. Ties break by account id."""
    ranked = sorted(
        (node for node in side_members if node in component),
        key=lambda node: (-component.degree(node, weight="weight"), node),
    )
    return ranked[:count]


def absorption_probabilities(component, pro_auth, anti_auth):
    """
    Chance that a walk from each non-stopping user hits each side's authorities.

    Authorities are absorbing. The linear system is the standard absorbing
    Markov chain: (I - Q) Z = R.
    """
    absorbing = set(pro_auth) | set(anti_auth)
    transient = [node for node in component.nodes if node not in absorbing]
    if not transient:
        return {}, []

    index = {node: position for position, node in enumerate(transient)}
    size = len(transient)
    transitions = sparse.lil_matrix((size, size), dtype=float)
    to_absorbing = np.zeros((size, 2), dtype=float)

    for node in transient:
        position = index[node]
        neighbors = list(component[node].items())
        total_weight = sum(data.get("weight", 1.0) for _, data in neighbors)
        if total_weight <= 0:
            continue
        for neighbor, data in neighbors:
            probability = data.get("weight", 1.0) / total_weight
            if neighbor in pro_auth:
                to_absorbing[position, 0] += probability
            elif neighbor in anti_auth:
                to_absorbing[position, 1] += probability
            elif neighbor in index:
                transitions[position, index[neighbor]] += probability

    system = sparse.eye(size, format="csc") - transitions.tocsc()
    reach_pro = np.asarray(spsolve(system, to_absorbing[:, 0]), dtype=float).ravel()
    reach_anti = np.asarray(spsolve(system, to_absorbing[:, 1]), dtype=float).ravel()
    probabilities = {
        node: (float(reach_pro[position]), float(reach_anti[position]))
        for node, position in index.items()
    }
    return probabilities, transient


def mean_side_probabilities(probabilities, starters):
    """Average absorption chances for the users who start on one side."""
    usable = []
    for node in starters:
        if node not in probabilities:
            continue
        reach_pro, reach_anti = probabilities[node]
        if reach_pro + reach_anti < 1.0 - 1e-3:
            continue
        usable.append((reach_pro, reach_anti))
    if not usable:
        return None
    stacked = np.asarray(usable, dtype=float)
    return stacked.mean(axis=0), len(usable)


def random_walk_controversy(graph, pro_users, anti_users):
    """
    Garimella random walk controversy on one graph.

    RWC = P(Pro ends Pro) * P(Anti ends Anti) - P(Pro ends Anti) * P(Anti ends Pro).
    Near 1 means a walker stays on the side they started. Near 0, or below 0,
    means the walker reaches the other side.
    """
    component_nodes = largest_mixed_component(graph, pro_users, anti_users)
    if component_nodes is None:
        return {
            "Status": "No shared component",
            "RWC": None,
        }

    component = graph.subgraph(component_nodes).copy()
    pro_in_graph = [node for node in component.nodes if node in pro_users]
    anti_in_graph = [node for node in component.nodes if node in anti_users]
    pro_k = authority_count(len(pro_in_graph))
    anti_k = authority_count(len(anti_in_graph))
    if pro_k == 0 or anti_k == 0:
        return {"Status": "Too few users on one side", "RWC": None}

    pro_auth = top_authorities(component, pro_users, pro_k)
    anti_auth = top_authorities(component, anti_users, anti_k)
    probabilities, _transient = absorption_probabilities(component, set(pro_auth), set(anti_auth))

    pro_starts = [node for node in pro_in_graph if node not in pro_auth]
    anti_starts = [node for node in anti_in_graph if node not in anti_auth]
    pro_mean = mean_side_probabilities(probabilities, pro_starts)
    anti_mean = mean_side_probabilities(probabilities, anti_starts)
    if pro_mean is None or anti_mean is None:
        return {"Status": "Walks did not reach a stopping user", "RWC": None}

    (pro_to_pro, pro_to_anti), pro_start_count = pro_mean
    (anti_to_pro, anti_to_anti), anti_start_count = anti_mean
    rwc = (pro_to_pro * anti_to_anti) - (pro_to_anti * anti_to_pro)
    return {
        "Status": "Computed",
        "Component_Nodes": component.number_of_nodes(),
        "Component_Edges": component.number_of_edges(),
        "Pro_Users": len(pro_in_graph),
        "Anti_Users": len(anti_in_graph),
        "Pro_Authorities": pro_k,
        "Anti_Authorities": anti_k,
        "Pro_Starts": pro_start_count,
        "Anti_Starts": anti_start_count,
        "P_Pro_to_Pro": round(pro_to_pro, 4),
        "P_Pro_to_Anti": round(pro_to_anti, 4),
        "P_Anti_to_Anti": round(anti_to_anti, 4),
        "P_Anti_to_Pro": round(anti_to_pro, 4),
        "RWC": round(float(rwc), 4),
    }


def check_separated_graph_scores_higher_than_mixed_graph():
    """
    A known pair of toy graphs. One bridge should score higher controversy
    than the same two groups with links between every opposing pair.
    """
    pro = {f"p{i}" for i in range(8)}
    anti = {f"a{i}" for i in range(8)}

    separated = nx.Graph()
    mixed = nx.Graph()
    for i in range(8):
        for j in range(i + 1, 8):
            separated.add_edge(f"p{i}", f"p{j}", weight=1.0)
            separated.add_edge(f"a{i}", f"a{j}", weight=1.0)
            mixed.add_edge(f"p{i}", f"p{j}", weight=1.0)
            mixed.add_edge(f"a{i}", f"a{j}", weight=1.0)
        for j in range(8):
            mixed.add_edge(f"p{i}", f"a{j}", weight=1.0)
    separated.add_edge("p0", "a0", weight=1.0)

    separated_score = random_walk_controversy(separated, pro, anti)
    mixed_score = random_walk_controversy(mixed, pro, anti)
    if separated_score["RWC"] is None or mixed_score["RWC"] is None:
        raise RuntimeError("Toy graphs did not produce a controversy score.")
    if separated_score["RWC"] <= mixed_score["RWC"]:
        raise RuntimeError(
            "Expected the barely connected graph to be more controversial "
            f"({separated_score['RWC']}) than the mixed graph ({mixed_score['RWC']})."
        )
    return separated_score["RWC"], mixed_score["RWC"]


def side_sets(stance_map):
    """Split the user map into the two sides the walk compares."""
    pro_users = {user for user, stance in stance_map.items() if stance == PRO}
    anti_users = {user for user, stance in stance_map.items() if stance == ANTI}
    return pro_users, anti_users


def score_row(platform, phase, result):
    """One output row. Missing scores stay blank instead of a fake zero."""
    row = {
        "Platform": platform,
        "Phase": phase,
        "Status": result.get("Status"),
        "Component_Nodes": result.get("Component_Nodes"),
        "Component_Edges": result.get("Component_Edges"),
        "Pro_Users": result.get("Pro_Users"),
        "Anti_Users": result.get("Anti_Users"),
        "Pro_Authorities": result.get("Pro_Authorities"),
        "Anti_Authorities": result.get("Anti_Authorities"),
        "Pro_Starts": result.get("Pro_Starts"),
        "Anti_Starts": result.get("Anti_Starts"),
        "P_Pro_to_Pro": result.get("P_Pro_to_Pro"),
        "P_Pro_to_Anti": result.get("P_Pro_to_Anti"),
        "P_Anti_to_Anti": result.get("P_Anti_to_Anti"),
        "P_Anti_to_Pro": result.get("P_Anti_to_Pro"),
        "RWC": result.get("RWC"),
    }
    return row


def plot_scores(scores_df, out_path):
    """One bar per graph. The label is the plain reading of that bar."""
    plotted = scores_df[scores_df["RWC"].notna()].copy()
    plotted["Label"] = plotted["Platform"] + "\n" + plotted["Phase"]
    colors = ["#1f4e79" if platform == "X" else "#b85c38" for platform in plotted["Platform"]]

    figure, axis = plt.subplots(figsize=(8.5, 4.8))
    positions = np.arange(len(plotted))
    axis.bar(positions, plotted["RWC"], color=colors, width=0.72)
    axis.axhline(0, color="#444444", linewidth=0.8)
    axis.set_xticks(positions)
    axis.set_xticklabels(plotted["Label"])
    axis.set_ylabel("Random walk controversy")
    axis.set_ylim(-1, 1)
    axis.set_title("Do the two sides meet? Higher means they stay apart")
    for position, score in zip(positions, plotted["RWC"]):
        axis.text(position, score + (0.04 if score >= 0 else -0.08), f"{score:.2f}", ha="center", va="bottom" if score >= 0 else "top", fontsize=9)
    figure.tight_layout()
    figure.savefig(out_path, dpi=160)
    plt.close(figure)


def run_random_walk_controversy():
    """Score X, each X phase, and Reddit. Write the table and the bar chart."""
    separated_rwc, mixed_rwc = check_separated_graph_scores_higher_than_mixed_graph()
    print("=======================================================================")
    print("      STEP 10: RANDOM WALK CONTROVERSY (PRO-CJP VS ANTI-CJP)          ")
    print("=======================================================================")
    print(f"Check: barely connected toy graph RWC = {separated_rwc:.2f}")
    print(f"Check: densely cross-linked toy graph RWC = {mixed_rwc:.2f}")
    print("Sides are users, by the stance they post most often.")
    print("No Louvain community is an Anti-CJP majority, on X or on Reddit.\n")

    root = project_root()
    x_edges = pd.read_csv(os.path.join(root, "output", "03_network_analysis", "x", "x_edges.csv"))
    x_phase_edges = pd.read_csv(os.path.join(root, "output", "03_network_analysis", "x", "x_edges_by_phase.csv"))
    r_edges = pd.read_csv(os.path.join(root, "output", "03_network_analysis", "reddit", "edges.csv"))
    x_items = pd.read_csv(os.path.join(root, "output", "06_stance_analysis", "x", "x_tweets_with_stance.csv"), usecols=["Id", "stance_category"])
    r_items = pd.read_csv(os.path.join(root, "output", "06_stance_analysis", "reddit", "reddit_items_with_stance.csv"), usecols=["Id", "stance_category"])

    x_pro, x_anti = side_sets(dominant_stance_map(x_items))
    r_pro, r_anti = side_sets(dominant_stance_map(r_items))

    rows = []
    x_graph = undirected_graph(x_edges)
    rows.append(score_row("X", "Full", random_walk_controversy(x_graph, x_pro, x_anti)))

    for phase in ["Before", "Peak", "After"]:
        phase_edges = x_phase_edges[x_phase_edges["Phase"].astype(str).str.strip() == phase]
        phase_graph = undirected_graph(phase_edges)
        rows.append(score_row("X", phase, random_walk_controversy(phase_graph, x_pro, x_anti)))

    reddit_graph = undirected_graph(r_edges)
    rows.append(score_row("Reddit", "Full", random_walk_controversy(reddit_graph, r_pro, r_anti)))

    scores = pd.DataFrame(rows)
    out_dir = os.path.join(root, "output", "10_random_walk_controversy")
    os.makedirs(out_dir, exist_ok=True)
    table_path = os.path.join(out_dir, "rwc_scores.csv")
    plot_path = os.path.join(out_dir, "rwc_by_graph.png")
    scores.to_csv(table_path, index=False, encoding="utf-8")
    plot_scores(scores, plot_path)

    print(scores.to_string(index=False))
    print(f"\nSaved table: {table_path}")
    print(f"Saved chart: {plot_path}")
    return scores


if __name__ == "__main__":
    run_random_walk_controversy()
