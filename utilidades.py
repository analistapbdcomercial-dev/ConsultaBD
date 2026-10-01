import re
from datetime import datetime

import pandas as pd
from bson import ObjectId


def convertir_objectid(valor):
    """Convierte un hexadecimal válido a ObjectId y conserva los demás valores."""
    if isinstance(valor, ObjectId):
        return valor

    if isinstance(valor, str):
        valor = valor.strip()
        if ObjectId.is_valid(valor):
            return ObjectId(valor)

    return valor


def convertir_recursivo(obj):
    """Convierte ObjectId anidados a texto para su exportación."""
    if isinstance(obj, ObjectId):
        return str(obj)

    if isinstance(obj, datetime):
        return obj

    if isinstance(obj, dict):
        return {str(clave): convertir_recursivo(valor) for clave, valor in obj.items()}

    if isinstance(obj, list):
        return [convertir_recursivo(valor) for valor in obj]

    return obj


def a_lista(valor):
    if valor is None:
        return []
    return valor if isinstance(valor, list) else [valor]


def nombre_hoja(nombre):
    nombre = re.sub(r'[\[\]:*?/\\]', "_", nombre)
    return nombre if len(nombre) <= 31 else nombre[:31]


def nombre_collection(namespace):
    return namespace.split(".", 1)[1] if "." in namespace else namespace


def agregar_metadatos(documentos, zona_nombre, zona_id, coleccion, metodo):
    salida = []
    for documento in documentos:
        nuevo = convertir_recursivo(documento)
        nuevo["_Zona"] = zona_nombre
        nuevo["_Zona_ID"] = str(zona_id)
        nuevo["_Coleccion"] = coleccion
        nuevo["_Metodo_Relacion"] = metodo
        salida.append(nuevo)
    return salida


def documentos_dataframe(documentos):
    if not documentos:
        return pd.DataFrame()

    documentos = [convertir_recursivo(documento) for documento in documentos]
    return pd.json_normalize(documentos, sep=".")