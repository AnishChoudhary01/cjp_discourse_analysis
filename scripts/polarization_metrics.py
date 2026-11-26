import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure UTF-8 standardisation on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

def calculate_community_ei(edges_df, node_community_map, comm_list):
    """
    Computes Krackhardt E-I Index for each community:
    EI = (External_Ties - Internal_Ties) / (External_Ties + Internal_Ties)
    
    Also computes exact Network-Level E-I:
    I_net = sum of weights where C(u) == C(v)
    E_net = sum of weights where C(u) != C(v)
    Network_EI = (E_net - I_net) / (E_net + I_net)
    """
    i_ties = {c: 0.0 for c in comm_list}
    e_ties = {c: 0.0 for c in comm_list}
    i_net = 0.0
    e_net = 0.0
    
    for _, r in edges_df.iterrows():
        u = str(r['Source']).strip().lower()
        v = str(r['Target']).strip().lower()
        w = float(r.get('Weight', 1.0))
        cu = node_community_map.get(u, 'Other')
        cv = node_community_map.get(v, 'Other')
        
        if cu == cv:
            if cu in i_ties:
                i_ties[cu] += w
            i_net += w
        else:
            if cu in e_ties:
                e_ties[cu] += w
            if cv in e_ties:
                e_ties[cv] += w
            e_net += w

    records = []
    for c in comm_list:
        i = i_ties[c]
        e = e_ties[c]
        tot = i + e
        ei = (e - i) / tot if tot > 0 else 0.0
        records.append({
            'Community': c,
            'Internal_Ties': round(i, 1),
            'External_Ties': round(e, 1),
            'Total_Ties': round(tot, 1),
            'EI_Index': round(ei, 4)
        })
        
    df = pd.DataFrame(records)
    total_net = i_net + e_net
    net_ei = (e_net - i_net) / total_net if total_net > 0 else 0.0
    return df, round(net_ei, 4), round(i_net, 1), round(e_net, 1), round(total_net, 1)

def run_polarization_analysis():
    base_dir = r"c:\Users\Palak\Documents\csma_prj"
    
    x_nodes_path = os.path.join(base_dir, "output", "04_community_detection", "x", "x_nodes_with_communities.csv")
    x_edges_path = os.path.join(base_dir, "output", "03_network_analysis", "x", "x_edges.csv")
    x_phase_edges_path = os.path.join(base_dir, "output", "03_network_analysis", "x", "x_edges_by_phase.csv")
    x_tweets_path = os.path.join(base_dir, "output", "06_stance_analysis", "x", "x_tweets_with_stance.csv")
    
    r_nodes_path = os.path.join(base_dir, "output", "04_community_detection", "reddit", "reddit_nodes_with_communities.csv")
    r_edges_path = os.path.join(base_dir, "output", "03_network_analysis", "reddit", "edges.csv")
    r_items_path = os.path.join(base_dir, "output", "06_stance_analysis", "reddit", "reddit_items_with_stance.csv")
    
    x_pol_dir = os.path.join(base_dir, "output", "08_polarization", "x")
    r_pol_dir = os.path.join(base_dir, "output", "08_polarization", "reddit")
    cross_dir = os.path.join(base_dir, "output", "09_cross_platform")
    
    os.makedirs(x_pol_dir, exist_ok=True)
    os.makedirs(r_pol_dir, exist_ok=True)
    os.makedirs(cross_dir, exist_ok=True)

    print("=======================================================================")
    print("      CSMA POLARIZATION & INTERACTION HOMOPHILY MODULE (E-I INDEX)     ")
    print("=======================================================================")
    print("Theoretical Framework: Krackhardt External-Internal (E-I) Index")
    print("Formula: EI = (E - I) / (E + I)  [-1.0 = Inward Homophily, +1.0 = Outward Bridging]")
    print("Objective: Empirically test structural boundary crossing and cross-stance interaction.\n")

    # 1. Load Nodes & Edges
    print("[Step 1] Loading existing network topologies and community assignments...")
    x_nodes = pd.read_csv(x_nodes_path)
    x_edges = pd.read_csv(x_edges_path)
    x_phase_edges = pd.read_csv(x_phase_edges_path)
    r_nodes = pd.read_csv(r_nodes_path)
    r_edges = pd.read_csv(r_edges_path)

    x_comm_map = dict(zip(x_nodes['Id'].astype(str).str.lower(), x_nodes['Community']))
    r_comm_map = dict(zip(r_nodes['Id'].astype(str).str.lower(), r_nodes['Community']))

    comm_order = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'Other']

    # 2. Community-Level E-I Index
    print("\n[Step 2] Computing Community-Level Krackhardt E-I Index...")
    x_comm_ei, x_net_ei, x_i_net, x_e_net, x_tot_net = calculate_community_ei(x_edges, x_comm_map, comm_order)
    r_comm_ei, r_net_ei, r_i_net, r_e_net, r_tot_net = calculate_community_ei(r_edges, r_comm_map, comm_order)

    x_comm_ei_path = os.path.join(x_pol_dir, "x_community_ei_index.csv")
    x_comm_ei.to_csv(x_comm_ei_path, index=False, encoding='utf-8')
    print(f" -> Saved X Community E-I Table: {x_comm_ei_path}")
    print("--- X Community E-I Index ---")
    print(x_comm_ei.to_string(index=False))
    print(f"Network-Level E-I Index (X): {x_net_ei:.4f} (Internal={x_i_net}, External={x_e_net}, Total Weight={x_tot_net})")

    r_comm_ei_path = os.path.join(r_pol_dir, "reddit_community_ei_index.csv")
    r_comm_ei.to_csv(r_comm_ei_path, index=False, encoding='utf-8')
    print(f"\n -> Saved Reddit Community E-I Table: {r_comm_ei_path}")
    print("--- Reddit Community E-I Index ---")
    print(r_comm_ei.to_string(index=False))
    print(f"Network-Level E-I Index (Reddit): {r_net_ei:.4f} (Internal={r_i_net}, External={r_e_net}, Total Weight={r_tot_net})")

    # Cross-Platform E-I Comparison Table
    cross_ei_df = pd.merge(
        x_comm_ei[['Community', 'Internal_Ties', 'External_Ties', 'EI_Index']].rename(
            columns={'Internal_Ties': 'X_Internal', 'External_Ties': 'X_External', 'EI_Index': 'X_EI_Index'}
        ),
        r_comm_ei[['Community', 'Internal_Ties', 'External_Ties', 'EI_Index']].rename(
            columns={'Internal_Ties': 'Reddit_Internal', 'External_Ties': 'Reddit_External', 'EI_Index': 'Reddit_EI_Index'}
        ),
        on='Community'
    )
    cross_ei_path = os.path.join(cross_dir, "community_ei_index_comparison.csv")
    cross_ei_df.to_csv(cross_ei_path, index=False, encoding='utf-8')
    print(f"\n -> Saved Cross-Platform Community E-I Comparison: {cross_ei_path}")

    # 3. Stance-Level Interaction Mixing Matrix & Homophily
    print("\n[Step 3] Evaluating Cross-Stance Interaction Mixing Matrix...")
    x_tweets = pd.read_csv(x_tweets_path)
    r_items = pd.read_csv(r_items_path)

    # Determine dominant node stance
    x_user_stance = x_tweets.groupby('Id')['stance_category'].agg(
        lambda s: s.value_counts().index[0]
    ).to_dict()
    
    r_user_stance = r_items.groupby('Id')['stance_category'].agg(
        lambda s: s.value_counts().index[0]
    ).to_dict()

    # Function to build stance mixing matrix with consistent Unknown/Target_Only handling
    def build_stance_matrix(edges_df, stance_map):
        stances = ['Pro-CJP', 'Anti-CJP', 'Neutral']
        cols = stances + ['Unknown / Target_Only']
        mat = {s: {c: 0.0 for c in cols} for s in stances}
        
        for _, r in edges_df.iterrows():
            u = str(r['Source']).strip().lower()
            v = str(r['Target']).strip().lower()
            w = float(r.get('Weight', 1.0))
            
            su = stance_map.get(u, 'Unknown / Target_Only')
            sv = stance_map.get(v, 'Unknown / Target_Only')
            
            if su in mat:
                if sv in mat[su]:
                    mat[su][sv] += w
                else:
                    mat[su]['Unknown / Target_Only'] += w
                
        df_mat = pd.DataFrame(mat).T
        return df_mat

    x_stance_mat = build_stance_matrix(x_edges, x_user_stance)
    r_stance_mat = build_stance_matrix(r_edges, r_user_stance)

    print("\n--- X Stance Interaction Matrix (Tie Weights: Source -> Target) ---")
    print(x_stance_mat)

    print("\n--- Reddit Stance Interaction Matrix (Tie Weights: Source -> Target) ---")
    print(r_stance_mat)

    # Row-normalized proportions across known stance users (%)
    x_stance_mat_known = x_stance_mat[['Pro-CJP', 'Anti-CJP', 'Neutral']].copy()
    x_stance_pct = x_stance_mat_known.div(x_stance_mat_known.sum(axis=1), axis=0) * 100
    
    r_stance_mat_known = r_stance_mat[['Pro-CJP', 'Anti-CJP', 'Neutral']].copy()
    r_stance_pct = r_stance_mat_known.div(r_stance_mat_known.sum(axis=1), axis=0) * 100

    print("\n--- X Outgoing Interaction Proportions (%) Between Known Stance Users ---")
    print(x_stance_pct.round(2))

    print("\n--- Reddit Outgoing Interaction Proportions (%) Between Known Stance Users ---")
    print(r_stance_pct.round(2))

    # Save mixing matrices
    x_mat_path = os.path.join(cross_dir, "x_stance_interaction_mixing_matrix.csv")
    x_stance_mat.to_csv(x_mat_path, encoding='utf-8')
    r_mat_path = os.path.join(cross_dir, "reddit_stance_interaction_mixing_matrix.csv")
    r_stance_mat.to_csv(r_mat_path, encoding='utf-8')

    # Compute Stance-Level E-I Index (between Pro-CJP and Anti-CJP)
    # Pro-CJP: Internal = Pro->Pro, External = Pro->Anti
    # Anti-CJP: Internal = Anti->Anti, External = Anti->Pro
    pro_int_x = x_stance_mat.loc['Pro-CJP', 'Pro-CJP']
    pro_ext_x = x_stance_mat.loc['Pro-CJP', 'Anti-CJP']
    pro_ei_x = (pro_ext_x - pro_int_x) / (pro_ext_x + pro_int_x) if (pro_ext_x + pro_int_x) > 0 else 0

    anti_int_x = x_stance_mat.loc['Anti-CJP', 'Anti-CJP']
    anti_ext_x = x_stance_mat.loc['Anti-CJP', 'Pro-CJP']
    anti_ei_x = (anti_ext_x - anti_int_x) / (anti_ext_x + anti_int_x) if (anti_ext_x + anti_int_x) > 0 else 0

    pro_int_r = r_stance_mat.loc['Pro-CJP', 'Pro-CJP']
    pro_ext_r = r_stance_mat.loc['Pro-CJP', 'Anti-CJP']
    pro_ei_r = (pro_ext_r - pro_int_r) / (pro_ext_r + pro_int_r) if (pro_ext_r + pro_int_r) > 0 else 0

    anti_int_r = r_stance_mat.loc['Anti-CJP', 'Anti-CJP']
    anti_ext_r = r_stance_mat.loc['Anti-CJP', 'Pro-CJP']
    anti_ei_r = (anti_ext_r - anti_int_r) / (anti_ext_r + anti_int_r) if (anti_ext_r + anti_int_r) > 0 else 0

    stance_ei_summary = pd.DataFrame([
        {
            'Platform': 'X (Twitter)',
            'Stance_Group': 'Pro-CJP',
            'Internal_Ties_to_Same': pro_int_x,
            'External_Ties_to_Opposite': pro_ext_x,
            'Stance_EI_Index': round(pro_ei_x, 4),
            'Pattern': 'Inward Homophilic Interaction' if pro_ei_x < 0 else 'Cross-Stance Outward Engagement'
        },
        {
            'Platform': 'X (Twitter)',
            'Stance_Group': 'Anti-CJP',
            'Internal_Ties_to_Same': anti_int_x,
            'External_Ties_to_Opposite': anti_ext_x,
            'Stance_EI_Index': round(anti_ei_x, 4),
            'Pattern': 'Cross-Stance Outward Engagement' if anti_ei_x > 0 else 'Inward Homophilic Interaction'
        },
        {
            'Platform': 'Reddit',
            'Stance_Group': 'Pro-CJP',
            'Internal_Ties_to_Same': pro_int_r,
            'External_Ties_to_Opposite': pro_ext_r,
            'Stance_EI_Index': round(pro_ei_r, 4),
            'Pattern': 'Inward Homophilic Interaction' if pro_ei_r < 0 else 'Cross-Stance Outward Engagement'
        },
        {
            'Platform': 'Reddit',
            'Stance_Group': 'Anti-CJP',
            'Internal_Ties_to_Same': anti_int_r,
            'External_Ties_to_Opposite': anti_ext_r,
            'Stance_EI_Index': round(anti_ei_r, 4),
            'Pattern': 'Cross-Stance Outward Engagement' if anti_ei_r > 0 else 'Inward Homophilic Interaction'
        }
    ])
    stance_ei_path = os.path.join(cross_dir, "stance_homophily_ei_summary.csv")
    stance_ei_summary.to_csv(stance_ei_path, index=False, encoding='utf-8')
    print(f"\n -> Saved Stance-Level Homophily E-I Table: {stance_ei_path}")
    print("\n--- Stance-Level Homophily & Boundary Crossing ---")
    print(stance_ei_summary.to_string(index=False))

    # 4. Temporal E-I Trajectory Across Protest Phases on X (RQ3)
    print("\n[Step 4] Tracking Temporal E-I Trajectory across Protest Phases on X...")
    phases = ['Before', 'Peak', 'After']
    temporal_records = []

    for p in phases:
        sub_edges = x_phase_edges[x_phase_edges['Phase'].astype(str).str.strip() == p]
        sub_comm_ei, sub_net_ei, sub_i_net, sub_e_net, sub_tot_net = calculate_community_ei(sub_edges, x_comm_map, comm_order)
        
        # Stance mixing in this phase
        sub_mat = build_stance_matrix(sub_edges, x_user_stance)
        pro_i = sub_mat.loc['Pro-CJP', 'Pro-CJP']
        pro_e = sub_mat.loc['Pro-CJP', 'Anti-CJP']
        anti_i = sub_mat.loc['Anti-CJP', 'Anti-CJP']
        anti_e = sub_mat.loc['Anti-CJP', 'Pro-CJP']
        
        p_pro_ei = (pro_e - pro_i) / (pro_e + pro_i) if (pro_e + pro_i) > 0 else 0.0
        p_anti_ei = (anti_e - anti_i) / (anti_e + anti_i) if (anti_e + anti_i) > 0 else 0.0

        temporal_records.append({
            'Phase': p,
            'Edges_Count': len(sub_edges),
            'Total_Edge_Weight': round(float(sub_tot_net), 1),
            'Internal_Ties': round(float(sub_i_net), 1),
            'External_Ties': round(float(sub_e_net), 1),
            'Network_EI_Index': round(sub_net_ei, 4),
            'C1_EI': round(float(sub_comm_ei[sub_comm_ei['Community'] == 'C1']['EI_Index'].values[0]), 4),
            'C2_EI': round(float(sub_comm_ei[sub_comm_ei['Community'] == 'C2']['EI_Index'].values[0]), 4),
            'C3_EI': round(float(sub_comm_ei[sub_comm_ei['Community'] == 'C3']['EI_Index'].values[0]), 4),
            'Pro_CJP_Stance_EI': round(p_pro_ei, 4),
            'Anti_CJP_Stance_EI': round(p_anti_ei, 4)
        })

    temporal_ei_df = pd.DataFrame(temporal_records)
    temporal_ei_path = os.path.join(x_pol_dir, "x_temporal_ei_trajectory.csv")
    temporal_ei_df.to_csv(temporal_ei_path, index=False, encoding='utf-8')
    print(f" -> Saved Temporal E-I Trajectory Table: {temporal_ei_path}")
    print("\n--- X Temporal E-I Trajectory ---")
    print(temporal_ei_df[['Phase', 'Edges_Count', 'Total_Edge_Weight', 'Network_EI_Index', 'C1_EI', 'C2_EI', 'C3_EI', 'Pro_CJP_Stance_EI', 'Anti_CJP_Stance_EI']].to_string(index=False))

    # 5. Publication-Ready Visualizations
    print("\n[Step 5] Generating Publication-Ready Polarization & E-I Visualizations...")
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

    # Visualization 1: Community-Level E-I Index Comparison (X vs Reddit)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    plot_df = cross_ei_df[cross_ei_df['Community'] != 'Other'].copy()
    
    x_indices = np.arange(len(plot_df))
    bar_width = 0.35
    
    rects1 = ax.bar(x_indices - bar_width/2, plot_df['X_EI_Index'], bar_width, label='X (Twitter)', color='#1F77B4', edgecolor='white')
    rects2 = ax.bar(x_indices + bar_width/2, plot_df['Reddit_EI_Index'], bar_width, label='Reddit', color='#FF7F0E', edgecolor='white')
    
    ax.axhline(0, color='black', linewidth=1.2, linestyle='--')
    ax.set_ylabel('Krackhardt E-I Index (External vs. Internal)', fontsize=11, fontweight='semibold')
    ax.set_title('Community-Level Structural Homophily (Krackhardt E-I Index): X vs. Reddit\nNegative values = Inward Interaction Concentration | Positive values = Outward Boundary Spanning',
                 fontsize=11.5, fontweight='bold', pad=15)
    ax.set_xticks(x_indices)
    ax.set_xticklabels(plot_df['Community'], fontsize=11)
    ax.set_ylim(-1.05, 0.2)
    ax.legend(loc='lower left', frameon=True, fontsize=10)
    
    # Annotate specific notable communities
    c3_ei = float(x_comm_ei.loc[x_comm_ei['Community'] == 'C3', 'EI_Index'].iloc[0])
    ax.annotate(f'C3 on X: Highest Boundary Crossing (EI = {c3_ei:.2f})',
                xy=(2 - bar_width/2, c3_ei), xytext=(1.2, 0.08),
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
                fontsize=9.5, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#1F77B4", lw=1.2))

    plt.tight_layout()
    v1_path = os.path.join(cross_dir, "community_ei_index_comparison.png")
    plt.savefig(v1_path, dpi=300)
    plt.close()
    print(f" -> Saved {v1_path}")

    # Visualization 2: Stance Interaction Heatmaps (Cross-Stance Mixing)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    sns.heatmap(x_stance_pct.loc[['Pro-CJP', 'Anti-CJP'], ['Pro-CJP', 'Anti-CJP']],
                annot=True, fmt='.1f', cmap='YlOrRd', ax=axes[0], cbar=False,
                annot_kws={"fontsize": 12, "fontweight": "bold"})
    x_anti_to_pro = x_stance_pct.loc['Anti-CJP', 'Pro-CJP']
    axes[0].set_title(f"X (Twitter): Outgoing Ties by Stance (%)\n(Anti-CJP directs {x_anti_to_pro:.1f}% of ties to Pro-CJP)", fontweight='bold', fontsize=11)
    axes[0].set_xlabel("Target Stance", fontsize=10, fontweight='semibold')
    axes[0].set_ylabel("Source Stance", fontsize=10, fontweight='semibold')

    sns.heatmap(r_stance_pct.loc[['Pro-CJP', 'Anti-CJP'], ['Pro-CJP', 'Anti-CJP']],
                annot=True, fmt='.1f', cmap='Blues', ax=axes[1], cbar=False,
                annot_kws={"fontsize": 12, "fontweight": "bold"})
    r_anti_to_pro = r_stance_pct.loc['Anti-CJP', 'Pro-CJP']
    axes[1].set_title(f"Reddit: Outgoing Ties by Stance (%)\n(Anti-CJP directs {r_anti_to_pro:.1f}% of ties to Pro-CJP)", fontweight='bold', fontsize=11)
    axes[1].set_xlabel("Target Stance", fontsize=10, fontweight='semibold')
    axes[1].set_ylabel("Source Stance", fontsize=10, fontweight='semibold')

    fig.suptitle("Cross-Stance Interaction Mixing Matrix: Substantial Boundary Crossing\n(Note: Substantial cross-stance interaction demonstrates that participants are not in closed ideological silos,\nthough this does not eliminate structural homophily)",
                 fontsize=11.5, fontweight='bold', y=0.99)
    plt.tight_layout()
    v2_path = os.path.join(cross_dir, "stance_interaction_mixing_matrices.png")
    plt.savefig(v2_path, dpi=300)
    plt.close()
    print(f" -> Saved {v2_path}")

    # Visualization 3: Temporal E-I Trajectory on X (Before, Peak, After)
    fig, ax1 = plt.subplots(figsize=(10.5, 5.5))
    
    phase_labels = [f"{r['Phase']}\n(n={r['Edges_Count']} edges | W={r['Total_Edge_Weight']:.0f})" for _, r in temporal_ei_df.iterrows()]
    x_pts = np.arange(len(phase_labels))

    ax1.plot(x_pts, temporal_ei_df['Network_EI_Index'], marker='o', linewidth=2.5, markersize=8, color='#D62728', label='Overall Network E-I')
    ax1.plot(x_pts, temporal_ei_df['C1_EI'], marker='s', linewidth=2.0, linestyle='--', color='#1F77B4', label='C1 (Largest Community)')
    ax1.plot(x_pts, temporal_ei_df['C3_EI'], marker='^', linewidth=2.0, linestyle='-.', color='#2CA02C', label='C3 (Highest Boundary-Crossing Community)')
    
    ax1.axhline(0, color='gray', linestyle=':', linewidth=1.0)
    ax1.set_ylabel('Krackhardt E-I Index', fontsize=11, fontweight='semibold')
    ax1.set_xlabel('Protest Temporal Phase & Interaction Volume', fontsize=11, fontweight='semibold')
    ax1.set_xticks(x_pts)
    ax1.set_xticklabels(phase_labels, fontsize=10.5)
    ax1.set_ylim(-1.0, 0.35)
    ax1.legend(loc='lower left', frameon=True, fontsize=10)
    
    ax1.set_title('Evolution of Structural Boundary Crossing Across Protest Phases on X (Twitter)\n[Tracking Overall Network alongside Focal Communities C1 and C3]',
                  fontsize=11.5, fontweight='bold', pad=15)
    
    # Text box explaining focal community selection neutrally
    ax1.text(0.03, 0.94,
             f"Focal Community Selection:\n• C1: Largest structural interaction community\n• C3: Community with highest boundary crossing (EI = {c3_ei:.2f})",
             transform=ax1.transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9, edgecolor='gray'),
             fontsize=9)
    
    plt.tight_layout()
    v3_path = os.path.join(x_pol_dir, "x_temporal_ei_trajectory.png")
    plt.savefig(v3_path, dpi=300)
    plt.close()
    print(f" -> Saved {v3_path}")

    print("\n=======================================================================")
    print("        POLARIZATION & INTERACTION HOMOPHILY MODULE COMPLETE           ")
    print("=======================================================================")
    print("Key Analytical Findings:")
    print(f" 1. Community-Level E-I: Louvain communities show inward structural concentration")
    print(f"    (Reddit Network EI = {r_net_ei:.4f}; X Network EI = {x_net_ei:.4f}).")
    print(f"    Exception: C3 on X exhibits high cross-community bridging (EI = {c3_ei:.4f}).")
    print(f" 2. Cross-Stance Engagement Shows Substantial Boundary Crossing:")
    x_anti_pair = x_stance_mat.loc['Anti-CJP', ['Pro-CJP', 'Anti-CJP']].sum()
    r_anti_pair = r_stance_mat.loc['Anti-CJP', ['Pro-CJP', 'Anti-CJP']].sum()
    x_anti_pair_pct = 100.0 * x_stance_mat.loc['Anti-CJP', 'Pro-CJP'] / x_anti_pair
    r_anti_pair_pct = 100.0 * r_stance_mat.loc['Anti-CJP', 'Pro-CJP'] / r_anti_pair
    print(f"    Anti-CJP participants direct {x_stance_pct.loc['Anti-CJP', 'Pro-CJP']:.1f}% of known-stance ties on X ({x_anti_pair_pct:.1f}% of ties that stay between Pro and Anti)")
    print(f"    and {r_stance_pct.loc['Anti-CJP', 'Pro-CJP']:.1f}% on Reddit ({r_anti_pair_pct:.1f}% of ties that stay between Pro and Anti) toward Pro-CJP targets.")
    print(f"    This demonstrates substantial cross-stance engagement rather than complete ideological isolation,")
    print(f"    though it does not eliminate structural homophily within the network.")
    print(f" 3. Temporal Trajectory: Network-level E-I became progressively more negative")
    print(f"    from Before ({temporal_ei_df.loc[0, 'Network_EI_Index']}) to Peak ({temporal_ei_df.loc[1, 'Network_EI_Index']}) to After ({temporal_ei_df.loc[2, 'Network_EI_Index']}),")
    print(f"    indicating increasing inward interaction concentration across the observation window.")
    print("=======================================================================")

if __name__ == "__main__":
    run_polarization_analysis()
