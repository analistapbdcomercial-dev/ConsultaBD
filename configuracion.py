import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
ARCHIVO_CUSTOMIZATION = BASE_DIR / "pos_01_10_2026.customization"
ARCHIVO_SALIDA = BASE_DIR / "BD_EL_PECHUGON_POR_ZONA.xlsx"

ZONAS = {
    "Guadalajara JR": "5e1614c1b523a93887b0082e",
    "Villahermosa": "64bab15d097de32daa6a87ad",
    "Ciudad Juárez": "614cd0418027ef143f369fc8",
    "Oaxaca": "61719a6eae0ee10cf3e4662f",
    "Querétaro": "614cd02f8027ef143f369f96",
    "Tuxtla Gutierrez": "614ccfd88027ef143f369f30",
    "Aguascalientes": "614cd0218027ef143f369f95",
    "San Cristóbal": "614ccfeb8027ef143f369f4e",
}

# Override opcional: nombre visible o nombre MongoDB de colección -> campo fecha.
CAMPOS_FECHA_POR_COLECCION = {}


def obtener_configuracion_mongodb():
    load_dotenv()

    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_database = os.getenv("MONGODB_DATABASE")

    if not mongodb_uri:
        raise ValueError(
            "No se encontró MONGODB_URI.\n"
            "Crea un archivo .env con:\n"
            "MONGODB_URI=tu_conexion_mongodb"
        )

    if not mongodb_database:
        raise ValueError(
            "No se encontró MONGODB_DATABASE.\n"
            "Crea un archivo .env con:\n"
            "MONGODB_DATABASE=nombre_de_tu_base"
        )

    return mongodb_uri, mongodb_database