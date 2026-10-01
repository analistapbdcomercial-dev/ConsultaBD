from bson import ObjectId

from periodos import crear_filtro_periodo


def obtener_sucursales(db, zona_id):
    coleccion = db["sucursals"]
    candidatos = [
        {"zona": zona_id},
        {"zona": str(zona_id)},
        {"zone": zona_id},
        {"zone": str(zona_id)},
    ]
    documentos = []

    for filtro in candidatos:
        try:
            documentos.extend(coleccion.find(filtro))
        except Exception:
            pass

    unicos = {str(documento["_id"]): documento for documento in documentos if "_id" in documento}
    return list(unicos.values())


def buscar_documentos_por_ids(collection, campos, ids, periodo=None, campo_fecha=None):
    if not ids:
        return []

    ids_objectid = []
    ids_string = []
    for valor in ids:
        if isinstance(valor, ObjectId):
            ids_objectid.append(valor)
            ids_string.append(str(valor))
        elif isinstance(valor, str):
            ids_string.append(valor)
            if ObjectId.is_valid(valor):
                ids_objectid.append(ObjectId(valor))

    documentos = []
    for campo in campos:
        filtros = []
        if ids_objectid:
            filtros.append({campo: {"$in": ids_objectid}})
        if ids_string:
            filtros.append({campo: {"$in": ids_string}})

        for filtro in filtros:
            try:
                if periodo:
                    ids_filtro = next(iter(filtro.items()))
                    consulta = crear_filtro_periodo(
                        ids_filtro[0],
                        ids_filtro[1]["$in"],
                        periodo,
                        campo_fecha,
                    )
                    documentos.extend(collection.find(consulta))
                else:
                    documentos.extend(collection.find(filtro))
            except Exception:
                pass

    unicos = {}
    for documento in documentos:
        clave = str(documento["_id"]) if "_id" in documento else str(documento)
        unicos[clave] = documento
    return list(unicos.values())


def buscar_por_zona(collection, campos_zona, zona_id, periodo=None, campo_fecha=None):
    return buscar_documentos_por_ids(
        collection, campos_zona, [zona_id], periodo, campo_fecha
    )


def buscar_por_sucursal(
    collection,
    campos_sucursal,
    campos_sucursales,
    sucursal_ids,
    periodo=None,
    campo_fecha=None,
):
    documentos = []
    if campos_sucursal:
        documentos.extend(
            buscar_documentos_por_ids(
                collection, campos_sucursal, sucursal_ids, periodo, campo_fecha
            )
        )
    if campos_sucursales:
        documentos.extend(
            buscar_documentos_por_ids(
                collection, campos_sucursales, sucursal_ids, periodo, campo_fecha
            )
        )

    unicos = {}
    for documento in documentos:
        clave = str(documento["_id"]) if "_id" in documento else str(documento)
        unicos[clave] = documento
    return list(unicos.values())