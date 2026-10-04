import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def main():
    base_dir = r"c:\Users\Palak\Documents\csma_prj"
    dataset_dir = os.path.join(base_dir, "dataset", "reddit_datasets")
    if not os.path.exists(dataset_dir):
        dataset_dir = os.path.join(base_dir, "dataset")

    out_processed = os.path.join(base_dir, "output", "reddit", "processed_data")
    out_viz = os.path.join(base_dir, "output", "reddit", "visualizations")
    out_network = os.path.join(base_dir, "output", "reddit", "network")

    os.makedirs(out_processed, exist_ok=True)
    os.makedirs(out_viz, exist_ok=True)
    os.makedirs(out_network, exist_ok=True)
    
    print("=== Phase 1: Preprocessing ===")
    # Load raw data
    posts = pd.read_csv(os.path.join(dataset_dir, "targeted_posts.csv"))
    comments = pd.read_csv(os.path.join(dataset_dir, "targeted_comments.csv"))
    
    # 1. Filter Bot and Deleted accounts
    ignore_authors = ['[deleted]', '[removed]', 'AutoModerator']
    posts_clean = posts[~posts['author'].isin(ignore_authors)].copy()
    comments_clean = comments[~comments['author'].isin(ignore_authors)].copy()
    
    print(f"Filtered Posts: {len(posts)} -> {len(posts_clean)}")
    print(f"Filtered Comments: {len(comments)} -> {len(comments_clean)}")
    
    # 2. Handle missing text
    posts_clean['selftext'] = posts_clean['selftext'].fillna("")
    posts_clean['flair'] = posts_clean['flair'].fillna("")
    
    # 3. Datetime conversion
    posts_clean['created_utc'] = pd.to_datetime(posts_clean['created_utc'], errors='coerce')
    comments_clean['created_utc'] = pd.to_datetime(comments_clean['created_utc'], errors='coerce')
    
    # Temporal features
    posts_clean['date'] = posts_clean['created_utc'].dt.date
    comments_clean['date'] = comments_clean['created_utc'].dt.date
    
    # Save processed data
    posts_clean.to_csv(os.path.join(out_processed, "processed_posts.csv"), index=False)
    comments_clean.to_csv(os.path.join(out_processed, "processed_comments.csv"), index=False)
    
    print("\n=== Phase 2: Minimal EDA ===")
    sns.set_theme(style="whitegrid")
    
    # 1. Volume Over Time
    posts_vol = posts_clean.groupby('date').size().reset_index(name='Posts')
    comments_vol = comments_clean.groupby('date').size().reset_index(name='Comments')
    
    # Merge and handle missing dates if any
    vol_df = pd.merge(posts_vol, comments_vol, on='date', how='outer').fillna(0).sort_values('date')
    
    plt.figure(figsize=(10, 5))
    plt.plot(vol_df['date'], vol_df['Posts'], marker='o', label='Posts')
    plt.plot(vol_df['date'], vol_df['Comments'], marker='s', label='Comments')
    plt.title('Daily Activity Volume')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_viz, "volume_over_time.png"))
    plt.close()
    
    # 2. Conversation Depth
    plt.figure(figsize=(8, 5))
    sns.histplot(data=comments_clean, x='depth', discrete=True)
    plt.title('Conversation Depth Distribution')
    plt.xlabel('Depth (0 = Direct Reply to Post)')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.savefig(os.path.join(out_viz, "depth_distribution.png"))
    plt.close()
    
    # 3. Top 10 Most Active Users
    user_counts = pd.concat([posts_clean['author'], comments_clean['author']]).value_counts().head(10)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=user_counts.values, y=user_counts.index, palette="viridis")
    plt.title('Top 10 Most Active Users')
    plt.xlabel('Total Interactions (Posts + Comments)')
    plt.ylabel('User')
    plt.tight_layout()
    plt.savefig(os.path.join(out_viz, "top_10_users.png"))
    plt.close()
    
    print("EDA Visualizations saved.")
    
    print("\n=== Phase 3: Network Construction ===")
    # Create the User-User directed network
    # For post replies (parent_type == post), target is Post Author
    # For comment replies (parent_type == comment), target is parent_author
    
    edges_list = []
    
    # Pre-map post_id -> post author for fast lookup
    post_author_map = dict(zip(posts_clean['post_id'], posts_clean['author']))
    
    for _, row in comments_clean.iterrows():
        source = row['author']
        
        # Determine target
        if row['parent_type'] == 'post':
            # Target is post author
            target = post_author_map.get(row['parent_id'])
        elif row['parent_type'] == 'comment':
            # Target is parent comment author
            target = row['parent_author']
        else:
            target = None
            
        if pd.notna(target) and target not in ignore_authors:
            edges_list.append((source, target))
            
    # Aggregate edge weights
    edge_df = pd.DataFrame(edges_list, columns=['Source', 'Target'])
    # Remove self-loops if you only want social interactions, but Gephi handles it.
    edge_df = edge_df[edge_df['Source'] != edge_df['Target']]
    
    edges_agg = edge_df.groupby(['Source', 'Target']).size().reset_index(name='Weight')
    edges_agg['Type'] = 'Directed'
    
    # Create Nodes list
    all_users = set(edges_agg['Source']).union(set(edges_agg['Target']))
    nodes_df = pd.DataFrame({'Id': list(all_users), 'Label': list(all_users)})
    
    # Export for Gephi
    nodes_df.to_csv(os.path.join(out_network, "nodes.csv"), index=False)
    edges_agg.to_csv(os.path.join(out_network, "edges.csv"), index=False)
    
    print(f"Network extracted: {len(nodes_df)} nodes, {len(edges_agg)} edges.")
    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
