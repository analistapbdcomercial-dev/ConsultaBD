from bson import ObjectId

from configuracion import CAMPOS_FECHA_POR_COLECCION, ZONAS
from consultas_mongo import (
    buscar_por_sucursal,
    buscar_por_zona,
    obtener_sucursales,
)
from utilidades import agregar_metadatos, nombre_collection


def extraer_por_zonas(db, colecciones_relacionadas, colecciones_mongo, periodo=None):
    datos_por_coleccion = {}
    auditoria = []
    resumen_zonas = []

    for zona_nombre, zona_id_string in ZONAS.items():
        print("\n")
        print("-" * 80)
        print(f"ZONA: {zona_nombre}")
        print(f"ID:   {zona_id_string}")
        print("-" * 80)

        zona_id = ObjectId(zona_id_string)
        sucursales = obtener_sucursales(db, zona_id)
        sucursal_ids = [documento["_id"] for documento in sucursales if "_id" in documento]
        print(f"Sucursales encontradas: {len(sucursal_ids)}")

        if sucursales:
            datos_por_coleccion.setdefault("sucursals", []).extend(
                agregar_metadatos(sucursales, zona_nombre, zona_id_string, "pos.sucursals", "zona")
            )

        resumen_zona = {
            "Zona": zona_nombre,
            "Zona_ID": zona_id_string,
            "Sucursales": len(sucursal_ids),
        }

        for relacion in colecciones_relacionadas:
            namespace = relacion["coleccion"]
            collection_name = nombre_collection(namespace)
            campos_zona = relacion["campos_zona"]
            campos_sucursal = relacion["campos_sucursal"]
            campos_sucursales = relacion["campos_sucursales"]
            campo_fecha = (
                CAMPOS_FECHA_POR_COLECCION.get(namespace)
                or CAMPOS_FECHA_POR_COLECCION.get(collection_name)
                or next(iter(relacion.get("campos_fecha", [])), None)
            )

            if collection_name not in colecciones_mongo:
                continue

            if periodo and not campo_fecha:
                print(f"  {collection_name}: omitida, no se detectó un campo fecha")
                auditoria.append({
                    "Zona": zona_nombre,
                    "Zona_ID": zona_id_string,
                    "Coleccion": namespace,
                    "Campos_Zona": ", ".join(campos_zona),
                    "Campos_Sucursal": ", ".join(campos_sucursal),
                    "Campos_Sucursales": ", ".join(campos_sucursales),
                    "Campo_Fecha": "NO DETECTADO",
                    "Metodo": "OMITIDA: SIN CAMPO FECHA",
                    "Registros": 0,
                })
                resumen_zona[collection_name] = 0
                continue

            collection = db[collection_name]
            documentos = []
            metodo = None

            if campos_zona:
                docs_zona = buscar_por_zona(
                    collection, campos_zona, zona_id, periodo, campo_fecha
                )
                if docs_zona:
                    documentos.extend(docs_zona)
                    metodo = "zona"

            if sucursal_ids:
                docs_sucursal = buscar_por_sucursal(
                    collection,
                    campos_sucursal,
                    campos_sucursales,
                    sucursal_ids,
                    periodo,
                    campo_fecha,
                )
                if docs_sucursal:
                    documentos.extend(docs_sucursal)
                    metodo = f"{metodo}+sucursal" if metodo else "sucursal"

            unicos = {}
            for documento in documentos:
                clave = str(documento["_id"]) if "_id" in documento else str(documento)
                unicos[clave] = documento
            documentos = list(unicos.values())

            cantidad = len(documentos)
            resumen_zona[collection_name] = cantidad

            if documentos:
                datos = agregar_metadatos(documentos, zona_nombre, zona_id_string, namespace, metodo)
                datos_por_coleccion.setdefault(collection_name, []).extend(datos)

            auditoria.append({
                "Zona": zona_nombre,
                "Zona_ID": zona_id_string,
                "Coleccion": namespace,
                "Campos_Zona": ", ".join(campos_zona),
                "Campos_Sucursal": ", ".join(campos_sucursal),
                "Campos_Sucursales": ", ".join(campos_sucursales),
                "Campo_Fecha": campo_fecha or "",
                "Metodo": metodo or "SIN DATOS",
                "Registros": cantidad,
            })

            if cantidad > 0:
                print(f"  {collection_name:<35}{cantidad:>10} registros")

        resumen_zonas.append(resumen_zona)

    return datos_por_coleccion, auditoria, resumen_zonas