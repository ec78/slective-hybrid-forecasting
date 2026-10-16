# Topics

How a week turns into a blog post, in three pieces:

- **`digests/`** — one dated file per week (`YYYY-MM-DD.md`), written by the
  scheduled forecasting-news crawl. Each digest is a short, link-forward
  research log: what showed up this week, and which of it might be worth a
  post. Treat it as a scratchpad, not something to polish — it's an input to
  deciding the week's topic, not the post itself.
- **`backlog.md`** — the running, de-duplicated list of candidate topics,
  accumulated across digests (and anything you add by hand). This is what
  you actually look at when picking what to write next.
- **This file** — the workflow, so a future session (human or scheduled
  agent) doesn't have to reverse-engineer it from the other two.

## The weekly crawl

A scheduled cloud agent runs every Monday morning, searches for new
time-series-forecasting research and developments since the last digest,
writes `digests/<date>.md`, appends anything genuinely new to `backlog.md`,
adds promising papers to [literature/index.md](../literature/index.md), and
opens a PR with all of it. Review the PR, merge what's worth keeping, and
pick the week's topic from the updated backlog. Manage the routine itself at
[claude.ai/code/routines](https://claude.ai/code/routines).

## Manual additions

Nothing here requires waiting for Monday — add rows to `backlog.md` or
PDFs + index rows to `literature/` whenever you come across something,
by hand or by pasting findings from elsewhere (e.g. the old ChatGPT research
task, while it's still in parallel use).

## From backlog to post

When a backlog entry turns into a real post:

1. Mark it `in-progress (post: <slug>)` in `backlog.md`.
2. Add a `notebooks/<NN>-<slug>/` + `results/<NN>-<slug>/` pair (see the
   root [README.md](../README.md) for the convention).
3. Once published, mark it `published (post: <slug>)` and add the post to
   the root README's list of companion posts.
