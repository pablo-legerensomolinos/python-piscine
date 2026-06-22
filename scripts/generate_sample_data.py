"""Genera un dataset sintético (pero realista) de calidad del aire en Madrid.

El dataset imita los datos abiertos del Ayuntamiento de Madrid
(https://datos.madrid.es) pero con "suciedad" añadida a propósito
para la demo de limpieza de datos:

- Decimales con coma (formato español) -> la columna llega como texto
- Valores centinela -999 en lugar de NaN
- Filas duplicadas
- Nombres de estación inconsistentes (mayúsculas, espacios, tildes)
- Fechas en dos formatos distintos

Uso:
    python scripts/generate_sample_data.py
"""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
RAW_PATH = Path(__file__).resolve().parents[1] / "data" / "raw" / "calidad_aire_madrid.csv"

ESTACIONES = {
    "Plaza Elíptica": {"base_no2": 48, "trafico": 1.00},
    "Escuelas Aguirre": {"base_no2": 42, "trafico": 0.90},
    "Plaza del Carmen": {"base_no2": 35, "trafico": 0.75},
    "Casa de Campo": {"base_no2": 18, "trafico": 0.30},
    "Retiro": {"base_no2": 22, "trafico": 0.40},
    "Cuatro Caminos": {"base_no2": 40, "trafico": 0.85},
}

# Variantes "sucias" del nombre de cada estación
VARIANTES = {
    "Plaza Elíptica": ["Plaza Elíptica", "PLAZA ELIPTICA", "Pza. Elíptica", " Plaza Elíptica "],
    "Escuelas Aguirre": ["Escuelas Aguirre", "ESCUELAS AGUIRRE", "escuelas aguirre"],
    "Plaza del Carmen": ["Plaza del Carmen", "PLAZA DEL CARMEN", "Plaza del Carmen "],
    "Casa de Campo": ["Casa de Campo", "CASA DE CAMPO", "casa de campo"],
    "Retiro": ["Retiro", "RETIRO", "Parque del Retiro"],
    "Cuatro Caminos": ["Cuatro Caminos", "CUATRO CAMINOS", "cuatro caminos "],
}


def main() -> None:
    rng = np.random.default_rng(SEED)
    random.seed(SEED)

    fechas = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    filas = []

    for fecha in fechas:
        # Estacionalidad: más NO2 en invierno (calefacciones + inversión térmica)
        factor_estacional = 1.0 + 0.35 * np.cos(2 * np.pi * (fecha.dayofyear - 15) / 365)
        # Menos tráfico en fin de semana
        factor_semana = 0.70 if fecha.dayofweek >= 5 else 1.0

        for nombre, params in ESTACIONES.items():
            no2 = (
                params["base_no2"]
                * factor_estacional
                * (1 - (1 - factor_semana) * params["trafico"])
                + rng.normal(0, 6)
            )
            no2 = max(no2, 2.0)

            pm25 = max(params["base_no2"] * 0.28 * factor_estacional + rng.normal(0, 2.5), 1.0)

            # --- suciedad deliberada ---
            estacion = random.choice(VARIANTES[nombre])

            # ~3% de valores perdidos como centinela -999
            if rng.random() < 0.03:
                no2 = -999.0
            if rng.random() < 0.02:
                pm25 = -999.0

            # Decimal con coma (formato español) -> columna de texto
            no2_str = f"{no2:.1f}".replace(".", ",")
            pm25_str = f"{pm25:.1f}".replace(".", ",")

            # Dos formatos de fecha mezclados
            if rng.random() < 0.25:
                fecha_str = fecha.strftime("%d/%m/%Y")
            else:
                fecha_str = fecha.strftime("%Y-%m-%d")

            filas.append(
                {
                    "FECHA": fecha_str,
                    "ESTACION": estacion,
                    "NO2": no2_str,
                    "PM25": pm25_str,
                    "MAGNITUD": "ug/m3",
                }
            )

    df = pd.DataFrame(filas)

    # ~1% de filas duplicadas
    duplicadas = df.sample(frac=0.01, random_state=SEED)
    df = pd.concat([df, duplicadas]).sample(frac=1, random_state=SEED).reset_index(drop=True)

    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_PATH, index=False, sep=";")
    print(f"Dataset generado: {RAW_PATH} ({len(df)} filas)")


if __name__ == "__main__":
    main()
