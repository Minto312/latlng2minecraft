# latlng2minecraft

Tools for translating geodetic coordinates into Minecraft-friendly positions.

`latlng2minecraft` builds upon ideas from [plateau2minecraft](https://github.com/Project-PLATEAU/plateau2minecraft)
and focuses on the conversion logic required to keep real-world latitude/longitude data synchronized with
Minecraft Java Edition coordinates. The project bundles a small Python library together with a command line
utility so that you can script conversions or run them interactively.

## Features

- **Bidirectional conversion** – translate between WGS84 latitude/longitude and Minecraft X/Z (treated as X/Y) values.
- **Deterministic math** – conversion relies on WGS84 ellipsoid calculations, including meridional arc length and
  iterative latitude solving, to minimise accumulated error when mapping distances to blocks.
- **CLI utilities** – convert single coordinate pairs (`var` subcommand) or enrich CSV files with Minecraft columns.
- **Library-first design** – the `latlng2minecraft.converter` module can be embedded in other tooling or game
  automation scripts.

## Quick start

1. Ensure you have Python 3.8 or newer available.
2. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/<your-org>/latlng2minecraft.git
   cd latlng2minecraft/latlng2minecraft
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

   The project is also compatible with [Rye](https://rye-up.com/) – `rye sync` installs both runtime and development
   dependencies declared in `pyproject.toml`.

3. Verify the command line interface:

   ```bash
   latlng2minecraft var lat2mc 36.1389 139.3891
   ```

   The CLI prints a JSON object containing the converted Minecraft coordinates.

### CSV conversion example

Use the `csv` subcommand to enrich a CSV file that contains latitude/longitude columns. The tool appends
`minecraft_x` and `minecraft_y` columns using the same base point that the rest of the project employs.

```bash
latlng2minecraft csv input.csv output.csv --lat-col latitude --lng-col longitude
```

Rows with missing or invalid numeric values are copied with empty Minecraft coordinate columns so that downstream
systems can detect and handle the gaps.

### Library usage

You can access the conversion routines programmatically:

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

The `BASE_POINT_MAP` constant defines the relationship between a real-world origin and a Minecraft reference
point. You can supply your own base point if your world uses a different anchor.

## Development workflow

This repository uses [Ruff](https://docs.astral.sh/ruff/) for formatting (`ruff format`) and linting
(`ruff check --fix`). The recommended workflow is:

```bash
# Install development dependencies
rye sync  # or `pip install -e .[dev]` once equivalent extras are defined

# Format & lint
rye run format
rye run lint

# Run tests
rye run pytest
```

Running `pytest` without Rye works as well. Continuous integration expects that the formatter and lint checks pass
before changes are committed.

## License

This project is distributed under the terms of the [MIT License](LICENSE). Portions of the source originate from
[plateau2minecraft](https://github.com/Project-PLATEAU/plateau2minecraft) and retain their original licensing terms.
