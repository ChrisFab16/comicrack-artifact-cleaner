# Spike: Legal / packaging (T011)

**Date**: 2026-09-30  
**Upstream**: https://github.com/jiaxi-jiang/FBCNN  
**License**: Apache License 2.0 (repo LICENSE + README badge)

## Decision

| Topic | Choice |
|-------|--------|
| Code/weights redistribution | Allowed under Apache-2.0 with LICENSE + NOTICE/attribution |
| Plugin zip contents | **Download-on-first-enable** (or Configure download) for `.onnx` — keep `.crplugin` small |
| Bundling | Legally OK if NOTICE shipped; not preferred for v1 package size |
| Attribution | Ship under `ArtifactCleaner/licenses/` (T038): FBCNN Apache-2.0 + ONNX Runtime notices |

## Pinning

At implement time, pin:

- Upstream commit or release tag for FBCNN
- Exact weight filenames + sha256 (record in `contracts/model-package.md` when first downloaded)

## Contract impact

`contracts/model-package.md` already prefers download-on-first-enable — no change required beyond sha256 pins later.

## Exit criteria

- [X] License identified (Apache-2.0)
- [X] Download-vs-bundle decision recorded
- [ ] sha256 pins for release assets (fill when weights first fetched in T009/T024)
