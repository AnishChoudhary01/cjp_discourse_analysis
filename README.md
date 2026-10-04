# Investigating Echo-Chamber Characteristics and Opinion Polarization in Online Discourse Surrounding the CJP–NEET Protest

**Course:** Computational Social Media Analysis (CSMA)  
**Authors:** Palak Bhatt, Manya Agarwal, Anish Choudhary, Akshit Wadhwa  

---

## 📌 Repository Organization & Workflow Architecture

The codebase is organized sequentially around a 7-stage computational social science pipeline. Each script reads from earlier stage outputs and writes to standardized directories under `output/`.

```
csma_prj/
│
├── dataset/                                   # Raw Ingested Data
│   ├── reddit_datasets/                       # Targeted Reddit posts & comments
│   └── x/                                     # X (Twitter) multi-period CSVs (Before, Peak, After)
│
├── scripts/                                   # Modular Analysis Pipeline
│   ├── reddit/
│   │   └── csma_pipeline.py                   # Stage 1A: Reddit cleaning, EDA & graph extraction
│   ├── x/
│   │   └── x_pipeline.py                      # Stage 1B: X cleaning, deduplication, regex & graph extraction
│   ├── community_detection.py                 # Stage 2: Louvain modularity & interactive PyVis graphs
│   ├── sentiment_analysis.py                  # Stage 3: VADER valence scoring & Dunn post-hoc statistics
│   ├── stance_analysis.py                     # Stage 4: Target-specific stance classification & contingency
│   ├── validate_stance_classifier.py          # Stage 5: Independent stratified gold-standard validation
│   └── polarization_metrics.py                # Stage 6: Krackhardt E-I Index, stance mixing & temporal trajectory
│
├── output/                                    # Generated Artifacts (59 Verified Assets Organized by Stage)
│   ├── 01_preprocessing/                      # Cleaned posts, comments, tweets (Reddit / X)
│   ├── 02_eda/                                # Volume, depth, top users, hashtags & phase engagement plots
│   ├── 03_network_analysis/                   # Directed edges & canonical node lists (Reddit / X)
│   ├── 04_community_detection/                # Louvain modularity summaries, static plots & PyVis HTML graphs
│   ├── 05_sentiment_analysis/                 # VADER scores, community distributions, Dunn post-hoc tests
│   ├── 06_stance_analysis/                    # 3-class target stance predictions, phase summaries & plots
│   ├── 07_stance_validation/                  # Stratified gold sample (N=180), metrics & confusion matrix
│   ├── 08_polarization/                       # Krackhardt E-I index tables & temporal trajectories (X / Reddit)
│   └── 09_cross_platform/                     # Cross-platform comparisons, heatmaps & stance mixing matrices
│
├── docs/                                      # Project Documentation & Reports
│   ├── BRIEF_PROGRESS_REPORT.md               # Mid-Term Evaluation Progress Report
│   ├── REVISED_PROJECT_TIMELINE.md            # Progress vs. Plan & Gantt chart
│   └── UPDATED_SYNOPSIS.md                    # Research questions, architecture & methodology
│
├── run_demo.py                                # Master end-to-end execution & verification harness
└── README.md                                  # Repository layout & viva guide
```

---

## 🚀 Execution Instructions

To execute the entire 7-stage pipeline end-to-end and verify all 59 project assets:

```bash
python run_demo.py
```

To run individual pipeline stages independently:

```bash
# Stage 1: Data Ingestion & Preprocessing
python scripts/reddit/csma_pipeline.py
python scripts/x/x_pipeline.py

# Stage 2: Community Detection & Modularity
python scripts/community_detection.py

# Stage 3: Valence Sentiment Scoring & Statistical Testing
python scripts/sentiment_analysis.py

# Stage 4: Target-Specific Stance Detection
python scripts/stance_analysis.py

# Stage 5: Independent Ground-Truth Validation
python scripts/validate_stance_classifier.py

# Stage 6: Krackhardt E-I Index & Polarization Analysis
python scripts/polarization_metrics.py
```
