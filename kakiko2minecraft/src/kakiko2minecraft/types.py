"""kakiko2minecraft types."""

from __future__ import annotations

from typing import TypedDict


class MinecraftPoint(TypedDict):
    """Minecraft point."""

    x: int
    z: int


class LatLngPoint(TypedDict):
    """LatLng point."""

    latitude: float
    longitude: float


class PointMap(TypedDict):
    """Point map."""

    minecraft: MinecraftPoint
    latlng: LatLngPoint


class PointMapList(TypedDict):
    """Point map list."""

    points: list[PointMap]
