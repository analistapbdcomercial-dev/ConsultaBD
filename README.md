EXTRACCIÓN COMPLETA DE INFORMACIÓN POR ZONA 

 Objetivo:
   1. Conectarse a MongoDB
   2. Tomar los 8 IDs de zona
   3. Encontrar las sucursales pertenecientes a cada zona
   4. Buscar información relacionada mediante:
        - zona
        - zona_id
        - zone
        - sucursal
        - sucursal_id
        - sucursales
        - branch
        - branch_id
   5. Leer la estructura .customization para descubrir colecciones
   6. Generar un Excel con información separada por colección
   7. Generar hojas de auditoría y resumen

Estructura del proyecto:
     - extraer_bd_por_zona.py: punto de entrada y coordinación del proceso
     - configuracion.py: rutas, zonas y variables de conexión
     - esquema.py: lectura de la estructura .customization
     - consultas_mongo.py: consultas a MongoDB
     - extraccion.py: procesamiento de documentos por zona
     - utilidades.py: conversiones y funciones compartidas
     - exportacion.py: creación y formato del archivo Excel

Para ejecutar la extracción, configura MONGODB_URI y MONGODB_DATABASE en un
archivo .env y ejecuta:

     python extraer_bd_por_zona.py

Si aparece un error DNS, revisa MONGODB_URI: pega la cadena completa de MongoDB
Atlas > Connect > Drivers y reemplaza todos los marcadores de usuario,
contraseña y host. 

Al iniciar, el programa permite elegir los últimos 7, 30 o 90 días, un rango
personalizado (AAAA-MM-DD HH:MM) o todo el historial. La hora final del rango
personalizado es inclusiva hasta el final de ese minuto. Los campos fecha se detectan
desde el esquema usando nombres comunes; para indicar otro nombre, agrega la
colección y su campo en CAMPOS_FECHA_POR_COLECCION dentro de configuracion.py.
Si falta el archivo .customization, el programa intenta inferir las colecciones
relacionadas muestreando hasta 50 documentos por colección en MongoDB.
Si se elige un período y una colección no tiene un campo fecha reconocible, se
omite y queda indicada en la hoja Auditoria. La colección de sucursales se
mantiene completa para poder relacionar los registros.# ConsultaBD
