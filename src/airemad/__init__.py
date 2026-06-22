"""airemad: análisis de calidad del aire en Madrid."""

from airemad.clean import limpiar
from airemad.load import load_raw, save_processed

__all__ = ["load_raw", "save_processed", "limpiar"]
__version__ = "0.1.0"
