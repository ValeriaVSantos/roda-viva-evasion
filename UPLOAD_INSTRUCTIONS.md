# Upload instructions

Do not delete the repository or its Git history.

1. Open the existing repository in GitHub Desktop.
2. Copy this prepared folder over the local repository folder.
3. Replace files when prompted; do not remove files that exist only in the original folder unless they are listed below.
4. Review changes in GitHub Desktop.
5. Commit with: `Add multi-annotator extension and agreement analysis`.
6. Push and confirm that the automated tests pass.

## Files to remove from the public repository

- `scripts/__pycache__/` and all `.pyc` files.

## Files to keep

- The initial paper source, clearly marked in the README as non-peer-reviewed.
- The original experimental scripts.
- Git history.

## Before a public release

- Confirm the license for the annotation layer.
- Decide whether missing labels will be completed or handled under a documented partial-coverage policy.
- Adjudicate the item flagged `ADJUDICATION_REQUIRED` and review majority-disagreement cases.
- Re-run the model baselines against the final gold labels.
