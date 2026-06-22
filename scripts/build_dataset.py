"""Pipeline: datos crudos -> dataset limpio en data/processed/.

Este script es el "punto de entrada" reproducible del proyecto:
cualquiera que clone el repo puede ejecutar `make data` y obtener
exactamente el mismo dataset procesado.
"""

from airemad import limpiar, load_raw, save_processed


def main() -> None:
    crudo = load_raw()
    print(f"Crudo:  {len(crudo):>5} filas | columnas: {list(crudo.columns)}")

    limpio = limpiar(crudo)
    print(f"Limpio: {len(limpio):>5} filas | nulos NO2: {limpio['NO2'].isna().sum()}")

    destino = save_processed(limpio)
    print(f"Guardado en {destino}")


if __name__ == "__main__":
    main()
