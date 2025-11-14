# Offending chunk files that contained sensitive material

The following files were detected by GitHub's secret scanner during the recent commits and were removed from repository history (the `deploy/CoPilot_chunks` directory was scrubbed and history was force-updated):

- `deploy/CoPilot_chunks/Microsoft Copilot_ Your AI companion.html`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_121.txt`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_122.txt`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_1579.txt`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_1590.txt`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_1610.txt`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_63.txt`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_65.txt`
- `deploy/CoPilot_chunks/copilot_chunks/chunk_946.txt`

Notes:
- These files were flagged because they contained API keys / OAuth tokens. They have been removed from the git history and are no longer present in `origin/main` after the force-push.
- Treat any credentials that appeared in those files as compromised; rotate/revoke them immediately in their provider consoles.

If you need copies of these files for analysis (for example, to find out where the tokens were used), extract them from your local reflog/backup before you run the history-scrub steps; after the scrub they are intentionally removed from the reflog as well.
