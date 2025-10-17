"""Tests for coordinate conversion utilities."""

import math
import unittest

from latlng2minecraft.converter import (
    latlng_to_minecraft,
    minecraft_to_latlng,
)
from latlng2minecraft.types import LatLngPoint, MinecraftPoint


class TestLatLngToMinecraft(unittest.TestCase):
    """Test LatLng to Minecraft conversion."""

    def test_same_point_conversion(self):
        """Test conversion of the same point returns origin."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        result = latlng_to_minecraft(base_point, base_point)

        self.assertEqual(result["x"], 0)
        self.assertEqual(result["y"], 0)

    def test_north_movement(self):
        """Test conversion for north movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        target_point: LatLngPoint = {"latitude": 36.147755, "longitude": 139.388908}  # 0.009度北

        result = latlng_to_minecraft(target_point, base_point)

        # 約1000m北に移動（緯度1度≈111km）
        self.assertEqual(result["x"], 0)  # 経度方向の変化なし
        self.assertLess(abs(result["y"] - 1000), 50)  # 1000m付近（誤差50m以内）

    def test_east_movement(self):
        """Test conversion for east movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        target_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.397908}  # 0.009度東

        result = latlng_to_minecraft(target_point, base_point)

        # 約1000m東に移動（緯度36度付近での経度1度≈90km）
        self.assertLess(abs(result["x"] - 1000), 200)  # 1000m付近（誤差200m以内）
        self.assertEqual(result["y"], 0)  # 緯度方向の変化なし


class TestMinecraftToLatLng(unittest.TestCase):
    """Test Minecraft to LatLng conversion."""

    def test_origin_conversion(self):
        """Test conversion of origin returns base point."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 0, "y": 0}

        result = minecraft_to_latlng(minecraft, base_point)

        self.assertLess(abs(result["latitude"] - base_point["latitude"]), 1e-6)
        self.assertLess(abs(result["longitude"] - base_point["longitude"]), 1e-6)

    def test_round_trip_conversion(self):
        """Test round-trip conversion maintains precision."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        original_minecraft: MinecraftPoint = {"x": 500, "y": -300}

        # Minecraft -> LatLng -> Minecraft
        latlng = minecraft_to_latlng(original_minecraft, base_point)
        converted_minecraft = latlng_to_minecraft(latlng, base_point)

        self.assertLess(abs(converted_minecraft["x"] - original_minecraft["x"]), 1)
        self.assertLess(abs(converted_minecraft["y"] - original_minecraft["y"]), 1)


class TestConversionAccuracy(unittest.TestCase):
    """Test conversion accuracy with known distances."""

    def test_1000m_north_accuracy(self):
        """Test accuracy for 1000m north movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 0, "y": 1000}

        result = minecraft_to_latlng(minecraft, base_point)

        # 1000m北の移動は約0.009度の緯度変化
        expected_lat = base_point["latitude"] + 1000 / 111320.0  # 約111.32km per degree
        actual_lat_diff = result["latitude"] - base_point["latitude"]
        expected_lat_diff = expected_lat - base_point["latitude"]

        # 誤差は1%以内
        self.assertLess(abs(actual_lat_diff - expected_lat_diff) / expected_lat_diff, 0.01)

    def test_1000m_east_accuracy(self):
        """Test accuracy for 1000m east movement."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 1000, "y": 0}

        result = minecraft_to_latlng(minecraft, base_point)

        # 1000m東の移動は緯度に依存する経度変化
        base_lat_rad = math.radians(base_point["latitude"])
        parallel_radius = (
            6378137.0 * math.cos(base_lat_rad) / math.sqrt(1 - 0.00669437999014 * math.sin(base_lat_rad) ** 2)
        )
        expected_lon_diff = 1000 / parallel_radius * 180 / math.pi

        actual_lon_diff = result["longitude"] - base_point["longitude"]

        # 誤差は1%以内
        self.assertLess(abs(actual_lon_diff - expected_lon_diff) / expected_lon_diff, 0.01)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_negative_coordinates(self):
        """Test conversion with negative Minecraft coordinates."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": -500, "y": -300}

        result = minecraft_to_latlng(minecraft, base_point)

        # 南西に移動するので、緯度・経度ともに減少
        self.assertLess(result["latitude"], base_point["latitude"])
        self.assertLess(result["longitude"], base_point["longitude"])

    def test_large_coordinates(self):
        """Test conversion with large Minecraft coordinates."""
        base_point: LatLngPoint = {"latitude": 36.138755, "longitude": 139.388908}
        minecraft: MinecraftPoint = {"x": 10000, "y": 10000}

        result = minecraft_to_latlng(minecraft, base_point)

        # 大きな移動でも計算が正常に完了
        self.assertIsInstance(result["latitude"], float)
        self.assertIsInstance(result["longitude"], float)
        self.assertFalse(math.isnan(result["latitude"]))
        self.assertFalse(math.isnan(result["longitude"]))


if __name__ == "__main__":
    unittest.main()
