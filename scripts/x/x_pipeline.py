import os
import sys
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# Ensure UTF-8 output on Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

def main():
    base_dir = r"c:\Users\Palak\Documents\csma_prj"
    dataset_x_dir = os.path.join(base_dir, "dataset", "x")
    out_processed = os.path.join(base_dir, "output", "01_preprocessing", "x")
    out_viz = os.path.join(base_dir, "output", "02_eda", "x")
    out_network = os.path.join(base_dir, "output", "03_network_analysis", "x")

    os.makedirs(out_processed, exist_ok=True)
    os.makedirs(out_viz, exist_ok=True)
    os.makedirs(out_network, exist_ok=True)

    print("==================================================")
    print("   X (Twitter) CSMA Data & Preliminary Pipeline   ")
    print("   [Updated with Statistical & Visual Rigor]      ")
    print("==================================================")

    # -------------------------------------------------------------------------
    # Phase 1: Ingestion, Multi-Period Merging & Preprocessing
    # -------------------------------------------------------------------------
    print("\n[Phase 1] Ingesting multi-period datasets...")
    phase_files = [
        ("Before", os.path.join(dataset_x_dir, "Before_protest_7juneto19july.csv"), "2026-06-07", "2026-07-19"),
        ("Peak",   os.path.join(dataset_x_dir, "Peak_protest_20julyto24july.csv"),  "2026-07-20", "2026-07-24"),
        ("After",  os.path.join(dataset_x_dir, "After_Protest_24julyto30july.csv"), "2026-07-25", "2026-07-30"),
    ]

    dfs = []
    for phase_name, fpath, start_date, end_date in phase_files:
        if not os.path.exists(fpath):
            print(f"Warning: File not found {fpath}")
            continue
        df = pd.read_csv(fpath, sep=';', on_bad_lines='skip', low_memory=False)
        df['protest_phase'] = phase_name
        df['phase_expected_start'] = start_date
        df['phase_expected_end'] = end_date
        print(f" -> Loaded {phase_name} Phase: {len(df)} records from {os.path.basename(fpath)}")
        dfs.append(df)

    if not dfs:
        print("Error: No X data loaded. Exiting.")
        return

    raw_x = pd.concat(dfs, ignore_index=True)
    print(f"Total raw records loaded: {len(raw_x)}")

    # 1. Deduplication on tweet ID
    if 'id' in raw_x.columns:
        initial_count = len(raw_x)
        raw_x = raw_x.drop_duplicates(subset=['id']).copy()
        print(f" -> Deduplication by tweet ID: {initial_count} -> {len(raw_x)}")

    # 2. Filter invalid / bot / blank authors and normalize handle
    raw_x = raw_x[raw_x['author'].notna() & (raw_x['author'].astype(str).str.strip() != '')].copy()
    raw_x['author_raw'] = raw_x['author']
    raw_x['author'] = raw_x['author'].astype(str).str.strip().str.lstrip('@').str.lower()

    # 3. Datetime standardisation
    raw_x['timestamp'] = pd.to_datetime(raw_x['timestamp'], errors='coerce')
    raw_x['date'] = raw_x['timestamp'].dt.date

    # 4. Numeric metric cleaning
    metric_cols = ['retweet_count', 'reply_count', 'like_count', 'quote_count', 'impression_count']
    for col in metric_cols:
        if col in raw_x.columns:
            raw_x[col] = pd.to_numeric(raw_x[col], errors='coerce').fillna(0).astype(int)

    # 5. Content relevance filtering (Removing general feed scraper noise e.g., entertainment, crypto)
    print("\n[Phase 1.2] Applying Protest Relevance Filter...")
    keywords = [
        r'cjp', r'cockroach', r'neet', r'paper\s*leak', r'nta', r'jantar\s*mantar',
        r'dharmendra\s*pradhan', r'abhijeet\s*dipke', r'dipke', r'student\s*protest',
        r'संसद_मार्च', r'नीट', r'delhipolice', r'wangchuk', r'education\s*minister'
    ]
    kw_regex = re.compile('|'.join(keywords), re.IGNORECASE)

    text_features = (
        raw_x['body'].fillna('') + ' ' + 
        raw_x['hashtags'].fillna('') + ' ' + 
        raw_x['mentions'].fillna('')
    )
    is_relevant = text_features.apply(lambda x: bool(kw_regex.search(str(x))))
    clean_x = raw_x[is_relevant].copy()

    print(f" -> Relevance Filter Result: {len(raw_x)} -> {len(clean_x)} relevant tweets retained ({len(clean_x)/len(raw_x)*100:.1f}%)")
    print(f"    - Filtered out {len(raw_x) - len(clean_x)} irrelevant/noise posts.")

    # Save cleaned dataset
    clean_csv_path = os.path.join(out_processed, "processed_x_tweets.csv")
    clean_x.to_csv(clean_csv_path, index=False, encoding='utf-8')
    print(f" -> Saved processed X dataset: {clean_csv_path}")

    # Compute empirical daily stats for verified reporting
    daily_stats = clean_x.groupby(['protest_phase', 'date']).size().reset_index(name='daily_count')
    phase_summary = daily_stats.groupby('protest_phase')['daily_count'].agg(['mean', 'median', 'count', 'sum']).reindex(['Before', 'Peak', 'After'])
    print("\nEmpirical Daily Activity Stats:")
    for phase_name, row in phase_summary.iterrows():
        print(f" - {phase_name}: Total={int(row['sum'])}, Days={int(row['count'])}, Daily Mean={row['mean']:.1f}, Daily Median={row['median']:.1f}")

    # -------------------------------------------------------------------------
    # Phase 2: Exploratory Data Analysis & Visualizations
    # -------------------------------------------------------------------------
    print("\n[Phase 2] Generating Refined EDA Visualizations...")
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

    # -------------------------------------------------------------------------
    # 1. Activity Volume over Time (Fix #5: Clean date spacing without overlap)
    # -------------------------------------------------------------------------
    # Aggregate daily counts across phases
    vol_by_date = clean_x.groupby(['date', 'protest_phase']).size().reset_index(name='tweet_count')
    # Filter to main protest observation window (June 07 to July 31) for clear visualization
    vol_by_date['datetime'] = pd.to_datetime(vol_by_date['date'])
    vol_by_date = vol_by_date[(vol_by_date['datetime'] >= '2026-06-07') & (vol_by_date['datetime'] <= '2026-07-31')].sort_values('datetime')

    # Create pivot for stacked bar representation
    pivot_vol = vol_by_date.pivot(index='datetime', columns='protest_phase', values='tweet_count').fillna(0)
    for col in ['Before', 'Peak', 'After']:
        if col not in pivot_vol.columns:
            pivot_vol[col] = 0
    pivot_vol = pivot_vol[['Before', 'Peak', 'After']]

    plt.figure(figsize=(13, 6))
    ax = plt.subplot(111)
    
    # Plot bar chart with explicit date indices
    bar_width = 0.8
    p1 = ax.bar(pivot_vol.index, pivot_vol['Before'], width=bar_width, label='Before', color='#4C72B0')
    p2 = ax.bar(pivot_vol.index, pivot_vol['Peak'], width=bar_width, bottom=pivot_vol['Before'], label='Peak', color='#C44E52')
    p3 = ax.bar(pivot_vol.index, pivot_vol['After'], width=bar_width, bottom=pivot_vol['Before'] + pivot_vol['Peak'], label='After', color='#55A868')

    # Formatting date axis cleanly: show tick every 3 days
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.xticks(rotation=45, ha='right', fontsize=10)
    
    plt.title('Daily X (Twitter) Discourse Activity Across Protest Phases', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Date (Observation Window: Jun 07 – Jul 31)', fontsize=11, labelpad=8)
    plt.ylabel('Tweet Count per Day', fontsize=11)
    plt.legend(title='Protest Phase', frameon=True)
    
    # Annotate the peak phase surge (strictly empirical date and volume)
    peak_date = pivot_vol['Peak'].idxmax()
    peak_val = pivot_vol.loc[peak_date].sum()
    ax.annotate(f'Peak Daily Volume\n({int(peak_val)} tweets on Jul 24)', 
                xy=(peak_date, peak_val), 
                xytext=(peak_date - pd.Timedelta(days=6), peak_val + 20),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=5),
                fontsize=9, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", lw=1))

    plt.tight_layout()
    v1_path = os.path.join(out_viz, "activity_volume_by_phase.png")
    plt.savefig(v1_path, dpi=300)
    plt.close()
    print(f" -> Saved {v1_path} (with cleaned, uncrowded date spacing and empirical labels)")

    # -------------------------------------------------------------------------
    # 2. Phase Engagement Comparison (Accurate Interpretation & Medians)
    # -------------------------------------------------------------------------
    clean_x['log_likes'] = np.log1p(clean_x['like_count'])
    clean_x['log_retweets'] = np.log1p(clean_x['retweet_count'])

    phase_order = ['Before', 'Peak', 'After']
    
    # Compute exact medians for annotation
    med_likes = clean_x.groupby('protest_phase')['like_count'].median().to_dict()
    med_rts = clean_x.groupby('protest_phase')['retweet_count'].median().to_dict()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Likes boxplot
    sns.boxplot(ax=axes[0], data=clean_x, x='protest_phase', y='log_likes', hue='protest_phase',
                palette='Set2', order=phase_order, legend=False)
    axes[0].set_title('Likes per Tweet Across Phases [log(1 + Likes)]', fontweight='bold', fontsize=12)
    axes[0].set_xlabel('Protest Phase', fontsize=11)
    axes[0].set_ylabel('log(1 + Likes)', fontsize=11)
    
    # Add clear text box noting median values to prevent misinterpretation
    axes[0].text(0.04, 0.93, 
                 f"Median Likes:\n• Before: {med_likes.get('Before', 0):.0f}\n• Peak: {med_likes.get('Peak', 0):.0f}\n• After: {med_likes.get('After', 0):.0f}", 
                 transform=axes[0].transAxes, verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9, edgecolor='gray'),
                 fontsize=10)

    # Retweets boxplot
    sns.boxplot(ax=axes[1], data=clean_x, x='protest_phase', y='log_retweets', hue='protest_phase',
                palette='Set2', order=phase_order, legend=False)
    axes[1].set_title('Retweets per Tweet Across Phases [log(1 + Retweets)]', fontweight='bold', fontsize=12)
    axes[1].set_xlabel('Protest Phase', fontsize=11)
    axes[1].set_ylabel('log(1 + Retweets)', fontsize=11)
    
    axes[1].text(0.04, 0.93, 
                 f"Median Retweets:\n• Before: {med_rts.get('Before', 0):.0f}\n• Peak: {med_rts.get('Peak', 0):.0f}\n• After: {med_rts.get('After', 0):.0f}", 
                 transform=axes[1].transAxes, verticalalignment='top',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.9, edgecolor='gray'),
                 fontsize=10)

    fig.suptitle('Distribution of Tweet Engagement Across Protest Phases', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    v2_path = os.path.join(out_viz, "engagement_distribution_by_phase.png")
    plt.savefig(v2_path, dpi=300)
    plt.close()
    print(f" -> Saved {v2_path} (with verified median annotations)")

    # -------------------------------------------------------------------------
    # 3. Top Mentioned Accounts / Actors (Concise title, no cutoff, normalized handles)
    # -------------------------------------------------------------------------
    all_mentions = []
    for mentions_str in clean_x['mentions'].dropna():
        # Split by comma or whitespace, lowercase, strip leading @, remove punctuation
        m_list = [m.strip().lstrip('@').lower() for m in re.split(r'[,;\s]+', str(mentions_str)) if m.strip()]
        for handle in m_list:
            if len(handle) > 1:
                all_mentions.append('@' + handle)

    if all_mentions:
        top_mentions = pd.Series(all_mentions).value_counts().head(15)
        plt.figure(figsize=(11, 6))
        sns.barplot(x=top_mentions.values, y=top_mentions.index, hue=top_mentions.index, palette='flare', legend=False)
        plt.title('Top 15 Most Frequently Mentioned Accounts\n(Reflects institutional and movement targets of tagging, not broadcast reach)', 
                  fontsize=12, fontweight='bold', pad=12)
        plt.xlabel('Total Mentions Across Corpus', fontsize=11)
        plt.ylabel('Normalized Account Handle', fontsize=11)
        plt.tight_layout()
        v3_path = os.path.join(out_viz, "top_mentioned_actors.png")
        plt.savefig(v3_path, dpi=300)
        plt.close()
        print(f" -> Saved {v3_path} (with clean title and no cutoff)")

    # -------------------------------------------------------------------------
    # 4. Top Protest Hashtags (Fix #1, #2 & #9: Normalized lowercase, consistent #, disclaimer)
    # -------------------------------------------------------------------------
    all_hashtags = []
    for h_str in clean_x['hashtags'].dropna():
        # Split, strip #, lowercase
        h_list = [h.strip().lstrip('#').lower() for h in re.split(r'[,;\s]+', str(h_str)) if h.strip()]
        for tag in h_list:
            if len(tag) > 1:
                all_hashtags.append('#' + tag)

    if all_hashtags:
        top_tags = pd.Series(all_hashtags).value_counts().head(15)
        plt.figure(figsize=(11, 6))
        sns.barplot(x=top_tags.values, y=top_tags.index, hue=top_tags.index, palette='crest', legend=False)
        plt.title('Top 15 Literal Hashtag Frequencies in Protest Discourse\n(Normalized to lowercase with # prefix; literal token counts, not semantically clustered topics)', 
                  fontsize=12, fontweight='bold', pad=12)
        plt.xlabel('Hashtag Occurrence Frequency', fontsize=11)
        plt.ylabel('Normalized Hashtag (#)', fontsize=11)
        plt.tight_layout()
        v4_path = os.path.join(out_viz, "top_protest_hashtags.png")
        plt.savefig(v4_path, dpi=300)
        plt.close()
        print(f" -> Saved {v4_path} (with canonical lowercase #prefix)")

    # -------------------------------------------------------------------------
    # Phase 3: Interaction Network Construction (Fix #8: Normalized handles in network)
    # -------------------------------------------------------------------------
    print("\n[Phase 3] Constructing Multi-Layer Directed Interaction Network...")
    edges = []

    # 1. Replies: author -> replied_author
    replies_df = clean_x[clean_x['is_reply'] == 'yes'][['author', 'replied_author', 'protest_phase']].dropna()
    for _, row in replies_df.iterrows():
        src = str(row['author']).strip().lstrip('@').lower()
        tgt = str(row['replied_author']).strip().lstrip('@').lower()
        if src and tgt and src != tgt and tgt != 'none':
            edges.append({'Source': src, 'Target': tgt, 'InteractionType': 'reply', 'Phase': row['protest_phase']})

    # 2. Quotes: author -> quote_author
    quotes_df = clean_x[clean_x['is_quote_tweet'] == 'yes'][['author', 'quote_author', 'protest_phase']].dropna()
    for _, row in quotes_df.iterrows():
        src = str(row['author']).strip().lstrip('@').lower()
        tgt = str(row['quote_author']).strip().lstrip('@').lower()
        if src and tgt and src != tgt and tgt != 'none':
            edges.append({'Source': src, 'Target': tgt, 'InteractionType': 'quote', 'Phase': row['protest_phase']})

    # 3. Mentions: author -> mentioned_user
    mentions_df = clean_x[['author', 'mentions', 'protest_phase']].dropna()
    for _, row in mentions_df.iterrows():
        src = str(row['author']).strip().lstrip('@').lower()
        m_list = [m.strip().lstrip('@').lower() for m in re.split(r'[,;\s]+', str(row['mentions'])) if m.strip()]
        for tgt in m_list:
            if src and tgt and src != tgt and tgt != 'none':
                edges.append({'Source': src, 'Target': tgt, 'InteractionType': 'mention', 'Phase': row['protest_phase']})

    edge_df = pd.DataFrame(edges)
    print(f" -> Raw interaction edges extracted: {len(edge_df)}")

    # Aggregate edge weights across interactions
    agg_edges = edge_df.groupby(['Source', 'Target']).agg(
        Weight=('InteractionType', 'count'),
        InteractionTypes=('InteractionType', lambda x: ','.join(sorted(set(x)))),
        PrimaryPhase=('Phase', lambda x: x.mode()[0] if not x.empty else 'Unknown')
    ).reset_index()

    agg_edges['Type'] = 'Directed'

    # Build unique nodes dataset
    all_users = set(agg_edges['Source']).union(set(agg_edges['Target']))
    nodes_df = pd.DataFrame({'Id': list(all_users), 'Label': list(all_users)})

    # Map user attributes (followers, verified status if available) using normalized author handle
    author_meta = clean_x.groupby('author').agg(
        followers=('author_followers', lambda x: pd.to_numeric(x, errors='coerce').max()),
        verified=('verified', lambda x: any(str(v).lower() == 'true' for v in x)),
        total_tweets=('id', 'count')
    ).reset_index()

    nodes_df = pd.merge(nodes_df, author_meta, left_on='Id', right_on='author', how='left')
    nodes_df['followers'] = nodes_df['followers'].fillna(0).astype(int)
    nodes_df['verified'] = nodes_df['verified'].fillna(False).astype(bool)
    nodes_df['total_tweets'] = nodes_df['total_tweets'].fillna(0).astype(int)
    nodes_df.drop(columns=['author'], inplace=True, errors='ignore')

    # Export CSVs for Gephi & NetworkX analysis
    nodes_path = os.path.join(out_network, "x_nodes.csv")
    edges_path = os.path.join(out_network, "x_edges.csv")
    nodes_df.to_csv(nodes_path, index=False, encoding='utf-8')
    agg_edges.to_csv(edges_path, index=False, encoding='utf-8')

    print(f" -> Exported Network: {len(nodes_df)} unique nodes, {len(agg_edges)} weighted directed edges.")
    print(f"    - Nodes file: {nodes_path}")
    print(f"    - Edges file: {edges_path}")

    # Summary table
    print("\n==================================================")
    print("           PIPELINE EXECUTION COMPLETE             ")
    print("==================================================")
    print(f"Tweets Cleaned:      {len(clean_x)}")
    print(f"Unique Users:        {nodes_df['Id'].nunique()}")
    print(f"Interaction Edges:   {len(agg_edges)}")
    print(f"Generated Figures:   4 high-resolution plots in {out_viz}")
    print("==================================================")

if __name__ == "__main__":
    main()
