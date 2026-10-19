# Topics

How a week turns into a blog post, in four pieces:

- **`digests/`** — one dated file per week (`YYYY-MM-DD.md`), written by the
  scheduled forecasting-news crawl. Each digest is a short, link-forward
  research log: what showed up this week, and which of it might be worth a
  post. Treat it as a scratchpad, not something to polish — it's an input to
  deciding the week's topic, not the post itself.
- **`chatgpt-reports/`** — raw weekly reports dropped in by the external
  ChatGPT research task, one dated file per report. Inputs only, not meant
  to be read directly — see [chatgpt-reports/README.md](chatgpt-reports/README.md).
- **`backlog.md`** — the running, de-duplicated list of candidate topics,
  accumulated across digests, ChatGPT reports, and anything added by hand.
  This is what you actually look at when picking what to write next.
- **This file** — the workflow, so a future session (human or scheduled
  agent) doesn't have to reverse-engineer it from the other three.

## The weekly crawl

A scheduled cloud agent runs every Monday morning. It:

1. Searches for new time-series-forecasting research/developments since the
   last digest.
2. Checks `chatgpt-reports/` for any report not yet merged (tracked by
   whether a prior digest mentions that filename).
3. Writes `digests/<date>.md`, appends anything genuinely new from both
   sources to `backlog.md`, and adds promising papers to
   [literature/index.md](../literature/index.md).
4. Opens a PR with all of it — never pushes straight to `main`.

Manage the routine itself at
[claude.ai/code/routines](https://claude.ai/code/routines).

**Merge (or close) each week's digest PR before the next Monday run.** The
routine only ever reads `main` — an unmerged PR is invisible to the next
run, which will then have no idea a prior digest exists and will re-cover
the same ground from scratch. If two digest PRs end up open at once, merging
the second will likely hit a small conflict in `backlog.md`/
`literature/index.md`; it's just two blocks of added rows, keep both.

## Feeding it from outside

- **ChatGPT report:** have the task commit (or drop, via the GitHub UI)
  a dated file directly into `chatgpt-reports/` — see that directory's
  README for the convention. It commits straight to `main`; nothing to
  review before it lands, since it's additive and doesn't touch a shared
  file. The next Monday run folds it in.
- **Anything else:** add rows to `backlog.md` or PDFs + index rows to
  `literature/` by hand whenever you come across something, or paste
  findings into a Claude Code chat and ask for them to be merged — faster
  than waiting for Monday if you want it folded in right away.

## From backlog to post

When a backlog entry turns into a real post:

1. Mark it `in-progress (post: <slug>)` in `backlog.md`.
2. Add a `notebooks/<NN>-<slug>/` + `results/<NN>-<slug>/` pair (see the
   root [README.md](../README.md) for the convention).
3. Once published, mark it `published (post: <slug>)` and add the post to
   the root README's list of companion posts.
