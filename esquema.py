import json
from datetime import datetime

from configuracion import ARCHIVO_CUSTOMIZATION


CAMPOS_ZONA = {"zona", "zona_id", "zone", "zone_id"}
CAMPOS_SUCURSAL = {
    "sucursal",
    "sucursal_id",
    "sucursalId",
    "branch",
    "branch_id",
    "branchId",
}
CAMPOS_SUCURSALES = {"sucursales", "branches"}
CAMPOS_FECHA_COMUNES = (
    "fecha",
    "date",
    "fecha_venta",
    "fechaVenta",
    "sale_date",
    "saleDate",
    "fecha_registro",
    "fechaRegistro",
    "created_at",
    "createdAt",
    "creation_date",
    "creationDate",
    "updated_at",
    "updatedAt",
    "timestamp",
)


def cargar_customization(db=None, colecciones_mongo=None):
    print("\n" + "=" * 80)
    print("CARGANDO ESTRUCTURA DE BASE DE DATOS")
    print("=" * 80)

    if not ARCHIVO_CUSTOMIZATION.exists():
        if db is None or colecciones_mongo is None:
            raise FileNotFoundError(
                f"No se encontró:\n{ARCHIVO_CUSTOMIZATION}\n"
                "Conecta a MongoDB para inferir las colecciones automáticamente, "
                "o coloca el archivo en esa ruta."
            )

        print(
            f"No se encontró {ARCHIVO_CUSTOMIZATION.name}. "
            "Se inferirá el esquema con una muestra de MongoDB."
        )
        campos_relacion = CAMPOS_ZONA | CAMPOS_SUCURSAL | CAMPOS_SUCURSALES
        colecciones = {}

        for nombre in colecciones_mongo:
            propiedades = {}
            documentos = db[nombre].find({}, limit=50)

            for documento in documentos:
                for campo, valor in documento.items():
                    if campo in campos_relacion:
                        propiedades[campo] = {}
                    elif campo in CAMPOS_FECHA_COMUNES or isinstance(valor, datetime):
                        propiedades[campo] = {"bsonType": "date"}

            if propiedades:
                colecciones[nombre] = {
                    "jsonSchema": {"properties": propiedades}
                }

        estructura = {"collections": colecciones, "relationships": []}
        print(f"Colecciones inferidas: {len(colecciones)}")
        return estructura

    with open(ARCHIVO_CUSTOMIZATION, "r", encoding="utf-8") as archivo:
        estructura = json.load(archivo)

    colecciones = estructura.get("collections", {})
    relaciones = estructura.get("relationships", [])
    print(f"Colecciones encontradas: {len(colecciones)}")
    print(f"Relaciones encontradas: {len(relaciones)}")
    return estructura


def obtener_campos_schema(schema):
    try:
        properties = schema.get("jsonSchema", {}).get("properties", {})
        return set(properties.keys())
    except Exception:
        return set()


def obtener_campos_fecha(schema):
    properties = schema.get("jsonSchema", {}).get("properties", {})
    campos = [campo for campo in CAMPOS_FECHA_COMUNES if campo in properties]

    for campo, definicion in properties.items():
        if not isinstance(definicion, dict):
            continue
        tipo = definicion.get("bsonType", definicion.get("type"))
        tipos = tipo if isinstance(tipo, list) else [tipo]
        if "date" in tipos and campo not in campos:
            campos.append(campo)

    return campos


def detectar_colecciones_relacionadas(estructura):
    resultado = []
    for namespace, info in estructura.get("collections", {}).items():
        campos = obtener_campos_schema(info)
        campos_zona = sorted(campos.intersection(CAMPOS_ZONA))
        campos_sucursal = sorted(campos.intersection(CAMPOS_SUCURSAL))
        campos_sucursales = sorted(campos.intersection(CAMPOS_SUCURSALES))
        campos_fecha = obtener_campos_fecha(info)

        if campos_zona or campos_sucursal or campos_sucursales:
            resultado.append({
                "coleccion": namespace,
                "campos_zona": campos_zona,
                "campos_sucursal": campos_sucursal,
                "campos_sucursales": campos_sucursales,
                "campos_fecha": campos_fecha,
            })

    return resultado