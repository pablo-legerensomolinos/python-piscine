# airemad — ¿Cuánto NO₂ nos regala el tráfico de Madrid?

Repositorio de la charla **"De Jupyter a producción: cómo se trabaja de verdad
con datos en Python"** (42 Madrid).

Analizamos datos de calidad del aire de Madrid (NO₂ y PM2.5 por estación de
medición) para responder una pregunta concreta: **¿cuánto contribuye el tráfico
a lo que respiramos?** Por el camino, el repo muestra cómo pasar de un notebook
caótico a un proyecto de datos profesional.

> Los datos de este repo son **sintéticos** (generados con
> `scripts/generate_sample_data.py`) pero imitan la estructura y los problemas
> reales de los datos abiertos del Ayuntamiento: https://datos.madrid.es

## Quickstart

```bash
git clone <este-repo> && cd charla-42-datos

# Base: venv + requirements.txt (funciona en cualquier máquina con Python):
python -m venv .venv
venv/bin/activate
pip install -r requirements.txt
pip install -e .                # instala el paquete airemad en modo editable
python scripts/generate_sample_data.py
python scripts/build_dataset.py
pytest -v
jupyter lab

# Alternativa: uv (https://docs.astral.sh/uv/) — mismo resultado, sin activar nada:
uv sync --all-extras
uv run python scripts/generate_sample_data.py
uv run python scripts/build_dataset.py
uv run pytest -v
uv run jupyter lab
```

## Estructura

```
.
├── data/
│   ├── raw/          # datos tal cual llegan: NO SE TOCAN nunca a mano
│   └── processed/    # datos limpios (generados, no commiteados)
├── notebooks/
│   ├── 01_eda_horrible.ipynb   # cómo NO hacerlo (punto de partida de la demo)
│   └── 02_eda_limpio.ipynb     # narrativa + resultados, la lógica vive en src/
├── src/airemad/      # el paquete: código importable, versionado y testeado
│   ├── load.py       # carga y guardado
│   ├── clean.py      # limpieza (funciones puras encadenables con .pipe)
│   └── plots.py      # gráficos
├── scripts/          # puntos de entrada ejecutables (pipeline, descarga)
├── tests/            # tests de la limpieza con pytest
├── figures/          # gráficos generados (no commiteados)
├── requirements.txt  # todas las dependencias (runtime + pytest, ruff, jupyterlab)
└── pyproject.toml    # metadata del paquete + configuración (ruff, pytest)
```

## Las ideas que cuenta este repo

**Los datos crudos son inmutables.** `data/raw/` es de solo lectura conceptual:
todo lo que les pase queda registrado en código, nunca en ediciones a mano.

**El notebook es para explorar y narrar, no para vivir.** En cuanto un trozo de
código se estabiliza, se muda a `src/` con nombre, docstring y test. El notebook
limpio (`02`) tiene ~10 líneas de código; el resto es historia.

**La limpieza se testea.** Es donde se cometen los errores más silenciosos y
caros de la ciencia de datos. Funciones puras + DataFrames diminutos hechos a
mano = tests rápidos que te salvan (ver `tests/test_clean.py`).

**Reproducibilidad o no pasó.** `requirements.txt` fija dependencias, el
pipeline (`generate_sample_data.py` + `build_dataset.py`) reconstruye todo
desde cero, y la historia de git cuenta cómo se llegó aquí
(`git log --oneline`).

## Datos reales

Para repetir el análisis con datos de verdad: portal de datos abiertos del
Ayuntamiento de Madrid (calidad del aire, tiempo real e histórico) en
https://datos.madrid.es — el dataset horario por estación y magnitud.
La interpretación de magnitudes y códigos de estación viene en su documento
de "Interpretación de datos". Spoiler: vienen aún más sucios que los de aquí.
