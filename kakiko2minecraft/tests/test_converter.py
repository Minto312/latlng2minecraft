"""Tests for coordinate conversion utilities."""

import math
import unittest
from typing import TYPE_CHECKING

from kakiko2minecraft.converter import (
    latlng_to_minecraft,
    minecraft_to_latlng,
)

if TYPE_CHECKING:
    from kakiko2minecraft.types import LatLngPoint, MinecraftPoint


TOL_NORTH_METERS = 50
TOL_EAST_METERS = 200
EPSILON = 1e-6
PERCENT_TOL = 0.01


class TestLatLngToMinecraft(unittest.TestCase):
    """Test LatLng to Minecraft conversion."""

    def test_same_point_conversion(self) -> None:
        """Test conversion of the same point returns origin."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        result: MinecraftPoint = latlng_to_minecraft(base_point, base_point)

        assert result["x"] == 0
        assert result["z"] == 0

    def test_north_movement(self) -> None:
        """Test conversion for north movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        target_point: LatLngPoint = {"latitude": 36.147755, "longitude": 139.388908}  # 0.009度北

        result: MinecraftPoint = latlng_to_minecraft(target_point, base_point)

        # 約1000m北に移動(緯度1度≈111km)
        assert result["x"] == 0  # 経度方向の変化なし
        assert abs(result["z"] - 1000) < TOL_NORTH_METERS  # 1000m付近(誤差50m以内)

    def test_east_movement(self) -> None:
        """Test conversion for east movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        target_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.397908}  # 0.009度東

        result: MinecraftPoint = latlng_to_minecraft(target_point, base_point)

        # 約1000m東に移動(緯度36度付近での経度1度≈90km)
        assert abs(result["x"] - 1000) < TOL_EAST_METERS  # 1000m付近(誤差200m以内)
        assert result["z"] == 0  # 緯度方向の変化なし


class TestMinecraftToLatLng(unittest.TestCase):
    """Test Minecraft to LatLng conversion."""

    def test_origin_conversion(self) -> None:
        """Test conversion of origin returns base point."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 0, "z": 0}

        result: LatLngPoint = minecraft_to_latlng(minecraft, base_point)

        assert abs(result["latitude"] - base_point["latitude"]) < EPSILON
        assert abs(result["longitude"] - base_point["longitude"]) < EPSILON

    def test_round_trip_conversion(self) -> None:
        """Test round-trip conversion maintains precision."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        original_minecraft: MinecraftPoint = {"x": 500, "z": -300}

        # Minecraft -> LatLng -> Minecraft
        latlng: LatLngPoint = minecraft_to_latlng(original_minecraft, base_point)
        converted_minecraft: MinecraftPoint = latlng_to_minecraft(latlng, base_point)

        assert abs(converted_minecraft["x"] - original_minecraft["x"]) < 1
        assert abs(converted_minecraft["z"] - original_minecraft["z"]) < 1


class TestConversionAccuracy(unittest.TestCase):
    """Test conversion accuracy with known distances."""

    def test_1000m_north_accuracy(self) -> None:
        """Test accuracy for 1000m north movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 0, "z": 1000}

        result: LatLngPoint = minecraft_to_latlng(minecraft, base_point)

        # 1000m北の移動は約0.009度の緯度変化
        expected_lat: float = base_point["latitude"] + 1000 / 111320.0  # 約111.32km per degree
        actual_lat_diff: float = result["latitude"] - base_point["latitude"]
        expected_lat_diff: float = expected_lat - base_point["latitude"]

        # 誤差は1%以内
        assert abs(actual_lat_diff - expected_lat_diff) / expected_lat_diff < PERCENT_TOL

    def test_1000m_east_accuracy(self) -> None:
        """Test accuracy for 1000m east movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 1000, "z": 0}

        result: LatLngPoint = minecraft_to_latlng(minecraft, base_point)

        # 1000m東の移動は緯度に依存する経度変化
        base_lat_rad: float = math.radians(base_point["latitude"])
        parallel_radius: float = (
            6378137.0 * math.cos(base_lat_rad) / math.sqrt(1 - 0.00669437999014 * math.sin(base_lat_rad) ** 2)
        )
        expected_lon_diff: float = 1000 / parallel_radius * 180 / math.pi

        actual_lon_diff: float = result["longitude"] - base_point["longitude"]

        # 誤差は1%以内
        assert abs(actual_lon_diff - expected_lon_diff) / expected_lon_diff < PERCENT_TOL


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_negative_coordinates(self) -> None:
        """Test conversion with negative Minecraft coordinates."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": -500, "z": -300}

        result: LatLngPoint = minecraft_to_latlng(minecraft, base_point)

        # 南西に移動するので、緯度・経度ともに減少
        assert result["latitude"] < base_point["latitude"]
        assert result["longitude"] < base_point["longitude"]

    def test_large_coordinates(self) -> None:
        """Test conversion with large Minecraft coordinates."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 10000, "z": 10000}

        result: LatLngPoint = minecraft_to_latlng(minecraft, base_point)

        # 大きな移動でも計算が正常に完了
        assert isinstance(result["latitude"], float)
        assert isinstance(result["longitude"], float)
        assert not math.isnan(result["latitude"])
        assert not math.isnan(result["longitude"])


if __name__ == "__main__":
    unittest.main()
