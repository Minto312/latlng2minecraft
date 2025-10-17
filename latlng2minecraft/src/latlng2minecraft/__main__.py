"""Command-line interface for latlng2minecraft.

Supports two modes initially:
- variable mode: compute using inline values (no I/O)
- CSV mode (scaffold): placeholders for future CSV input/output integration
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from latlng2minecraft.consts import BASE_POINT_MAP
from latlng2minecraft.converter import latlng_to_minecraft, minecraft_to_latlng
from latlng2minecraft.types import LatLngPoint, MinecraftPoint


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="latlng2minecraft", description="Convert between lat/lng and Minecraft coords")

    sub = parser.add_subparsers(dest="command", required=True)

    var = sub.add_parser("var", help="Compute conversion using inline variables")
    var.add_argument("mode", choices=["lat2mc", "mc2lat"], help="Conversion direction")
    var.add_argument("values", nargs="+", help="Values: lat lon OR x y (integers)")

    csvp = sub.add_parser("csv", help="CSV conversion (scaffold)")
    csvp.add_argument("input", help="Input CSV path")
    csvp.add_argument("output", help="Output CSV path")
    csvp.add_argument("--direction", choices=["lat2mc", "mc2lat"], default="lat2mc")

    return parser.parse_args(argv)


def handle_var(mode: str, values: list[str]) -> dict:
    if mode == "lat2mc":
        if len(values) != 2:
            raise SystemExit("Expected 2 values: <latitude> <longitude>")
        lat, lon = float(values[0]), float(values[1])
        point: LatLngPoint = {"latitude": lat, "longitude": lon}
        # Use lat/lng base point for relative conversion
        result: MinecraftPoint = latlng_to_minecraft(point, BASE_POINT_MAP["latlng"])
        return {"x": result["x"], "y": result["y"]}
    else:
        if len(values) != 2:
            raise SystemExit("Expected 2 values: <x> <y>")
        x, y = int(values[0]), int(values[1])
        point: MinecraftPoint = {"x": x, "y": y}
        # Use lat/lng base point for relative conversion
        result: LatLngPoint = minecraft_to_latlng(point, BASE_POINT_MAP["latlng"])
        return {"latitude": result["latitude"], "longitude": result["longitude"]}


def handle_csv(input_path: str, output_path: str, direction: str) -> None:
    # Placeholder for future CSV I/O; keeps interface stable for later work.
    raise SystemExit("CSV mode not implemented yet. This is a scaffold for future work.")


def main(argv: Optional[list[str]] = None) -> int:
    ns = _parse_args(argv)
    if ns.command == "var":
        out = handle_var(ns.mode, ns.values)
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
        return 0
    if ns.command == "csv":
        handle_csv(ns.input, ns.output, ns.direction)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())


