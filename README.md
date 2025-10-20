# latlng2minecraft

現実の測地座標を plateau2minecraft で生成された Minecraft ワールドの座標に変換するためのツールです。

また、このリポジトリに含まれる plateau2minecraft は一部改変し、生成された建物の下（と思われる座標）に草ブロックを置くようになっています。
必要であれば使ってください。

## 特長

- **双方向変換** – WGS84 の緯度経度と Minecraft の X/Z（内部的には X/Y として扱う）座標を双方向に変換します。
- **決定的な計算** – WGS84 楕円体に基づく子午線弧長の算出や反復法による緯度解法を用いて、ブロックへ距離をマッピングする際の累積誤差を抑えます。
- **CLI ユーティリティ** – 単一の座標ペアを変換する `var` サブコマンドや、CSV に Minecraft の列を追加するツールを提供します。
- **ライブラリ優先設計** – `latlng2minecraft.converter` モジュールを他のツールやゲーム自動化スクリプトに組み込めます。

## クイックスタート

1. Python 3.8 以降が利用可能であることを確認します。
2. リポジトリをクローンし、依存関係をインストールします。

   ```bash
   git clone https://github.com/<your-org>/latlng2minecraft.git
   cd latlng2minecraft/latlng2minecraft
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

   [Rye](https://rye-up.com/) にも対応しており、`rye sync` を実行すると `pyproject.toml` に記載された実行時・開発時の依存関係がまとめてインストールされます。

3. コマンドラインインターフェースを確認します。

   ```bash
   latlng2minecraft var lat2mc 36.1389 139.3891
   ```

   変換された Minecraft 座標を含む JSON オブジェクトが表示されます。

### CSV 変換例

緯度経度の列を含む CSV ファイルを `csv` サブコマンドで拡張できます。同じ基準点を使って `minecraft_x` と `minecraft_y` 列が追記されます。

```bash
latlng2minecraft csv input.csv output.csv --lat-col latitude --lng-col longitude
```

数値が欠けている、または不正な行は Minecraft 座標列が空のままコピーされるため、後段のシステムで欠損を検出しやすくなります。

### ライブラリとしての利用

変換ルーチンはコードから直接呼び出せます。

```python
from latlng2minecraft.consts import BASE_POINT_MAP
from latlng2minecraft.converter import latlng_to_minecraft

relative = latlng_to_minecraft(
    {"latitude": 36.138755, "longitude": 139.388908},
    BASE_POINT_MAP["latlng"],
)
absolute = {
    "x": BASE_POINT_MAP["minecraft"]["x"] + relative["x"],
    "y": BASE_POINT_MAP["minecraft"]["y"] + relative["y"],
}
print(absolute)
```

`BASE_POINT_MAP` 定数は、現実世界の原点と Minecraft の参照点との対応関係を定義します。ワールドで異なるアンカーを用いる場合は、独自の基準点を指定してください。

## 開発フロー

このリポジトリでは [Ruff](https://docs.astral.sh/ruff/) をフォーマッタ（`ruff format`）兼リンタ（`ruff check --fix`）として利用します。推奨されるワークフローは次のとおりです。

```bash
# 開発用依存関係のインストール
rye sync  # 同等の extras を用意した場合は `pip install -e .[dev]` でも可

# フォーマットと lint
rye run format
rye run lint

# テスト実行
rye run pytest
```

Rye を使わずに `pytest` を直接実行しても構いません。コミット前にフォーマッタと lint のチェックが通ることを継続的インテグレーションでも期待しています。

## ライセンス

本プロジェクトは [MIT License](LICENSE) の下で配布されています。一部のソースコードは [plateau2minecraft](https://github.com/Project-PLATEAU/plateau2minecraft) から継承しており、元のライセンス条項に従います。
