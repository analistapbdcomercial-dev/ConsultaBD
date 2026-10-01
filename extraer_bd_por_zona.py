import traceback
from datetime import datetime

from pymongo import MongoClient
from pymongo.errors import ConfigurationError

from configuracion import ARCHIVO_SALIDA, obtener_configuracion_mongodb
from esquema import cargar_customization, detectar_colecciones_relacionadas
from exportacion import exportar_excel
from extraccion import extraer_por_zonas
from periodos import seleccionar_periodo


def main():
    inicio = datetime.now()

    print("\n")
    print("=" * 80)
    print("EXTRACCIÓN DE BD - EL PECHUGÓN")
    print("=" * 80)

    periodo = seleccionar_periodo()
    mongodb_uri, mongodb_database = obtener_configuracion_mongodb()
    print("\nConectando a MongoDB...")
    cliente = MongoClient(mongodb_uri, serverSelectionTimeoutMS=30000)

    try:
        cliente.admin.command("ping")
        db = cliente[mongodb_database]
        print("Conexión OK")
        print(f"Base de datos: {mongodb_database}")

        colecciones_mongo = set(db.list_collection_names())
        print(f"Colecciones existentes en MongoDB: {len(colecciones_mongo)}")

        estructura = cargar_customization(db, colecciones_mongo)
        colecciones_relacionadas = detectar_colecciones_relacionadas(estructura)
        print(f"\nColecciones relacionadas detectadas: {len(colecciones_relacionadas)}")

        datos_por_coleccion, auditoria, resumen_zonas = extraer_por_zonas(
            db,
            colecciones_relacionadas,
            colecciones_mongo,
            periodo,
        )
        dfs = exportar_excel(
            datos_por_coleccion,
            auditoria,
            resumen_zonas,
            colecciones_relacionadas,
        )

        duracion = (datetime.now() - inicio).total_seconds()
        print("\n")
        print("=" * 80)
        print("EXTRACCIÓN TERMINADA")
        print("=" * 80)
        print(f"Archivo generado:\n{ARCHIVO_SALIDA}")
        print(f"\nColecciones exportadas: {len(dfs)}")
        print(f"Tiempo de ejecución: {duracion:.2f} segundos")
        print("\nRegistros por colección:")

        for nombre, df in dfs.items():
            print(f"  {nombre:<35}{len(df):>12,}")
    finally:
        cliente.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProceso cancelado por el usuario.")
    except ConfigurationError as error:
        if "DNS query name does not exist" in str(error):
            print("\nNo se pudo encontrar el host DNS de MongoDB.")
            print("Edita la variable MONGODB_URI en el archivo .env.")
            print("Copia la cadena completa desde MongoDB Atlas > Connect > Drivers.")
            print("Formato de referencia (reemplaza todos los valores entre < >):")
            print(
                "MONGODB_URI=mongodb+srv://<USUARIO>:<CONTRASENA>"
                "@<HOST_REAL>/?retryWrites=true&w=majority"
            )
        else:
            print(f"Error de configuración de MongoDB: {error}")
            traceback.print_exc()
    except Exception as error:
        print("\n")
        print("=" * 80)
        print("ERROR")
        print("=" * 80)
        print(f"\n{type(error).__name__}: {error}")
        print("\nDetalle:")
        traceback.print_exc()