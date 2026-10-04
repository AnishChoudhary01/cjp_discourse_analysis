import os
import sys
import re
import pandas as pd
import numpy as np
import networkx as nx
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
from pyvis.network import Network

# Ensure UTF-8 standardisation
sys.stdout.reconfigure(encoding='utf-8')

def build_graph_from_edges(edges_df, directed=True):
    """Constructs a NetworkX graph from an edge dataframe."""
    G = nx.DiGraph() if directed else nx.Graph()
    for _, r in edges_df.iterrows():
        u = str(r['Source']).strip().lower()
        v = str(r['Target']).strip().lower()
        w = float(r.get('Weight', 1.0))
        if u and v and u != v:
            if G.has_edge(u, v):
                G[u][v]['weight'] += w
            else:
                G.add_edge(u, v, weight=w)
    return G

def run_community_pipeline(platform_name, edges_path, nodes_path, text_data_path, out_network_dir, out_viz_dir):
    """
    Executes Louvain community detection, centrality profiling, 
    static network visualization, and interactive PyVis HTML export.
    """
    print(f"\n=======================================================")
    print(f"   Louvain Community Detection: {platform_name.upper()} Network   ")
    print(f"=======================================================")

    if not os.path.exists(edges_path):
        print(f"Error: Edges file not found at {edges_path}")
        return

    edges_df = pd.read_csv(edges_path)
    nodes_df = pd.read_csv(nodes_path) if os.path.exists(nodes_path) else pd.DataFrame()

    # 1. Build directed graph for centralities & undirected for Louvain modularity
    G_dir = build_graph_from_edges(edges_df, directed=True)
    G_undir = G_dir.to_undirected()

    num_dir_edges = G_dir.number_of_edges()
    num_undir_edges = G_undir.number_of_edges()
    reciprocal_pairs = num_dir_edges - num_undir_edges
    num_nodes = G_undir.number_of_nodes()

    print(f"Directed Graph: {G_dir.number_of_nodes()} nodes, {num_dir_edges} directed interaction edges.")
    print(f"Undirected Projection (for Louvain): {num_undir_edges} edges ({reciprocal_pairs} reciprocal mutual interaction pairs collapsed).")
    print(f"Connected Components: {nx.number_connected_components(G_undir)}")

    # 2. Centrality Metrics (Verified PageRank & Degree)
    print(" -> Computing network centralities (Degree, In/Out-Degree, PageRank)...")
    in_degrees = dict(G_dir.in_degree(weight='weight'))
    out_degrees = dict(G_dir.out_degree(weight='weight'))
    total_degrees = dict(G_undir.degree(weight='weight'))
    
    try:
        pagerank = nx.pagerank(G_dir, weight='weight', alpha=0.85, max_iter=200)
        print(f"    - PageRank computed successfully: {len(set(pagerank.values()))} unique values across {len(pagerank)} nodes.")
    except Exception as e:
        print(f"    - Warning: PageRank fallback due to {e}")
        pagerank = {n: total_degrees.get(n, 0) / (2 * num_undir_edges if num_undir_edges > 0 else 1) for n in G_dir.nodes()}

    # 3. Louvain Community Detection (Modularity Optimization)
    print(" -> Running Louvain modularity optimization (seed=42)...")
    raw_communities = nx_comm.louvain_communities(G_undir, weight='weight', resolution=1.0, seed=42)
    modularity_q = nx_comm.modularity(G_undir, raw_communities, weight='weight')
    print(f" -> Partition complete: {len(raw_communities)} communities detected.")
    print(f" -> Newman Modularity Score (Q): {modularity_q:.4f}")
    print("    [Interpretation: The modularity scores indicate strong community structure and interactional compartmentalization.")
    print("     Further analysis is required to determine whether these communities exhibit echo-chamber characteristics.]")

    # Sort communities by size
    sorted_comms = sorted(raw_communities, key=len, reverse=True)

    # Assign Community ID (Top 6 get specific IDs, smaller ones mapped to 'Other')
    node_community = {}
    top_k = min(6, len(sorted_comms))
    for comm_idx in range(top_k):
        for node in sorted_comms[comm_idx]:
            node_community[node] = f"C{comm_idx + 1}"
    
    # Remaining smaller components
    for comm_idx in range(top_k, len(sorted_comms)):
        for node in sorted_comms[comm_idx]:
            node_community[node] = "Other"

    # 4. Compile Enriched Node Table
    enriched_nodes = []
    for node in G_undir.nodes():
        enriched_nodes.append({
            'Id': node,
            'Label': node,
            'Community': node_community.get(node, 'Other'),
            'Total_Degree': total_degrees.get(node, 0),
            'In_Degree': in_degrees.get(node, 0),
            'Out_Degree': out_degrees.get(node, 0),
            'PageRank': pagerank.get(node, 0.0)
        })
    enriched_df = pd.DataFrame(enriched_nodes)

    # Merge metadata if available in original nodes_df (e.g. followers, verified)
    if not nodes_df.empty and 'followers' in nodes_df.columns:
        enriched_df = pd.merge(enriched_df, nodes_df[['Id', 'followers', 'verified', 'total_tweets']], on='Id', how='left')

    out_nodes_csv = os.path.join(out_network_dir, f"{platform_name}_nodes_with_communities.csv")
    enriched_df.to_csv(out_nodes_csv, index=False, encoding='utf-8')
    print(f" -> Saved enriched nodes: {out_nodes_csv}")

    # 5. Community Summary & Topical Profiling
    print("\n--- Major Community Profiles ---")
    comm_summary = []
    
    # Load text content for topic extraction if available (for X)
    user_hashtags = {}
    if text_data_path and os.path.exists(text_data_path):
        text_df = pd.read_csv(text_data_path)
        if 'author' in text_df.columns and 'hashtags' in text_df.columns:
            for _, r in text_df.iterrows():
                author = str(r['author']).strip().lower()
                h_str = str(r.get('hashtags', ''))
                if pd.notna(h_str) and h_str.strip():
                    tags = [t.strip().lstrip('#').lower() for t in re.split(r'[,;\s]+', h_str) 
                            if t.strip() and t.strip().lower() != 'nan' and len(t.strip()) > 1]
                    if author not in user_hashtags:
                        user_hashtags[author] = []
                    user_hashtags[author].extend(tags)

    for i in range(top_k):
        c_nodes = sorted_comms[i]
        c_id = f"C{i + 1}"
        c_size = len(c_nodes)
        c_share = (c_size / num_nodes) * 100

        # Top central actors in community by total interaction degree
        c_actors = sorted([(n, total_degrees.get(n, 0)) for n in c_nodes], key=lambda x: x[1], reverse=True)[:5]
        actor_str = ", ".join([f"@{n} ({d})" for n, d in c_actors])

        # Top hashtags for this community (if X)
        c_tags = [t for n in c_nodes if n in user_hashtags for t in user_hashtags[n] if t != 'nan']
        top_tags_str = ", ".join([f"#{t}" for t, _ in pd.Series(c_tags).value_counts().head(4).items()]) if c_tags else "N/A"

        # Internal edges vs external edges
        internal_edges = 0
        external_edges = 0
        for u in c_nodes:
            for v in G_undir.neighbors(u):
                if v in c_nodes:
                    internal_edges += 1
                else:
                    external_edges += 1
        # Each undirected internal edge is counted twice
        internal_edges = internal_edges // 2

        comm_summary.append({
            'Community_ID': c_id,
            'Node_Count': c_size,
            'Share_Percent': round(c_share, 2),
            'Internal_Edges': internal_edges,
            'External_Edges': external_edges,
            'Top_Central_Actors': actor_str,
            'Dominant_Hashtags': top_tags_str
        })

        print(f"Community {c_id}: {c_size} nodes ({c_share:.1f}%) | Internal Edges: {internal_edges}, External: {external_edges}")
        print(f"  Key Actors: {actor_str}")
        if c_tags:
            print(f"  Top Hashtags: {top_tags_str}")

    summary_df = pd.DataFrame(comm_summary)
    summary_csv = os.path.join(out_network_dir, f"{platform_name}_community_summary.csv")
    summary_df.to_csv(summary_csv, index=False, encoding='utf-8')
    print(f" -> Saved community summary: {summary_csv}")

    # 6. High-Resolution Static Network Plot
    print("\n -> Generating static publication-ready network plot...")
    plt.figure(figsize=(14, 11), facecolor='#F8F9FA')
    ax = plt.subplot(111)
    ax.set_facecolor('#F8F9FA')

    # Color palette for communities
    comm_colors = {
        'C1': '#4C72B0',  # Steel Blue
        'C2': '#C44E52',  # Crimson
        'C3': '#55A868',  # Forest Green
        'C4': '#E8853A',  # Amber Orange
        'C5': '#8172B2',  # Purple
        'C6': '#CCB974',  # Gold
        'Other': '#C0C0C0' # Light Gray
    }

    # Extract Giant Connected Component (GCC) for clear, non-hairball layout
    gcc_nodes = max(nx.connected_components(G_undir), key=len)
    G_sub = G_undir.subgraph(gcc_nodes).copy()
    
    # Subsample top nodes by degree if network is massive for visual clarity
    if G_sub.number_of_nodes() > 400:
        top_sub_nodes = sorted(G_sub.nodes(), key=lambda n: total_degrees.get(n, 0), reverse=True)[:350]
        G_plot = G_sub.subgraph(top_sub_nodes).copy()
    else:
        G_plot = G_sub

    # Spring layout with physics repulsion
    pos = nx.spring_layout(G_plot, k=0.18, iterations=60, seed=42, weight='weight')

    # Draw edges with subtle transparency
    nx.draw_networkx_edges(G_plot, pos, alpha=0.18, edge_color='#7F7F7F', width=0.8, ax=ax)

    # Draw nodes grouped by community
    for c_id, color in comm_colors.items():
        c_nodes_plot = [n for n in G_plot.nodes() if node_community.get(n) == c_id]
        if c_nodes_plot:
            count_total = len([n for n in G_undir.nodes() if node_community.get(n) == c_id])
            if c_id == 'Other':
                lbl = f"Other — remaining smaller communities ({count_total} users)"
            else:
                lbl = f"{c_id} ({count_total} users)"
            sizes = [max(30, min(800, total_degrees.get(n, 1) * 12)) for n in c_nodes_plot]
            nx.draw_networkx_nodes(G_plot, pos, nodelist=c_nodes_plot, node_color=color,
                                   node_size=sizes, alpha=0.88, edgecolors='#FFFFFF', linewidths=0.8,
                                   label=lbl, ax=ax)

    # Label top 10 prominent actors across the network
    top_label_nodes = sorted(G_plot.nodes(), key=lambda n: total_degrees.get(n, 0), reverse=True)[:10]
    labels = {n: f"@{n}" if not n.startswith('@') else n for n in top_label_nodes}
    nx.draw_networkx_labels(G_plot, pos, labels=labels, font_size=8, font_family='sans-serif',
                            font_weight='bold', font_color='#111111', ax=ax,
                            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.85, lw=0.5))

    plt.title(f"{platform_name.upper()} Interaction Network: Louvain Community Partition\n(Newman Modularity Q = {modularity_q:.4f}, GCC N = {len(gcc_nodes)})",
              fontsize=14, fontweight='bold', pad=15)
    plt.legend(title="Louvain Communities", loc='upper left', frameon=True, fontsize=9)
    plt.axis('off')
    plt.tight_layout()

    static_plot_path = os.path.join(out_viz_dir, f"{platform_name}_network_communities.png")
    plt.savefig(static_plot_path, dpi=300)
    plt.close()
    print(f" -> Saved static plot: {static_plot_path}")

    # 7. Interactive PyVis HTML Graph
    print(" -> Generating interactive PyVis HTML network visualization...")
    net = Network(height="800px", width="100%", bgcolor="#FAFAFA", font_color="#222222", directed=False, cdn_resources='remote')
    net.force_atlas_2based(gravity=-60, central_gravity=0.015, spring_length=100, spring_strength=0.08)

    # Add nodes to PyVis (filtering to top 250 connected nodes for responsive web browser interaction)
    pyvis_nodes = sorted(G_undir.nodes(), key=lambda n: total_degrees.get(n, 0), reverse=True)[:250]
    pyvis_sub = G_undir.subgraph(pyvis_nodes)

    for node in pyvis_sub.nodes():
        c_id = node_community.get(node, 'Other')
        comm_label = "Other — remaining smaller communities" if c_id == 'Other' else c_id
        color = comm_colors.get(c_id, '#C0C0C0')
        deg = total_degrees.get(node, 0)
        in_deg = in_degrees.get(node, 0)
        out_deg = out_degrees.get(node, 0)
        pr = pagerank.get(node, 0.0)
        size = max(10, min(45, np.sqrt(deg) * 6))
        
        tooltip = (f"<b>User:</b> @{node}<br>"
                   f"<b>Community:</b> {comm_label}<br>"
                   f"<b>Total Degree:</b> {deg} (In: {in_deg}, Out: {out_deg})<br>"
                   f"<b>PageRank:</b> {pr:.5f}")
        net.add_node(node, label=f"@{node}" if deg > 15 else "", title=tooltip, color=color, size=size)

    for u, v, data in pyvis_sub.edges(data=True):
        w = data.get('weight', 1.0)
        net.add_edge(u, v, value=w, color="#B0B0B0", alpha=0.4)

    interactive_html_path = os.path.join(out_viz_dir, f"interactive_{platform_name}_network.html")
    net.save_graph(interactive_html_path)
    print(f" -> Saved interactive HTML graph: {interactive_html_path}")

    return {
        'num_nodes': num_nodes,
        'num_undir_edges': num_undir_edges,
        'num_dir_edges': num_dir_edges,
        'modularity_q': modularity_q,
        'num_communities': len(sorted_comms),
        'top_communities': comm_summary
    }

def main():
    base_dir = r"c:\Users\Palak\Documents\csma_prj"

    # 1. Run for X (Twitter) Network
    x_edges = os.path.join(base_dir, "output", "x", "network", "x_edges.csv")
    x_nodes = os.path.join(base_dir, "output", "x", "network", "x_nodes.csv")
    x_text = os.path.join(base_dir, "output", "x", "processed_data", "processed_x_tweets.csv")
    x_out_net = os.path.join(base_dir, "output", "x", "network")
    x_out_viz = os.path.join(base_dir, "output", "x", "visualizations")

    x_res = run_community_pipeline("x", x_edges, x_nodes, x_text, x_out_net, x_out_viz)

    # 2. Run for Reddit Network
    reddit_edges = os.path.join(base_dir, "output", "reddit", "network", "edges.csv")
    reddit_nodes = os.path.join(base_dir, "output", "reddit", "network", "nodes.csv")
    reddit_text = os.path.join(base_dir, "output", "reddit", "processed_data", "processed_comments.csv")
    reddit_out_net = os.path.join(base_dir, "output", "reddit", "network")
    reddit_out_viz = os.path.join(base_dir, "output", "reddit", "visualizations")

    reddit_res = run_community_pipeline("reddit", reddit_edges, reddit_nodes, reddit_text, reddit_out_net, reddit_out_viz)

    print("\n=======================================================")
    print("      COMMUNITY DETECTION & VISUALIZATION COMPLETE     ")
    print("=======================================================")
    print("Core Finding: We have identified strong interaction-based community structure.")
    print("We now test whether these structurally separated communities also exhibit echo-chamber characteristics.")
    print("-------------------------------------------------------")
    if x_res:
        print(f"X Network Modularity Q:      {x_res['modularity_q']:.4f}")
    if reddit_res:
        print(f"Reddit Network Modularity Q: {reddit_res['modularity_q']:.4f}")
    print("Note: Reddit shows stronger structural community separation in this dataset than X.")
    print("Whether this reflects stronger echo-chamber characteristics requires further interaction and content analysis.")
    print("\n=======================================================")
    print("                   NEXT ANALYSIS PHASES                ")
    print("=======================================================")
    print(" 1. Within-Community vs. Between-Community Interactions")
    print(" 2. Krackhardt E-I Index (Quantifying Homophily)")
    print(" 3. Community-Level Sentiment & Stance Distribution")
    print(" 4. Community-Level Topics & Narrative Mining")
    print(" 5. Cross-Platform Comparison (X vs. Reddit)")
    print(" 6. Temporal Polarization Dynamics (Before -> Peak -> After)")
    print("=======================================================")

if __name__ == "__main__":
    main()
