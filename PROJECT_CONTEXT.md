# CJP discourse

Course study of echo chambers and opinion polarization in public posts about the Cockroach Janta Party and the NEET-UG 2026 protests. Platforms: X and Reddit. Window: 7 June–30 July 2026, split on X into Before, Peak, and After the 20 July march.

## Stack

Python analysis pipeline (`scripts/`, outputs in `output/`). Two static pages, no server app:

- `landing/` — project overview. Question, plan, dataset, findings. Protest photographs from Wikimedia Commons.
- `dashboard/` — results. Summary tables only. No raw posts or account names.
- `index.html` redirects to the landing page.

## Conventions

Numbers on the pages come from `output/` and `PROGRESS.md`. Do not invent a second copy of a metric. The landing page states the network E-I as −0.75 on X and −0.94 on Reddit. Stance, tone, and community are separate measures.

Photographs in `landing/images/` are resized derivatives. Credits and licenses stay in the landing footer. Do not drop in copyrighted news photos.

## Active work

Landing page is the public front door. Dashboard is the results view. Tableau and the end-term report are still open. See `PROGRESS.md`.
