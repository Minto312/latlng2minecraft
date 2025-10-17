"""Coordinate conversion utilities between Minecraft and LatLng coordinates."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import LatLngPoint, MinecraftPoint

# 地球の楕円体パラメータ(WGS84)
EARTH_EQUATORIAL_RADIUS = 6378137.0  # 赤道半径(メートル)
EARTH_POLAR_RADIUS = 6356752.314245  # 極半径(メートル)
EARTH_ECCENTRICITY_SQUARED = 0.00669437999014  # 離心率の2乗


def latlng_to_minecraft(latlng: LatLngPoint, base_point: LatLngPoint) -> MinecraftPoint:
    """
    Convert LatLng coordinates to Minecraft coordinates.

    Args:
        latlng: Target LatLng point to convert
        base_point: Reference LatLng point (origin in Minecraft coordinates)

    Returns:
        Minecraft coordinates relative to base_point

    """
    lat_rad: float = math.radians(latlng["latitude"])
    base_lat_rad: float = math.radians(base_point["latitude"])

    # 緯度方向の距離計算(メートル)
    # より正確な子午線弧長の計算
    delta_lat_rad: float = lat_rad - base_lat_rad
    lat_distance: float = _meridional_arc_length(delta_lat_rad, base_lat_rad)

    # 経度方向の距離計算(メートル)
    # 緯度に依存する平行圏半径を使用
    parallel_radius: float = _parallel_radius(base_lat_rad)
    delta_lon_rad: float = math.radians(latlng["longitude"] - base_point["longitude"])
    lon_distance: float = parallel_radius * delta_lon_rad

    return {
        "x": round(lon_distance),  # 経度方向をx軸とする
        "y": round(lat_distance),  # 緯度方向をy軸とする
    }


def minecraft_to_latlng(minecraft: MinecraftPoint, base_point: LatLngPoint) -> LatLngPoint:
    """
    Convert Minecraft coordinates to LatLng coordinates.

    Args:
        minecraft: Minecraft coordinates relative to base_point
        base_point: Reference LatLng point (origin in Minecraft coordinates)

    Returns:
        LatLng coordinates

    """
    # 緯度の逆変換
    # メートルから緯度への変換(反復計算を使用)
    lat_distance: int = minecraft["y"]
    new_lat: float = _meters_to_latitude(lat_distance, base_point["latitude"])

    # 経度の変換
    # 緯度に依存する平行圏半径を使用
    parallel_radius: float = _parallel_radius(math.radians(new_lat))
    delta_lon_rad: float = minecraft["x"] / parallel_radius
    new_lon: float = base_point["longitude"] + math.degrees(delta_lon_rad)

    return {
        "latitude": new_lat,
        "longitude": new_lon,
    }


def _meridional_arc_length(delta_lat_rad: float, base_lat_rad: float) -> float:
    """
    Calculate meridional arc length for given latitude difference.

    Args:
        delta_lat_rad: Latitude difference in radians
        base_lat_rad: Base latitude in radians

    Returns:
        Arc length in meters

    """
    # 楕円体での子午線弧長の近似計算
    # より正確な計算には楕円積分が必要だが、ここでは簡略化

    # 平均緯度での曲率半径
    avg_lat_rad: float = base_lat_rad + delta_lat_rad / 2
    sin_lat: float = math.sin(avg_lat_rad)

    # 子午線曲率半径
    rho: float = (
        EARTH_EQUATORIAL_RADIUS
        * (1 - EARTH_ECCENTRICITY_SQUARED)
        / math.pow(1 - EARTH_ECCENTRICITY_SQUARED * sin_lat * sin_lat, 1.5)
    )

    return rho * delta_lat_rad


def _parallel_radius(lat_rad: float) -> float:
    """
    Calculate radius of parallel circle at given latitude.

    Args:
        lat_rad: Latitude in radians

    Returns:
        Parallel radius in meters

    """
    sin_lat: float = math.sin(lat_rad)
    return EARTH_EQUATORIAL_RADIUS * math.cos(lat_rad) / math.sqrt(1 - EARTH_ECCENTRICITY_SQUARED * sin_lat * sin_lat)


def _meters_to_latitude(meters: float, base_lat: float) -> float:
    """
    Convert meters to latitude using iterative method.

    Args:
        meters: Distance in meters (positive = north)
        base_lat: Base latitude in degrees

    Returns:
        New latitude in degrees

    """
    base_lat_rad: float = math.radians(base_lat)

    # 初期推定値(簡略化された計算)
    initial_delta_lat: float = meters / 111320.0  # 約111.32km per degree
    current_lat: float = base_lat + initial_delta_lat

    # 反復計算で精度を向上
    for _ in range(3):  # 3回の反復で十分な精度
        current_lat_rad: float = math.radians(current_lat)
        delta_lat_rad: float = current_lat_rad - base_lat_rad
        calculated_distance: float = _meridional_arc_length(delta_lat_rad, base_lat_rad)

        # 誤差を修正
        error: float = meters - calculated_distance
        lat_correction: float = error / 111320.0  # 簡略化された補正
        current_lat += lat_correction

    return current_lat
