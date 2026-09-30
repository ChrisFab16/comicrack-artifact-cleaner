"""Export FBCNN color weights to ONNX (T009).

Requires:
  - weights/fbcnn_color.pth (gitignored; from FBCNN release v1.0)
  - third_party/FBCNN clone (gitignored)

Usage:
  python harness/export_fbcnn_onnx.py
  python harness/export_fbcnn_onnx.py --weights weights/fbcnn_color.pth --out weights/fbcnn_color.onnx
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import torch
import torch.nn as nn


ROOT = Path(__file__).resolve().parents[1]
FBCNN_ROOT = ROOT / "third_party" / "FBCNN"


class BlindFbcnnWrapper(nn.Module):
    """ONNX-friendly wrapper: image in -> restored image + predicted QF (blind)."""

    def __init__(self, net: nn.Module):
        super().__init__()
        self.net = net

    def forward(self, x: torch.Tensor):
        return self.net(x, None)


class ManualFbcnnWrapper(nn.Module):
    """ONNX-friendly wrapper: image + qf_input [[1-QF/100]] -> restored + internal qf."""

    def __init__(self, net: nn.Module):
        super().__init__()
        self.net = net

    def forward(self, x: torch.Tensor, qf_input: torch.Tensor):
        return self.net(x, qf_input)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_color_net(weights: Path, device: torch.device) -> nn.Module:
    if str(FBCNN_ROOT) not in sys.path:
        sys.path.insert(0, str(FBCNN_ROOT))
    from models.network_fbcnn import FBCNN as Net

    model = Net(in_nc=3, out_nc=3, nc=[64, 128, 256, 512], nb=4, act_mode="R")
    state = torch.load(str(weights), map_location="cpu", weights_only=False)
    model.load_state_dict(state, strict=True)
    model.eval()
    for p in model.parameters():
        p.requires_grad_(False)
    return model.to(device)


def export_blind(model: nn.Module, out: Path, height: int, width: int, device: torch.device) -> None:
    wrapper = BlindFbcnnWrapper(model).to(device).eval()
    dummy = torch.randn(1, 3, height, width, device=device)
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        wrapper,
        dummy,
        str(out),
        input_names=["image"],
        output_names=["restored", "qf"],
        dynamic_axes={
            "image": {2: "height", 3: "width"},
            "restored": {2: "height", 3: "width"},
        },
        opset_version=17,
        do_constant_folding=True,
        dynamo=False,
    )


def export_manual(model: nn.Module, out: Path, height: int, width: int, device: torch.device) -> None:
    wrapper = ManualFbcnnWrapper(model).to(device).eval()
    dummy = torch.randn(1, 3, height, width, device=device)
    qf = torch.tensor([[0.5]], dtype=torch.float32, device=device)
    out.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        wrapper,
        (dummy, qf),
        str(out),
        input_names=["image", "qf_input"],
        output_names=["restored", "qf"],
        dynamic_axes={
            "image": {2: "height", 3: "width"},
            "restored": {2: "height", 3: "width"},
        },
        opset_version=17,
        do_constant_folding=True,
        dynamo=False,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Export FBCNN .pth to ONNX")
    p.add_argument("--weights", type=Path, default=ROOT / "weights" / "fbcnn_color.pth")
    p.add_argument("--out", type=Path, default=ROOT / "weights" / "fbcnn_color.onnx")
    p.add_argument("--out-manual", type=Path, default=ROOT / "weights" / "fbcnn_color_manual.onnx")
    p.add_argument("--height", type=int, default=256)
    p.add_argument("--width", type=int, default=256)
    p.add_argument("--skip-manual", action="store_true")
    p.add_argument("--device", default="cpu")
    args = p.parse_args(argv)

    if not FBCNN_ROOT.is_dir():
        print("Missing third_party/FBCNN — clone https://github.com/jiaxi-jiang/FBCNN", file=sys.stderr)
        return 1
    if not args.weights.is_file():
        print("Missing weights: {0}".format(args.weights), file=sys.stderr)
        return 1

    device = torch.device(args.device)
    print("Loading {0} (sha256={1})...".format(args.weights, sha256_file(args.weights)))
    net = load_color_net(args.weights, device)

    print("Exporting blind ONNX -> {0}".format(args.out))
    export_blind(net, args.out, args.height, args.width, device)
    print("  wrote {0} ({1} bytes) sha256={2}".format(args.out, args.out.stat().st_size, sha256_file(args.out)))

    if not args.skip_manual:
        print("Exporting manual-QF ONNX -> {0}".format(args.out_manual))
        export_manual(net, args.out_manual, args.height, args.width, device)
        print(
            "  wrote {0} ({1} bytes) sha256={2}".format(
                args.out_manual, args.out_manual.stat().st_size, sha256_file(args.out_manual)
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
