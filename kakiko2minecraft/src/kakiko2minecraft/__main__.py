"""
Command-line interface for kakiko2minecraft.

Supports two modes initially:
- variable mode: compute using inline values (no I/O)
- CSV mode (scaffold): placeholders for future CSV input/output integration
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from kakiko2minecraft.consts import BASE_POINT_MAP
from kakiko2minecraft.converter import latlng_to_minecraft, minecraft_to_latlng

PAIR_VALUE_COUNT = 2

if TYPE_CHECKING:
    from kakiko2minecraft.types import LatLngPoint, MinecraftPoint


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="kakiko2minecraft", description="Convert between lat/lng and Minecraft coords"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    var = sub.add_parser("var", help="Compute conversion using inline variables")
    var.add_argument("mode", choices=["lat2mc", "mc2lat"], help="Conversion direction")
    var.add_argument("values", nargs="+", help="Values: lat lon OR x z (integers)")

    csvp = sub.add_parser("csv", help="CSV conversion: append minecraft_x/minecraft_z from lat/lng")
    csvp.add_argument("input", help="Input CSV path")
    csvp.add_argument("output", help="Output CSV path")
    csvp.add_argument("--lat-col", default="lat", help="Latitude column name (default: lat)")
    csvp.add_argument("--lng-col", default="lng", help="Longitude column name (default: lng)")

    return parser.parse_args(argv)


def handle_var(mode: str, values: list[str]) -> dict:
    """Convert inline values between LatLng and Minecraft coordinates."""
    if mode == "lat2mc":
        if len(values) != PAIR_VALUE_COUNT:
            message = "Expected 2 values: <latitude> <longitude>"
            raise SystemExit(message)
        lat, lon = float(values[0]), float(values[1])
        point: LatLngPoint = {"latitude": lat, "longitude": lon}
        # 1) 基準点(緯度経度)からの相対オフセット(メートル)に変換
        rel: MinecraftPoint = latlng_to_minecraft(point, BASE_POINT_MAP["latlng"])
        # 2) 変換後の単位(Minecraftメートル)を基準Minecraft座標に足し合わせて絶対座標に
        abs_x = BASE_POINT_MAP["minecraft"]["x"] + rel["x"]
        abs_z = BASE_POINT_MAP["minecraft"]["z"] + rel["z"]
        return {"x": abs_x, "z": abs_z}
    if len(values) != PAIR_VALUE_COUNT:
        message = "Expected 2 values: <x> <z>"
        raise SystemExit(message)
    x, z = int(values[0]), int(values[1])
    # 1) 入力Minecraft座標(絶対)から基準Minecraft座標を差し引いて相対オフセットへ
    rel_point: MinecraftPoint = {
        "x": x - BASE_POINT_MAP["minecraft"]["x"],
        "z": z - BASE_POINT_MAP["minecraft"]["z"],
    }
    # 2) 相対オフセット(メートル)を基準緯度経度に対して緯度経度へ変換(結果は絶対緯度経度)
    result: LatLngPoint = minecraft_to_latlng(rel_point, BASE_POINT_MAP["latlng"])
    return {"latitude": result["latitude"], "longitude": result["longitude"]}


def handle_csv(input_path: str, output_path: str, lat_col: str, lng_col: str) -> None:
    """Convert CSV rows by appending Minecraft coordinates."""
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open(newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = list(reader.fieldnames or [])
        if lat_col not in fieldnames or lng_col not in fieldnames:
            message = f"Missing required columns: {lat_col}, {lng_col}"
            raise SystemExit(message)

        # Prepare output columns
        out_fieldnames = fieldnames[:]
        if "minecraft_x" not in out_fieldnames:
            out_fieldnames.append("minecraft_x")
        if "minecraft_z" not in out_fieldnames:
            out_fieldnames.append("minecraft_z")

        with output_file.open("w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=out_fieldnames)
            writer.writeheader()

            for row in reader:
                try:
                    lat = float(row[lat_col])
                    lng = float(row[lng_col])
                except (KeyError, ValueError):
                    # Write row through with empty coords if invalid
                    row["minecraft_x"] = ""
                    row["minecraft_z"] = ""
                    writer.writerow(row)
                    continue

                rel = latlng_to_minecraft({"latitude": lat, "longitude": lng}, BASE_POINT_MAP["latlng"])
                abs_x = BASE_POINT_MAP["minecraft"]["x"] + rel["x"]
                abs_z = BASE_POINT_MAP["minecraft"]["z"] + rel["z"]
                row["minecraft_x"] = abs_x
                row["minecraft_z"] = abs_z
                writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the command-line interface."""
    ns = _parse_args(argv)
    if ns.command == "var":
        out = handle_var(ns.mode, ns.values)
        sys.stdout.write(json.dumps(out, ensure_ascii=False) + "\n")
        return 0
    if ns.command == "csv":
        handle_csv(ns.input, ns.output, ns.lat_col, ns.lng_col)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
