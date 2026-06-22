"""Tests de la limpieza de datos.

La idea que se cuenta en la charla: el código de limpieza es donde más
errores silenciosos se cometen en ciencia de datos. Si la limpieza está
en funciones puras, se puede testear con DataFrames diminutos hechos a
mano, sin tocar el dataset real.

Ejecutar:  pytest
"""

import pandas as pd
import pytest

from airemad import clean


@pytest.fixture
def df_sucio() -> pd.DataFrame:
    """Mini-dataset con todos los problemas del dataset real."""
    return pd.DataFrame(
        {
            "FECHA": ["2025-01-01", "01/01/2025", "2025-06-15"],
            "ESTACION": ["PLAZA ELIPTICA", " Plaza Elíptica ", "Parque del Retiro"],
            "NO2": ["48,3", "48,3", "-999,0"],
            "PM25": ["12,1", "12,1", "8,4"],
            "MAGNITUD": ["ug/m3"] * 3,
        }
    )


def test_parse_fechas_unifica_formatos(df_sucio):
    out = clean.parse_fechas(df_sucio)
    assert pd.api.types.is_datetime64_any_dtype(out["FECHA"])
    assert out["FECHA"].iloc[0] == out["FECHA"].iloc[1] == pd.Timestamp("2025-01-01")


def test_parse_decimales_convierte_coma(df_sucio):
    out = clean.parse_decimales(df_sucio)
    assert out["NO2"].dtype == float
    assert out["NO2"].iloc[0] == pytest.approx(48.3)


def test_sentinel_se_convierte_en_nan(df_sucio):
    out = clean.parse_decimales(df_sucio).pipe(clean.sentinel_a_nan)
    assert out["NO2"].iloc[2] is pd.NA or pd.isna(out["NO2"].iloc[2])
    # Y los valores buenos siguen intactos:
    assert out["NO2"].iloc[0] == pytest.approx(48.3)


def test_normalizar_estaciones_unifica_variantes(df_sucio):
    out = clean.normalizar_estaciones(df_sucio)
    assert list(out["ESTACION"]) == ["Plaza Elíptica", "Plaza Elíptica", "Retiro"]


def test_normalizar_estaciones_falla_con_desconocidas():
    df = pd.DataFrame({"ESTACION": ["Mordor"]})
    with pytest.raises(ValueError, match="mordor"):
        clean.normalizar_estaciones(df)


def test_quitar_duplicados(df_sucio):
    out = clean.limpiar(df_sucio)
    # Las dos primeras filas eran la misma observación con formatos distintos
    assert len(out) == 2


def test_pipeline_completo_no_pierde_estaciones(df_sucio):
    out = clean.limpiar(df_sucio)
    assert set(out["ESTACION"]) == {"Plaza Elíptica", "Retiro"}
    assert out["FECHA"].is_monotonic_increasing or len(out["ESTACION"].unique()) > 1
