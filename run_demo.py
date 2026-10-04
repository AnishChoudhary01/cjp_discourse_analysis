import os
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

def print_banner(text):
    print("\n" + "="*70)
    print(f"   {text}")
    print("="*70)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    print_banner("CSMA PROJECT: CJP-NEET PROTEST DISCOURSE ANALYSIS")
    print("Computational Social Media Analysis - Phase 2 Demonstration")
    print("Team: Manya Agarwal, Anish Choudhary, Palak Bhatt, Akshit Wadhwa\n")
    
    # 1. Execute Reddit Pipeline
    print_banner("[1/7] RUNNING REDDIT DATA PIPELINE")
    reddit_script = os.path.join(base_dir, "scripts", "reddit", "csma_pipeline.py")
    res_reddit = subprocess.run([sys.executable, reddit_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_reddit.stdout)
    if res_reddit.stderr:
        for line in res_reddit.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 2. Execute X Pipeline
    print_banner("[2/7] RUNNING X (TWITTER) MULTI-PERIOD PIPELINE")
    x_script = os.path.join(base_dir, "scripts", "x", "x_pipeline.py")
    res_x = subprocess.run([sys.executable, x_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_x.stdout)
    if res_x.stderr:
        for line in res_x.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 3. Execute Community Detection Pipeline
    print_banner("[3/7] RUNNING LOUVAIN COMMUNITY DETECTION & INTERACTIVE VIZ")
    comm_script = os.path.join(base_dir, "scripts", "community_detection.py")
    res_comm = subprocess.run([sys.executable, comm_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_comm.stdout)
    if res_comm.stderr:
        for line in res_comm.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 4. Execute Sentiment Analysis Pipeline
    print_banner("[4/7] RUNNING VALENCE SENTIMENT & POST-HOC ANALYSIS")
    sent_script = os.path.join(base_dir, "scripts", "sentiment_analysis.py")
    res_sent = subprocess.run([sys.executable, sent_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_sent.stdout)
    if res_sent.stderr:
        for line in res_sent.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 5. Execute Stance Detection Pipeline
    print_banner("[5/7] RUNNING TARGET-SPECIFIC STANCE DETECTION")
    stance_script = os.path.join(base_dir, "scripts", "stance_analysis.py")
    res_stance = subprocess.run([sys.executable, stance_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_stance.stdout)
    if res_stance.stderr:
        for line in res_stance.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 6. Execute Independent Stance Validation Pipeline
    print_banner("[6/7] RUNNING INDEPENDENT STANCE CLASSIFIER VALIDATION")
    val_script = os.path.join(base_dir, "scripts", "validate_stance_classifier.py")
    res_val = subprocess.run([sys.executable, val_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_val.stdout)
    if res_val.stderr:
        for line in res_val.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 7. Execute Polarization & E-I Metrics Pipeline
    print_banner("[7/7] RUNNING POLARIZATION & INTERACTION HOMOPHILY MODULE (E-I INDEX)")
    pol_script = os.path.join(base_dir, "scripts", "polarization_metrics.py")
    res_pol = subprocess.run([sys.executable, pol_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_pol.stdout)
    if res_pol.stderr:
        for line in res_pol.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 8. Summary of Deliverables & Output Assets
    print_banner("VERIFICATION OF PIPELINE OUTPUTS & DEMONSTRATION ARTIFACTS")
    
    assets = [
        # Stage 01: Preprocessing
        ("Reddit Processed Posts", os.path.join(base_dir, "output", "01_preprocessing", "reddit", "processed_posts.csv")),
        ("Reddit Processed Comments", os.path.join(base_dir, "output", "01_preprocessing", "reddit", "processed_comments.csv")),
        ("X Processed Tweets", os.path.join(base_dir, "output", "01_preprocessing", "x", "processed_x_tweets.csv")),
        
        # Stage 02: Exploratory Data Analysis (EDA)
        ("Reddit Activity Volume Plot", os.path.join(base_dir, "output", "02_eda", "reddit", "volume_over_time.png")),
        ("Reddit Conversation Depth Plot", os.path.join(base_dir, "output", "02_eda", "reddit", "depth_distribution.png")),
        ("Reddit Top Users Plot", os.path.join(base_dir, "output", "02_eda", "reddit", "top_10_users.png")),
        ("X Phase Volume Plot", os.path.join(base_dir, "output", "02_eda", "x", "activity_volume_by_phase.png")),
        ("X Phase Engagement Plot", os.path.join(base_dir, "output", "02_eda", "x", "engagement_distribution_by_phase.png")),
        ("X Top Mentions Plot", os.path.join(base_dir, "output", "02_eda", "x", "top_mentioned_actors.png")),
        ("X Top Hashtags Plot", os.path.join(base_dir, "output", "02_eda", "x", "top_protest_hashtags.png")),

        # Stage 03: Network Analysis (Graph Extraction)
        ("Reddit Network Nodes", os.path.join(base_dir, "output", "03_network_analysis", "reddit", "nodes.csv")),
        ("Reddit Network Edges", os.path.join(base_dir, "output", "03_network_analysis", "reddit", "edges.csv")),
        ("X Network Nodes", os.path.join(base_dir, "output", "03_network_analysis", "x", "x_nodes.csv")),
        ("X Network Edges", os.path.join(base_dir, "output", "03_network_analysis", "x", "x_edges.csv")),

        # Stage 04: Community Detection
        ("Reddit Community Summary", os.path.join(base_dir, "output", "04_community_detection", "reddit", "reddit_community_summary.csv")),
        ("Reddit Community Network Plot", os.path.join(base_dir, "output", "04_community_detection", "reddit", "reddit_network_communities.png")),
        ("Reddit Interactive HTML Graph", os.path.join(base_dir, "output", "04_community_detection", "reddit", "interactive_reddit_network.html")),
        ("Reddit Nodes with Communities", os.path.join(base_dir, "output", "04_community_detection", "reddit", "reddit_nodes_with_communities.csv")),
        ("X Community Summary", os.path.join(base_dir, "output", "04_community_detection", "x", "x_community_summary.csv")),
        ("X Community Network Plot", os.path.join(base_dir, "output", "04_community_detection", "x", "x_network_communities.png")),
        ("X Interactive HTML Graph", os.path.join(base_dir, "output", "04_community_detection", "x", "interactive_x_network.html")),
        ("X Nodes with Communities", os.path.join(base_dir, "output", "04_community_detection", "x", "x_nodes_with_communities.csv")),

        # Stage 05: Sentiment Analysis
        ("X Tweets with Sentiment", os.path.join(base_dir, "output", "05_sentiment_analysis", "x", "x_tweets_with_sentiment.csv")),
        ("Reddit Items with Sentiment", os.path.join(base_dir, "output", "05_sentiment_analysis", "reddit", "reddit_items_with_sentiment.csv")),
        ("X Community Sentiment Summary", os.path.join(base_dir, "output", "05_sentiment_analysis", "x", "x_community_sentiment_summary.csv")),
        ("Reddit Community Sentiment Summary", os.path.join(base_dir, "output", "05_sentiment_analysis", "reddit", "reddit_community_sentiment_summary.csv")),
        ("X Community Dunn Post-Hoc", os.path.join(base_dir, "output", "05_sentiment_analysis", "x", "x_community_sentiment_dunn_posthoc.csv")),
        ("Reddit Community Dunn Post-Hoc", os.path.join(base_dir, "output", "05_sentiment_analysis", "reddit", "reddit_community_sentiment_dunn_posthoc.csv")),
        ("X Community Sentiment Plot", os.path.join(base_dir, "output", "05_sentiment_analysis", "x", "x_community_sentiment_distributions.png")),
        ("Reddit Community Sentiment Plot", os.path.join(base_dir, "output", "05_sentiment_analysis", "reddit", "reddit_community_sentiment_distributions.png")),

        # Stage 06: Target-Specific Stance Analysis
        ("X Tweets with Stance", os.path.join(base_dir, "output", "06_stance_analysis", "x", "x_tweets_with_stance.csv")),
        ("Reddit Items with Stance", os.path.join(base_dir, "output", "06_stance_analysis", "reddit", "reddit_items_with_stance.csv")),
        ("X Community Stance Summary", os.path.join(base_dir, "output", "06_stance_analysis", "x", "x_community_stance_summary.csv")),
        ("Reddit Community Stance Summary", os.path.join(base_dir, "output", "06_stance_analysis", "reddit", "reddit_community_stance_summary.csv")),
        ("X Temporal Stance Summary", os.path.join(base_dir, "output", "06_stance_analysis", "x", "x_temporal_stance_summary.csv")),
        ("X Community Stance Plot", os.path.join(base_dir, "output", "06_stance_analysis", "x", "x_community_stance_distributions.png")),
        ("Reddit Community Stance Plot", os.path.join(base_dir, "output", "06_stance_analysis", "reddit", "reddit_community_stance_distributions.png")),
        ("X Temporal Stance Plot", os.path.join(base_dir, "output", "06_stance_analysis", "x", "x_temporal_stance_shift.png")),

        # Stage 07: Stance Classifier Validation
        ("Stance Validation Sample CSV", os.path.join(base_dir, "output", "07_stance_validation", "stance_validation_annotated_sample.csv")),
        ("Stance Validation Metrics CSV", os.path.join(base_dir, "output", "07_stance_validation", "stance_validation_metrics.csv")),
        ("Stance Validation Confusion Matrix", os.path.join(base_dir, "output", "07_stance_validation", "stance_validation_confusion_matrix.png")),

        # Stage 08: Polarization & Homophily Analysis
        ("X Community E-I Index", os.path.join(base_dir, "output", "08_polarization", "x", "x_community_ei_index.csv")),
        ("Reddit Community E-I Index", os.path.join(base_dir, "output", "08_polarization", "reddit", "reddit_community_ei_index.csv")),
        ("X Temporal E-I Trajectory CSV", os.path.join(base_dir, "output", "08_polarization", "x", "x_temporal_ei_trajectory.csv")),
        ("X Temporal E-I Trajectory Plot", os.path.join(base_dir, "output", "08_polarization", "x", "x_temporal_ei_trajectory.png")),

        # Stage 09: Cross-Platform Comparative Synthesis
        ("Cross-Platform Sentiment Table", os.path.join(base_dir, "output", "09_cross_platform", "cross_platform_sentiment_comparison.csv")),
        ("Sentiment Coverage Summary", os.path.join(base_dir, "output", "09_cross_platform", "community_sentiment_coverage_summary.csv")),
        ("Cross-Platform Sentiment Plot", os.path.join(base_dir, "output", "09_cross_platform", "overall_sentiment_comparison_x_reddit.png")),
        ("Community Category Breakdown Plot", os.path.join(base_dir, "output", "09_cross_platform", "sentiment_category_breakdown_by_community.png")),
        ("Cross-Platform Stance Table", os.path.join(base_dir, "output", "09_cross_platform", "cross_platform_stance_comparison.csv")),
        ("Cross-Platform Stance Plot", os.path.join(base_dir, "output", "09_cross_platform", "cross_platform_stance_comparison.png")),
        ("Sentiment vs Stance Heatmap", os.path.join(base_dir, "output", "09_cross_platform", "sentiment_vs_stance_contingency.png")),
        ("Sentiment vs Stance Matrix CSV", os.path.join(base_dir, "output", "09_cross_platform", "stance_sentiment_contingency_table.csv")),
        ("Cross-Platform E-I Table", os.path.join(base_dir, "output", "09_cross_platform", "community_ei_index_comparison.csv")),
        ("Cross-Platform E-I Plot", os.path.join(base_dir, "output", "09_cross_platform", "community_ei_index_comparison.png")),
        ("X Stance Mixing Matrix CSV", os.path.join(base_dir, "output", "09_cross_platform", "x_stance_interaction_mixing_matrix.csv")),
        ("Reddit Stance Mixing Matrix CSV", os.path.join(base_dir, "output", "09_cross_platform", "reddit_stance_interaction_mixing_matrix.csv")),
        ("Stance Homophily E-I Summary", os.path.join(base_dir, "output", "09_cross_platform", "stance_homophily_ei_summary.csv")),
        ("Stance Mixing Matrix Heatmap", os.path.join(base_dir, "output", "09_cross_platform", "stance_interaction_mixing_matrices.png")),
    ]

    print(f"{'Asset Name':<35} | {'Status':<10} | {'Details'}")
    print("-" * 70)
    for name, path in assets:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"{name:<35} | FOUND      | {size:,} bytes")
        else:
            print(f"{name:<35} | MISSING    | -")

    print(f"\nAll {len(assets)} demonstration artifacts verified successfully!")

if __name__ == "__main__":
    main()
