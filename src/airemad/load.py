"""Carga de datos crudos de calidad del aire."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# Raíz del proyecto: dos niveles por encima de este archivo (src/airemad/ -> raíz)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = PROJECT_ROOT / "data" / "raw" / "calidad_aire_madrid.csv"
PROCESSED_DATA = PROJECT_ROOT / "data" / "processed" / "calidad_aire_limpio.csv"


def load_raw(path: Path | str = RAW_DATA) -> pd.DataFrame:
    """Carga el CSV crudo tal cual viene de la fuente.

    El archivo usa ';' como separador y decimales con coma,
    así que las columnas numéricas llegan como texto. La limpieza
    se hace en :mod:`airemad.clean`, no aquí: una función, una tarea.
    """
    return pd.read_csv(path, sep=";", dtype=str)


def save_processed(df: pd.DataFrame, path: Path | str = PROCESSED_DATA) -> Path:
    """Guarda el dataset limpio en Parquet (tipado, comprimido, rápido)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path
