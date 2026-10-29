"""Generador de datos simulados de la zona de demo (PB-004)."""

from .generar import build
from .zonas import ALCALDIAS, POLIGONOS

__all__ = ["ALCALDIAS", "POLIGONOS", "build"]
