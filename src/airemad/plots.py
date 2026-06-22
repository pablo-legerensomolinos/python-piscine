"""Gráficos del análisis de calidad del aire."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

LIMITE_OMS_NO2 = 10  # guía anual OMS 2021 (µg/m³)
LIMITE_UE_NO2 = 40   # límite anual UE (µg/m³)


def serie_mensual_no2(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """Media mensual de NO2 por estación, con los límites de referencia."""
    if ax is None:
        _, ax = plt.subplots(figsize=(11, 5))

    mensual = (
        df.set_index("FECHA")
        .groupby("ESTACION")["NO2"]
        .resample("ME")
        .mean()
        .reset_index()
    )
    for estacion, grupo in mensual.groupby("ESTACION"):
        ax.plot(grupo["FECHA"], grupo["NO2"], marker="o", markersize=3, label=estacion)

    ax.axhline(LIMITE_UE_NO2, color="firebrick", ls="--", lw=1, label="Límite UE (40)")
    ax.axhline(LIMITE_OMS_NO2, color="gray", ls=":", lw=1, label="Guía OMS (10)")
    ax.set_ylabel("NO₂ (µg/m³, media mensual)")
    ax.set_title("NO₂ en Madrid por estación de medición")
    ax.legend(fontsize=8, ncols=2)
    ax.spines[["top", "right"]].set_visible(False)
    return ax


def comparativa_semana_finde(df: pd.DataFrame, ax: plt.Axes | None = None) -> plt.Axes:
    """¿Cuánto baja el NO2 el fin de semana? (proxy del efecto del tráfico)."""
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 5))

    tmp = df.copy()
    tmp["tipo_dia"] = tmp["FECHA"].dt.dayofweek.map(lambda d: "Finde" if d >= 5 else "Laborable")
    medias = tmp.groupby(["ESTACION", "tipo_dia"])["NO2"].mean().unstack()
    medias["caida_%"] = 100 * (1 - medias["Finde"] / medias["Laborable"])
    medias = medias.sort_values("caida_%")

    medias[["Laborable", "Finde"]].plot.barh(ax=ax, color=["#444444", "#e07b39"])
    ax.set_xlabel("NO₂ medio (µg/m³)")
    ax.set_title("NO₂: laborable vs fin de semana (el tráfico, en una imagen)")
    ax.spines[["top", "right"]].set_visible(False)
    return ax


def guardar(fig: plt.Figure, nombre: str, carpeta: Path | str = "figures") -> Path:
    """Guarda una figura en la carpeta de salida con calidad decente."""
    carpeta = Path(carpeta)
    carpeta.mkdir(exist_ok=True)
    destino = carpeta / f"{nombre}.png"
    fig.savefig(destino, dpi=150, bbox_inches="tight")
    return destino
