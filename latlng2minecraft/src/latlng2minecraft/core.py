"""Core conversion logic for lat/lng <-> Minecraft coordinates.

This module exposes pure functions designed for TDD and later reuse by a CLI
and CSV I/O utilities. The conversion uses an affine transform derived from a
single base point for now, and is structured to allow extension to multi-point
calibration in the future.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from latlng2minecraft.types import LatLngPoint, MinecraftPoint, PointMap


@dataclass(frozen=True)
class AffineTransform:
    """Represents a simple affine mapping between two 2D spaces.

    This placeholder currently only supports translation using a single base
    correspondence. It can be extended to include scaling/rotation if the
    project later provides calibration from multiple reference points.
    """

    dx: float
    dy: float

    def apply_to_minecraft(self, point: MinecraftPoint) -> MinecraftPoint:
        return {"x": int(round(point["x"] + self.dx)), "y": int(round(point["y"] + self.dy))}

    def apply_to_latlng(self, point: LatLngPoint) -> LatLngPoint:
        return {"latitude": point["latitude"] + self.dy, "longitude": point["longitude"] + self.dx}


def build_translation_from_base(base: PointMap) -> AffineTransform:
    """Build a translation-only transform based on the provided base pair.

    The intent is to keep function signatures stable while actual math evolves.
    Currently, we treat the base as aligning origins and only allow translation
    deltas to be zero (identity). As calibration data expands, we can compute
    real deltas or full affine parameters.
    """

    # For now, identity transform; placeholders for future calibration.
    return AffineTransform(dx=0.0, dy=0.0)


def latlng_to_minecraft(point: LatLngPoint, base: PointMap) -> MinecraftPoint:
    """Convert a lat/lng point to a Minecraft coordinate.

    Current behavior returns the base minecraft coordinates as-is when the
    input equals the base lat/lng; otherwise, it returns a translated value
    using the current transform (identity for now).
    """

    transform = build_translation_from_base(base)
    if point == base["latlng"]:
        return base["minecraft"]
    # Identity until calibration rules are defined
    return transform.apply_to_minecraft(base["minecraft"])  # placeholder


def minecraft_to_latlng(point: MinecraftPoint, base: PointMap) -> LatLngPoint:
    """Convert a Minecraft coordinate to a lat/lng point.

    Mirrors the behavior of `latlng_to_minecraft` with identity transform.
    """

    transform = build_translation_from_base(base)
    if point == base["minecraft"]:
        return base["latlng"]
    return transform.apply_to_latlng(base["latlng"])  # placeholder


def bulk_latlng_to_minecraft(points: Iterable[LatLngPoint], base: PointMap) -> list[MinecraftPoint]:
    """Batch convert lat/lng points to Minecraft coordinates."""

    return [latlng_to_minecraft(p, base) for p in points]


def bulk_minecraft_to_latlng(points: Iterable[MinecraftPoint], base: PointMap) -> list[LatLngPoint]:
    """Batch convert Minecraft coordinates to lat/lng points."""

    return [minecraft_to_latlng(p, base) for p in points]


