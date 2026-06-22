"""Limpieza del dataset de calidad del aire.

Cada función hace UNA cosa y devuelve un DataFrame nuevo (sin mutar
el de entrada). Eso las hace encadenables con ``.pipe()`` y, sobre
todo, testeables: ver ``tests/test_clean.py``.
"""

from __future__ import annotations

import unicodedata

import pandas as pd

SENTINEL = -999.0

# Mapa de variantes -> nombre canónico (tras normalizar)
ALIAS_ESTACIONES = {
    "pza. eliptica": "Plaza Elíptica",
    "plaza eliptica": "Plaza Elíptica",
    "escuelas aguirre": "Escuelas Aguirre",
    "plaza del carmen": "Plaza del Carmen",
    "casa de campo": "Casa de Campo",
    "retiro": "Retiro",
    "parque del retiro": "Retiro",
    "cuatro caminos": "Cuatro Caminos",
}


def _quitar_tildes(texto: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )


def parse_fechas(df: pd.DataFrame, col: str = "FECHA") -> pd.DataFrame:
    """Unifica los dos formatos de fecha (ISO y dd/mm/yyyy) en datetime."""
    df = df.copy()
    iso = pd.to_datetime(df[col], format="%Y-%m-%d", errors="coerce")
    esp = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")
    df[col] = iso.fillna(esp)
    return df


def parse_decimales(df: pd.DataFrame, cols: tuple[str, ...] = ("NO2", "PM25")) -> pd.DataFrame:
    """Convierte columnas con decimal-coma ('12,3') a float."""
    df = df.copy()
    for col in cols:
        df[col] = df[col].str.replace(",", ".", regex=False).astype(float)
    return df


def sentinel_a_nan(
    df: pd.DataFrame, cols: tuple[str, ...] = ("NO2", "PM25"), sentinel: float = SENTINEL
) -> pd.DataFrame:
    """Sustituye el valor centinela (-999) por NaN de verdad."""
    df = df.copy()
    for col in cols:
        df.loc[df[col] == sentinel, col] = pd.NA
        df[col] = df[col].astype("Float64")
    return df


def normalizar_estaciones(df: pd.DataFrame, col: str = "ESTACION") -> pd.DataFrame:
    """Unifica variantes de nombre: espacios, mayúsculas, tildes y alias."""
    df = df.copy()
    clave = (
        df[col]
        .str.strip()
        .str.lower()
        .map(_quitar_tildes)
    )
    df[col] = clave.map(ALIAS_ESTACIONES)
    sin_mapear = df[col].isna()
    if sin_mapear.any():
        desconocidas = sorted(clave[sin_mapear].unique())
        raise ValueError(f"Estaciones sin alias conocido: {desconocidas}")
    return df


def quitar_duplicados(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas duplicadas exactas (tras normalizar)."""
    return df.drop_duplicates(subset=["FECHA", "ESTACION"]).reset_index(drop=True)


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Pipeline completo de limpieza, en el orden correcto."""
    return (
        df
        .pipe(parse_fechas)
        .pipe(parse_decimales)
        .pipe(sentinel_a_nan)
        .pipe(normalizar_estaciones)
        .pipe(quitar_duplicados)
        .sort_values(["ESTACION", "FECHA"])
        .reset_index(drop=True)
    )
