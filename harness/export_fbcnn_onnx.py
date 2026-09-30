"""Export FBCNN color weights to ONNX (Phase 2 spike T009).

Usage (after placing fbcnn_color.pth under weights/ and cloning FBCNN upstream
or vendoring the network definition):

  python harness/export_fbcnn_onnx.py --weights weights/fbcnn_color.pth --out weights/fbcnn_color.onnx

This stub documents the interface; full export lands when upstream model code
and weights are available locally.
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export FBCNN .pth to ONNX")
    p.add_argument("--weights", default="weights/fbcnn_color.pth")
    p.add_argument("--out", default="weights/fbcnn_color.onnx")
    p.add_argument("--height", type=int, default=256)
    p.add_argument("--width", type=int, default=256)
    args = p.parse_args(argv)

    print(
        "export_fbcnn_onnx: stub — implement load/export in T009.\n"
        "  weights={0}\n  out={1}\n  dummy_size={2}x{3}".format(
            args.weights, args.out, args.height, args.width
        )
    )
    print(
        "See harness/README.md and specs/001-fbcnn-reader-toggle/spike-model.md"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
