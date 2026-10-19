# ChatGPT reports

Raw drops from the external ChatGPT research task, landed here as-is — one
file per report, named `YYYY-MM-DD.md` (the date the report was generated).
No particular format is required; paste or export the report's content
verbatim, no reformatting needed.

These are inputs, not the reading list — treat
[`../backlog.md`](../backlog.md) as the actual place to look when picking a
topic. The weekly crawl routine checks this directory every run, folds any
genuinely new items from unmerged reports into `backlog.md` and
[`../../literature/index.md`](../../literature/index.md), and records which
filename(s) it merged in that week's digest — that record is how it knows
not to merge the same report twice. A report only needs to land here;
nothing else has to happen for it to get folded in on the next run.

Commit directly to `main` — these are additive, dated, and don't touch any
shared file, so there's nothing to review before they land (the curated
merge into `backlog.md`/`literature/index.md` still goes through the normal
weekly PR).

If you'd rather have a report folded in right away instead of waiting for
the next Monday run, paste it into a Claude Code chat instead of, or in
addition to, dropping it here.
