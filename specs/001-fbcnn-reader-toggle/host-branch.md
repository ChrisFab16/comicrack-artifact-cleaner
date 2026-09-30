# Host branch workflow (ComicRackCE fork)

**Repo**: `ChrisFab16/ComicRackCE`  
**Base**: `development`  
**Do not** open PRs to `maforget/ComicRackCE` unless the operator explicitly asks (FR-017).

## Suggested branch name

Match Spec Kit sequential numbering when practical:

```text
001-fbcnn-reader-toggle
```

Create from up-to-date `development`:

```bash
cd /path/to/ComicRackCE
git fetch origin
git checkout development
git pull
git checkout -b 001-fbcnn-reader-toggle
```

## Scope on the host branch

- `IPageImageFilter` (or equivalent) + `ImagePool.GetPage` insert
- Filter fingerprint in display-cache identity
- ONNX Runtime runner (`Microsoft.ML.OnnxRuntime`)
- Per-reader-window filter state
- Processing feedback UI

Plugin UI and Spec Kit artifacts stay in `comicrack-artifact-cleaner`.

## Spike evidence

Record pipeline/API notes under this feature’s `spike-*.md` files in the plugin repo (or link CE commit SHAs from those notes).
