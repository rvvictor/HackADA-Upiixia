"""Entrada: `uv run python -m pipeline.geo` (determinista, semilla fija)."""

from __future__ import annotations

from .generar import build


def main() -> None:
    for nombre, ruta in build().items():
        print(f"{nombre}: {ruta}")


if __name__ == "__main__":
    main()
