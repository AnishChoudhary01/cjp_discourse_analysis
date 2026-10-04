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
    print_banner("[1/6] RUNNING REDDIT DATA PIPELINE")
    reddit_script = os.path.join(base_dir, "scripts", "reddit", "csma_pipeline.py")
    res_reddit = subprocess.run([sys.executable, reddit_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_reddit.stdout)
    if res_reddit.stderr:
        for line in res_reddit.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 2. Execute X Pipeline
    print_banner("[2/6] RUNNING X (TWITTER) MULTI-PERIOD PIPELINE")
    x_script = os.path.join(base_dir, "scripts", "x", "x_pipeline.py")
    res_x = subprocess.run([sys.executable, x_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_x.stdout)
    if res_x.stderr:
        for line in res_x.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 3. Execute Community Detection Pipeline
    print_banner("[3/6] RUNNING LOUVAIN COMMUNITY DETECTION & INTERACTIVE VIZ")
    comm_script = os.path.join(base_dir, "scripts", "community_detection.py")
    res_comm = subprocess.run([sys.executable, comm_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_comm.stdout)
    if res_comm.stderr:
        for line in res_comm.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 4. Execute Sentiment Analysis Pipeline
    print_banner("[4/6] RUNNING VALENCE SENTIMENT & POST-HOC ANALYSIS")
    sent_script = os.path.join(base_dir, "scripts", "sentiment_analysis.py")
    res_sent = subprocess.run([sys.executable, sent_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_sent.stdout)
    if res_sent.stderr:
        for line in res_sent.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 5. Execute Stance Detection Pipeline
    print_banner("[5/6] RUNNING TARGET-SPECIFIC STANCE DETECTION")
    stance_script = os.path.join(base_dir, "scripts", "stance_analysis.py")
    res_stance = subprocess.run([sys.executable, stance_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_stance.stdout)
    if res_stance.stderr:
        for line in res_stance.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 6. Execute Independent Stance Validation Pipeline
    print_banner("[6/6] RUNNING INDEPENDENT STANCE CLASSIFIER VALIDATION")
    val_script = os.path.join(base_dir, "scripts", "validate_stance_classifier.py")
    res_val = subprocess.run([sys.executable, val_script], cwd=base_dir, capture_output=True, text=True, encoding='utf-8')
    print(res_val.stdout)
    if res_val.stderr:
        for line in res_val.stderr.splitlines():
            if "FutureWarning" not in line and "deprecated" not in line:
                print("  ", line)

    # 7. Summary of Deliverables & Output Assets
    print_banner("VERIFICATION OF PIPELINE OUTPUTS & DEMONSTRATION ARTIFACTS")
    
    assets = [
        ("Reddit Processed Posts", os.path.join(base_dir, "output", "reddit", "processed_data", "processed_posts.csv")),
        ("Reddit Processed Comments", os.path.join(base_dir, "output", "reddit", "processed_data", "processed_comments.csv")),
        ("Reddit Network Nodes", os.path.join(base_dir, "output", "reddit", "network", "nodes.csv")),
        ("Reddit Network Edges", os.path.join(base_dir, "output", "reddit", "network", "edges.csv")),
        ("Reddit Activity Volume Plot", os.path.join(base_dir, "output", "reddit", "visualizations", "volume_over_time.png")),
        ("Reddit Conversation Depth Plot", os.path.join(base_dir, "output", "reddit", "visualizations", "depth_distribution.png")),
        ("Reddit Top Users Plot", os.path.join(base_dir, "output", "reddit", "visualizations", "top_10_users.png")),
        ("Reddit Community Summary", os.path.join(base_dir, "output", "reddit", "network", "reddit_community_summary.csv")),
        ("Reddit Community Network Plot", os.path.join(base_dir, "output", "reddit", "visualizations", "reddit_network_communities.png")),
        ("Reddit Interactive HTML Graph", os.path.join(base_dir, "output", "reddit", "visualizations", "interactive_reddit_network.html")),
        ("Reddit Community Sentiment Summary", os.path.join(base_dir, "output", "reddit", "network", "reddit_community_sentiment_summary.csv")),
        ("Reddit Community Sentiment Plot", os.path.join(base_dir, "output", "reddit", "visualizations", "reddit_community_sentiment_distributions.png")),
        ("X Processed Tweets", os.path.join(base_dir, "output", "x", "processed_data", "processed_x_tweets.csv")),
        ("X Network Nodes", os.path.join(base_dir, "output", "x", "network", "x_nodes.csv")),
        ("X Network Edges", os.path.join(base_dir, "output", "x", "network", "x_edges.csv")),
        ("X Phase Volume Plot", os.path.join(base_dir, "output", "x", "visualizations", "activity_volume_by_phase.png")),
        ("X Phase Engagement Plot", os.path.join(base_dir, "output", "x", "visualizations", "engagement_distribution_by_phase.png")),
        ("X Top Mentions Plot", os.path.join(base_dir, "output", "x", "visualizations", "top_mentioned_actors.png")),
        ("X Top Hashtags Plot", os.path.join(base_dir, "output", "x", "visualizations", "top_protest_hashtags.png")),
        ("X Community Summary", os.path.join(base_dir, "output", "x", "network", "x_community_summary.csv")),
        ("X Community Network Plot", os.path.join(base_dir, "output", "x", "visualizations", "x_network_communities.png")),
        ("X Interactive HTML Graph", os.path.join(base_dir, "output", "x", "visualizations", "interactive_x_network.html")),
        ("X Community Sentiment Summary", os.path.join(base_dir, "output", "x", "network", "x_community_sentiment_summary.csv")),
        ("X Community Sentiment Plot", os.path.join(base_dir, "output", "x", "visualizations", "x_community_sentiment_distributions.png")),
        ("Cross-Platform Sentiment Table", os.path.join(base_dir, "output", "cross_platform", "cross_platform_sentiment_comparison.csv")),
        ("Sentiment Coverage Summary", os.path.join(base_dir, "output", "cross_platform", "community_sentiment_coverage_summary.csv")),
        ("Cross-Platform Sentiment Plot", os.path.join(base_dir, "output", "cross_platform", "overall_sentiment_comparison_x_reddit.png")),
        ("Community Category Breakdown Plot", os.path.join(base_dir, "output", "cross_platform", "sentiment_category_breakdown_by_community.png")),
        ("X Community Dunn Post-Hoc", os.path.join(base_dir, "output", "x", "network", "x_community_sentiment_dunn_posthoc.csv")),
        ("Reddit Community Dunn Post-Hoc", os.path.join(base_dir, "output", "reddit", "network", "reddit_community_sentiment_dunn_posthoc.csv")),
        ("X Tweets with Stance", os.path.join(base_dir, "output", "x", "processed_data", "x_tweets_with_stance.csv")),
        ("Reddit Items with Stance", os.path.join(base_dir, "output", "reddit", "processed_data", "reddit_items_with_stance.csv")),
        ("Cross-Platform Stance Table", os.path.join(base_dir, "output", "cross_platform", "cross_platform_stance_comparison.csv")),
        ("Cross-Platform Stance Plot", os.path.join(base_dir, "output", "cross_platform", "cross_platform_stance_comparison.png")),
        ("Sentiment vs Stance Heatmap", os.path.join(base_dir, "output", "cross_platform", "sentiment_vs_stance_contingency.png")),
        ("Sentiment vs Stance Matrix CSV", os.path.join(base_dir, "output", "cross_platform", "stance_sentiment_contingency_table.csv")),
        ("X Community Stance Summary", os.path.join(base_dir, "output", "x", "network", "x_community_stance_summary.csv")),
        ("X Community Stance Plot", os.path.join(base_dir, "output", "x", "visualizations", "x_community_stance_distributions.png")),
        ("Reddit Community Stance Summary", os.path.join(base_dir, "output", "reddit", "network", "reddit_community_stance_summary.csv")),
        ("Reddit Community Stance Plot", os.path.join(base_dir, "output", "reddit", "visualizations", "reddit_community_stance_distributions.png")),
        ("X Temporal Stance Summary", os.path.join(base_dir, "output", "x", "network", "x_temporal_stance_summary.csv")),
        ("X Temporal Stance Plot", os.path.join(base_dir, "output", "x", "visualizations", "x_temporal_stance_shift.png")),
        ("Stance Validation Sample CSV", os.path.join(base_dir, "output", "validation", "stance_validation_annotated_sample.csv")),
        ("Stance Validation Metrics CSV", os.path.join(base_dir, "output", "validation", "stance_validation_metrics.csv")),
        ("Stance Validation Confusion Matrix", os.path.join(base_dir, "output", "validation", "stance_validation_confusion_matrix.png")),
    ]

    print(f"{'Asset Name':<35} | {'Status':<10} | {'Details'}")
    print("-" * 70)
    for name, path in assets:
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"{name:<35} | FOUND      | {size:,} bytes")
        else:
            print(f"{name:<35} | MISSING    | -")

    print("\nDemonstration completed successfully!")

if __name__ == "__main__":
    main()
