"""
Step 11: What the communities are talking about.

Sentiment scores how a post feels. Stance scores which side it takes.
Neither says what the post is about. This step fits one topic model on the
cleaned X and Reddit text, then compares the mix of themes across communities
and across the Before, Peak, and After phases on X.

Search words such as "cjp" and "neet" are removed from the topic labels.
They were the collection filter, so they sit in almost every post and would
otherwise hide the actual grievance.
"""

import os
import sys
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial.distance import jensenshannon
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer

sys.stdout.reconfigure(encoding="utf-8")

COMMUNITIES = ["C1", "C2", "C3", "C4", "C5", "C6"]
PHASES = ["Before", "Peak", "After"]
MIN_WORDS = 5
RANDOM_SEED = 42
SHUFFLE_RUNS = 30
THEME_FOOTNOTE = (
    "Each row is the share of posts assigned to a theme. "
    "Posts under 5 words and unsorted posts are excluded. Percents are rounded."
)
# Names for this fit, read from the top words of each topic id.
DISPLAY_NAMES = {
    0: "Street protest",
    1: "Hashtag campaign",
    8: "Education minister",
    2: "Video and media",
    3: "BJP and Congress",
    4: "Organizer accounts",
    5: "Hindu and country",
    6: "Students",
    10: "Exam",
    7: "Rahul Gandhi",
    9: "Umar Khalid",
}
# Collection keywords. They define the dataset, not a theme inside it.
QUERY_STOPWORDS = {
    "cjp",
    "neet",
    "protest",
    "protests",
    "protesting",
    "protester",
    "protesters",
    "https",
    "http",
    "www",
    "com",
    "amp",
    "rt",
    "via",
}
# Function words in Hinglish and Hindi. They are grammar, not a grievance.
FUNCTION_STOPWORDS = {
    "hai",
    "hain",
    "ke",
    "ka",
    "ki",
    "se",
    "nahi",
    "nahin",
    "mein",
    "ko",
    "ho",
    "ye",
    "yeh",
    "aur",
    "bhi",
    "toh",
    "kya",
    "tha",
    "thi",
    "hum",
    "aap",
    "woh",
    "vo",
    "na",
    "par",
    "pe",
    "liye",
    "kar",
    "kaun",
    "kyu",
    "kyun",
    "और",
    "पर",
    "के",
    "की",
    "का",
    "है",
    "में",
    "से",
    "को",
    "ने",
    "यह",
    "वह",
    "नहीं",
    "भी",
    "तो",
    "ही",
    "एक",
    "लिए",
    "कर",
    "करने",
    "हैं",
    "था",
    "थी",
    "हो",
    "या",
    "कि",
}


def project_root():
    """Repository root, one level above this scripts/ file."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def js_distance(left, right):
    """
    Jensen-Shannon distance between two theme mixes.

    0 means the same mix. 1 means the two groups share no theme.
    SciPy returns the base-2 distance, which already sits on that 0 to 1 scale.
    """
    left = np.asarray(left, dtype=float)
    right = np.asarray(right, dtype=float)
    left_total = left.sum()
    right_total = right.sum()
    if left_total <= 0 or right_total <= 0:
        return None
    return float(jensenshannon(left / left_total, right / right_total, base=2))


def pairwise_js(count_table):
    """Mean and the single largest gap between communities in one table."""
    names = list(count_table.index)
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            distance = js_distance(count_table.loc[names[i]], count_table.loc[names[j]])
            if distance is None:
                continue
            pairs.append((names[i], names[j], distance))
    if not pairs:
        return None, None, []
    distances = [item[2] for item in pairs]
    widest = max(pairs, key=lambda item: item[2])
    return float(np.mean(distances)), widest, pairs


def shuffle_baseline(community_labels, topic_ids, runs, seed):
    """
    Mean pairwise distance if community labels were random.

    The observed distance has to clear this bar before it means the
    communities are actually talking about different things.
    """
    labels = np.asarray(community_labels)
    topics = np.asarray(topic_ids)
    generator = np.random.default_rng(seed)
    scores = []
    for _ in range(runs):
        shuffled = labels.copy()
        generator.shuffle(shuffled)
        table = theme_count_table(shuffled, topics)
        mean_distance, _widest, _pairs = pairwise_js(table)
        if mean_distance is not None:
            scores.append(mean_distance)
    if not scores:
        return None
    return float(np.mean(scores))


def theme_count_table(communities, topics, community_order=None):
    """Rows are communities, columns are theme ids, values are post counts."""
    frame = pd.DataFrame({"Community": communities, "Topic": topics})
    frame = frame[frame["Topic"] != -1]
    if frame.empty:
        return pd.DataFrame()
    table = pd.crosstab(frame["Community"], frame["Topic"])
    if community_order is not None:
        present = [name for name in community_order if name in table.index]
        table = table.reindex(present).fillna(0)
    return table.astype(float)


def check_js_distance_bounds():
    """Identical mixes score 0. Mixes with nothing in common score 1."""
    same = js_distance([10, 20, 30], [10, 20, 30])
    apart = js_distance([10, 0, 0], [0, 0, 12])
    if same is None or apart is None:
        raise RuntimeError("Jensen-Shannon check did not return a score.")
    if abs(same) > 1e-9:
        raise RuntimeError(f"Identical mixes should score 0, got {same}.")
    if abs(apart - 1) > 1e-6:
        raise RuntimeError(f"Disjoint mixes should score 1, got {apart}.")
    return same, apart


def load_posts(root):
    """Cleaned posts that are long enough to carry a theme."""
    x_posts = pd.read_csv(
        os.path.join(root, "output", "06_stance_analysis", "x", "x_tweets_with_stance.csv"),
        usecols=["clean_text", "Community", "protest_phase"],
    )
    reddit_posts = pd.read_csv(
        os.path.join(root, "output", "06_stance_analysis", "reddit", "reddit_items_with_stance.csv"),
        usecols=["clean_text", "Community"],
    )
    x_posts["Platform"] = "X"
    x_posts["Phase"] = x_posts["protest_phase"].astype(str).str.strip()
    reddit_posts["Platform"] = "Reddit"
    reddit_posts["Phase"] = "Full"
    posts = pd.concat(
        [
            x_posts[["clean_text", "Community", "Platform", "Phase"]],
            reddit_posts[["clean_text", "Community", "Platform", "Phase"]],
        ],
        ignore_index=True,
    )
    posts["clean_text"] = posts["clean_text"].fillna("").astype(str).str.strip()
    posts["Community"] = posts["Community"].fillna("Unclustered").astype(str).str.strip()
    word_count = posts["clean_text"].str.split().str.len()
    posts = posts[word_count >= MIN_WORDS].reset_index(drop=True)
    return posts


def fit_topics(texts, embedding_path):
    """
    One BERTopic model for both platforms.

    Embeddings are multilingual, because the posts mix English with Hindi
    and Bengali. Theme names are rebuilt with the same stop-word list after
    any merge. Without that, BERTopic replaces the list and the labels
    collapse into words like "the" and "and".
    """
    from bertopic import BERTopic
    from bertopic.vectorizers import ClassTfidfTransformer
    from hdbscan import HDBSCAN
    from sentence_transformers import SentenceTransformer
    from umap import UMAP

    stops = list(ENGLISH_STOP_WORDS.union(QUERY_STOPWORDS).union(FUNCTION_STOPWORDS))
    vectorizer = CountVectorizer(stop_words=stops, ngram_range=(1, 2), min_df=10)
    ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)
    embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    if os.path.exists(embedding_path):
        embeddings = np.load(embedding_path)
        if len(embeddings) != len(texts):
            embeddings = None
    else:
        embeddings = None
    if embeddings is None:
        embeddings = embedding_model.encode(texts, batch_size=64, show_progress_bar=True)
        np.save(embedding_path, embeddings)
    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=UMAP(
            n_neighbors=15,
            n_components=5,
            min_dist=0.0,
            metric="cosine",
            random_state=RANDOM_SEED,
        ),
        hdbscan_model=HDBSCAN(
            min_cluster_size=40,
            min_samples=5,
            metric="euclidean",
            prediction_data=True,
        ),
        vectorizer_model=vectorizer,
        ctfidf_model=ctfidf_model,
        calculate_probabilities=False,
        verbose=False,
    )
    topics, _probs = topic_model.fit_transform(texts, embeddings=embeddings)
    topics = np.asarray(topics)
    theme_count = int(len(set(topics) - {-1}))
    print(f"Themes before merging: {theme_count}. Unsorted share: {np.mean(topics == -1):.1%}.")
    if theme_count > 12:
        topic_model.reduce_topics(texts, nr_topics=12, use_ctfidf=True)
        topics = np.asarray(topic_model.topics_)
    outlier_share = float(np.mean(topics == -1))
    if outlier_share > 0.35:
        topics = np.asarray(topic_model.reduce_outliers(list(texts), topics.tolist(), strategy="c-tf-idf"))
        topic_model.update_topics(
            list(texts),
            topics=topics.tolist(),
            vectorizer_model=vectorizer,
            ctfidf_model=ctfidf_model,
        )
        topics = np.asarray(topic_model.topics_)
    return topic_model, topics


def topic_label_table(topic_model):
    """Short word label for each theme, plus how many posts it holds."""
    info = topic_model.get_topic_info()
    rows = []
    for row in info.itertuples(index=False):
        topic_id = int(row.Topic)
        if topic_id == -1:
            label = "Unsorted"
            words = ""
        else:
            words = ", ".join(word for word, _score in topic_model.get_topic(topic_id)[:6])
            label = " / ".join(word for word, _score in topic_model.get_topic(topic_id)[:3])
        rows.append(
            {
                "Topic": topic_id,
                "Label": label,
                "Top_Words": words,
                "Posts": int(row.Count),
            }
        )
    table = pd.DataFrame(rows).sort_values("Posts", ascending=False)
    return table


def mix_by(posts, column, group_order):
    """Theme counts and row percentages for one grouping column."""
    counts = theme_count_table(posts[column], posts["Topic"], group_order)
    if counts.empty:
        return counts, counts
    shares = counts.div(counts.sum(axis=1), axis=0)
    return counts, shares


def theme_display_name(topic_id, fallback):
    """Slide name for a theme. Unknown topic ids keep the model words."""
    return DISPLAY_NAMES.get(int(topic_id), fallback)


def ordered_theme_ids(labels):
    """Largest theme first, so the same column order can be used on every chart."""
    themed = labels[labels["Topic"].astype(int) != -1].copy()
    themed["Topic"] = themed["Topic"].astype(int)
    themed = themed.sort_values(["Posts", "Topic"], ascending=[False, True])
    return [int(topic) for topic in themed["Topic"]]


def wrap_theme_name(name):
    """Two lines when a name is too long to sit under one column."""
    words = str(name).split()
    if len(words) < 2 or len(name) <= 12:
        return str(name)
    midpoint = max(1, len(words) // 2)
    return " ".join(words[:midpoint]) + "\n" + " ".join(words[midpoint:])


def format_share(share):
    """Whole numbers for large shares. One decimal so a small share is not shown as zero."""
    if share < 0.05:
        return "0"
    if share < 10:
        return f"{share:.1f}"
    return f"{share:.0f}"


def cell_text_color(share):
    """White text on dark blue, black text on light blue."""
    red, green, blue, _alpha = plt.cm.Blues(np.clip(share / 100.0, 0, 1))
    luminance = (0.2126 * red) + (0.7152 * green) + (0.0722 * blue)
    if luminance < 0.45:
        return "white"
    return "#1a1a1a"


def plot_theme_heatmap(counts, column_order, display_names, title, out_path, row_axis):
    """
    One heatmap on a fixed 0–100 scale.

    Counts supply the row size printed beside each group. Shares are rescaled
    within the row, which matches the footnote on the chart.
    """
    table = counts.copy()
    table.columns = [int(column) for column in table.columns]
    ordered = [topic for topic in column_order if topic in table.columns]
    table = table[ordered]
    row_totals = table.sum(axis=1)
    shares = table.div(row_totals, axis=0) * 100
    values = shares.to_numpy(dtype=float)
    row_labels = [f"{name}  (n={int(row_totals.loc[name])})" for name in table.index]
    column_labels = [wrap_theme_name(display_names.get(topic, str(topic))) for topic in ordered]

    figure_height = 6.2 if len(table) > 3 else 5.2
    figure, axis = plt.subplots(figsize=(14.8, figure_height))
    image = axis.imshow(values, aspect="auto", cmap="Blues", vmin=0, vmax=100)
    axis.set_xticks(np.arange(len(column_labels)))
    axis.set_xticklabels(column_labels, rotation=0, ha="center", fontsize=8)
    axis.set_yticks(np.arange(len(row_labels)))
    axis.set_yticklabels(row_labels, fontsize=9)
    axis.set_xlabel("Theme")
    axis.set_ylabel(row_axis)
    axis.set_title("\n".join(textwrap.wrap(title, 78)), fontsize=12, pad=12)
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            share = float(values[row, col])
            axis.text(
                col,
                row,
                format_share(share),
                ha="center",
                va="center",
                fontsize=8,
                color=cell_text_color(share),
            )
    colorbar = figure.colorbar(image, ax=axis, fraction=0.03, pad=0.02)
    colorbar.set_label("Share of themed posts (%)")
    colorbar.set_ticks([0, 25, 50, 75, 100])
    figure.tight_layout(rect=(0, 0.08, 1, 1))
    figure.text(0.01, 0.015, THEME_FOOTNOTE, fontsize=8, color="#444444", ha="left")
    figure.savefig(out_path, dpi=160)
    plt.close(figure)


def share_table(counts, column_order, display_names):
    """Row percentages with slide names, in the same order as the charts."""
    table = counts.copy()
    table.columns = [int(column) for column in table.columns]
    ordered = [topic for topic in column_order if topic in table.columns]
    shares = table[ordered].div(table.sum(axis=1), axis=0)
    shares.columns = [display_names.get(topic, str(topic)) for topic in ordered]
    return shares


def run_topic_modeling():
    """Fit the themes, compare communities and X phases, and save the charts."""
    same, apart = check_js_distance_bounds()
    print("=======================================================================")
    print("      STEP 11: THEMES IN THE CJP-NEET POSTS                           ")
    print("=======================================================================")
    print(f"Check: identical mixes score {same:.0f}. Mixes with nothing in common score {apart:.0f}.")

    root = project_root()
    out_dir = os.path.join(root, "output", "11_topic_modeling")
    os.makedirs(out_dir, exist_ok=True)
    posts = load_posts(root)
    print(f"Posts used: {len(posts):,} with at least {MIN_WORDS} words.")
    topic_model, topics = fit_topics(
        posts["clean_text"].tolist(),
        os.path.join(out_dir, "embeddings.npy"),
    )
    posts["Topic"] = topics

    labels = topic_label_table(topic_model)
    labels["Display_Name"] = [
        theme_display_name(topic, fallback) for topic, fallback in zip(labels["Topic"], labels["Label"])
    ]
    label_map = dict(zip(labels["Topic"].astype(int), labels["Display_Name"]))
    column_order = ordered_theme_ids(labels)
    print("\n--- Themes ---")
    print(labels.to_string(index=False))

    labels.to_csv(os.path.join(out_dir, "topic_labels.csv"), index=False, encoding="utf-8")
    posts[["Platform", "Community", "Phase", "Topic"]].to_csv(
        os.path.join(out_dir, "post_topics.csv"), index=False, encoding="utf-8"
    )

    summary_rows = []
    pair_rows = []
    for platform in ["X", "Reddit"]:
        platform_posts = posts[(posts["Platform"] == platform) & (posts["Community"].isin(COMMUNITIES))]
        counts, _shares = mix_by(platform_posts, "Community", COMMUNITIES)
        counts.to_csv(os.path.join(out_dir, f"{platform.lower()}_community_topic_counts.csv"), encoding="utf-8")
        share_table(counts, column_order, label_map).to_csv(
            os.path.join(out_dir, f"{platform.lower()}_community_topic_shares.csv"),
            encoding="utf-8",
        )
        title = {
            "X": "On X, C5 is a hashtag campaign. The other communities are the street protest.",
            "Reddit": "On Reddit, every community is mostly the street protest.",
        }[platform]
        plot_theme_heatmap(
            counts,
            column_order,
            label_map,
            title,
            os.path.join(out_dir, f"{platform.lower()}_community_topic_mix.png"),
            "Community",
        )
        observed, widest, pairs = pairwise_js(counts)
        baseline = shuffle_baseline(
            platform_posts.loc[platform_posts["Topic"] != -1, "Community"].tolist(),
            platform_posts.loc[platform_posts["Topic"] != -1, "Topic"].tolist(),
            SHUFFLE_RUNS,
            RANDOM_SEED,
        )
        summary_rows.append(
            {
                "Platform": platform,
                "Comparison": "Communities C1-C6",
                "Mean_JS": None if observed is None else round(observed, 4),
                "Shuffle_Mean_JS": None if baseline is None else round(baseline, 4),
                "Widest_Pair": None if widest is None else f"{widest[0]} vs {widest[1]}",
                "Widest_JS": None if widest is None else round(widest[2], 4),
            }
        )
        for left, right, distance in pairs:
            pair_rows.append(
                {
                    "Platform": platform,
                    "Group": f"{left} vs {right}",
                    "JS_Distance": round(distance, 4),
                }
            )
        print(f"\n{platform} communities: mean JS = {observed:.3f}, random-label JS = {baseline:.3f}")
        if widest is not None:
            print(f"  Widest gap: {widest[0]} vs {widest[1]} ({widest[2]:.3f})")

    x_posts = posts[posts["Platform"] == "X"]
    phase_counts, _phase_shares = mix_by(x_posts, "Phase", PHASES)
    phase_counts.index.name = "Phase"
    phase_counts.to_csv(os.path.join(out_dir, "x_phase_topic_counts.csv"), encoding="utf-8")
    phase_share_out = share_table(phase_counts, column_order, label_map)
    phase_share_out.index.name = "Phase"
    phase_share_out.to_csv(os.path.join(out_dir, "x_phase_topic_shares.csv"), encoding="utf-8")
    plot_theme_heatmap(
        phase_counts,
        column_order,
        label_map,
        "On X, the street protest stays the main theme across Before, Peak, and After.",
        os.path.join(out_dir, "x_phase_topic_mix.png"),
        "Phase",
    )
    before_peak = js_distance(phase_counts.loc["Before"], phase_counts.loc["Peak"])
    peak_after = js_distance(phase_counts.loc["Peak"], phase_counts.loc["After"])
    summary_rows.append(
        {
            "Platform": "X",
            "Comparison": "Before vs Peak",
            "Mean_JS": None if before_peak is None else round(before_peak, 4),
            "Shuffle_Mean_JS": None,
            "Widest_Pair": "Before vs Peak",
            "Widest_JS": None if before_peak is None else round(before_peak, 4),
        }
    )
    summary_rows.append(
        {
            "Platform": "X",
            "Comparison": "Peak vs After",
            "Mean_JS": None if peak_after is None else round(peak_after, 4),
            "Shuffle_Mean_JS": None,
            "Widest_Pair": "Peak vs After",
            "Widest_JS": None if peak_after is None else round(peak_after, 4),
        }
    )
    print(f"\nX phases: Before vs Peak JS = {before_peak:.3f}, Peak vs After JS = {peak_after:.3f}")

    summary = pd.DataFrame(summary_rows)
    pairs = pd.DataFrame(pair_rows).sort_values(["Platform", "JS_Distance"], ascending=[True, False])
    summary.to_csv(os.path.join(out_dir, "topic_js_summary.csv"), index=False, encoding="utf-8")
    pairs.to_csv(os.path.join(out_dir, "community_topic_js_pairs.csv"), index=False, encoding="utf-8")
    print(f"\nSaved tables and charts in {out_dir}")
    return summary


def redraw_saved_charts():
    """Redraw the three theme charts from the saved counts. Does not refit the model."""
    root = project_root()
    out_dir = os.path.join(root, "output", "11_topic_modeling")
    labels = pd.read_csv(os.path.join(out_dir, "topic_labels.csv"))
    labels["Display_Name"] = [
        theme_display_name(topic, fallback) for topic, fallback in zip(labels["Topic"], labels["Label"])
    ]
    labels.to_csv(os.path.join(out_dir, "topic_labels.csv"), index=False, encoding="utf-8")
    label_map = dict(zip(labels["Topic"].astype(int), labels["Display_Name"]))
    column_order = ordered_theme_ids(labels)

    charts = [
        (
            "x_community_topic_counts.csv",
            "x_community_topic_shares.csv",
            "x_community_topic_mix.png",
            "On X, C5 is a hashtag campaign. The other communities are the street protest.",
            "Community",
        ),
        (
            "reddit_community_topic_counts.csv",
            "reddit_community_topic_shares.csv",
            "reddit_community_topic_mix.png",
            "On Reddit, every community is mostly the street protest.",
            "Community",
        ),
        (
            "x_phase_topic_counts.csv",
            "x_phase_topic_shares.csv",
            "x_phase_topic_mix.png",
            "On X, the street protest stays the main theme across Before, Peak, and After.",
            "Phase",
        ),
    ]
    for counts_name, shares_name, image_name, title, row_axis in charts:
        counts = pd.read_csv(os.path.join(out_dir, counts_name), index_col=0)
        counts.index.name = row_axis
        shares = share_table(counts, column_order, label_map)
        shares.index.name = row_axis
        shares.to_csv(os.path.join(out_dir, shares_name), encoding="utf-8")
        plot_theme_heatmap(
            counts,
            column_order,
            label_map,
            title,
            os.path.join(out_dir, image_name),
            row_axis,
        )
        print(f"Saved {image_name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--redraw":
        redraw_saved_charts()
    else:
        run_topic_modeling()
