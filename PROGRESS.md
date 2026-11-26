# Project progress

**Project:** Echo chambers and opinion polarization in CJP–NEET protest discourse  
**Platforms:** X and Reddit  
**Updated:** 24 November 2026, 3:00 AM IST

Steps 1–9 were already in the repository. This file records steps 10 and 11, which finish the analysis, and the step that is still open.

## Finished

| Step | What was done | Where it lives |
| --- | --- | --- |
| 1–7 | Cleaned data, EDA, interaction graphs, Louvain communities, VADER sentiment, stance labels, and the 180-item stance check | `output/01_preprocessing/` through `output/07_stance_validation/` |
| 8 | E-I index. Communities point inward. On X the network gets more inward from Before to After. | `output/08_polarization/` |
| 9 | Cross-stance mixing. Pro-CJP users mostly talk to Pro-CJP users. Anti-CJP users mostly reach Pro-CJP users, on both platforms. | `output/09_cross_platform/` |
| 10 | Random walk controversy. A walker who starts on one stance side usually can reach the other. The full-period score is 0.05 on X and 0.03 on Reddit. A sealed split would be near 1. Peak on X is the most separated moment, at 0.14. | `scripts/random_walk_controversy.py`, `output/10_random_walk_controversy/` |
| 11 | Themes. Both platforms are mostly the Jantar Mantar street protest. On X, C5 is the hashtag campaign (56%) and C6 is the street protest (52%). Reddit communities are closer to each other. The theme barely changes from Before to After. | `scripts/topic_modeling.py`, `output/11_topic_modeling/` |

Step 10 was committed at 2:00 AM IST on 24 November 2026. Step 11 was committed at 3:00 AM IST the same day.

## What the results mean together

Communities are structurally inward, and the smaller stance side still reaches the larger one. Those cross-ties are enough for the two sides to meet. The communities are also not split into unrelated subjects. They share one grievance, with one X community framing it as a hashtag campaign.

## Left: two dashboards

The analysis steps are done. Two dashboards are left. Both use the summary tables only. Neither one includes raw posts or account names. Streamlit is not part of this plan.

They show the same four views:

1. Volume, sentiment, and stance for Before, Peak, and After on X.
2. Community size, stance mix, and sentiment.
3. E-I scores and the stance mixing table, with X beside Reddit.
4. The step 10 controversy score and the step 11 theme mix.

**Tableau.** This is the dashboard named in the course handout. Build one workbook and publish it on Tableau Public. That publication is the standard course link.

**Vercel.** This is a separate page in HTML, CSS, and JavaScript, deployed on Vercel, for a public link with a layout the team controls. It is a standard way to publish a finished dashboard when every number is already computed. The page only displays the tables and charts. It does not replace the Tableau workbook.

Gephi remains a separate network figure, not a sheet inside either dashboard.

## Possible next steps

1. Build the Tableau workbook from `output/` and publish it on Tableau Public.
2. Build the HTML dashboard and deploy it on Vercel.
3. Export Gephi figures of the existing networks if the viva needs a static network picture.
4. Write the end-term report and add steps 8–11 to the slides. The current deck stops at step 7.
