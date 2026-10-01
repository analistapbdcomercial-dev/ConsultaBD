from datetime import date, datetime, time, timedelta, timezone


def _crear_periodo(fecha_inicio, fecha_fin):
    if fecha_inicio > fecha_fin:
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")

    return {
        "desde": datetime.combine(fecha_inicio, time.min, tzinfo=timezone.utc),
        "hasta": datetime.combine(fecha_fin + timedelta(days=1), time.min, tzinfo=timezone.utc),
    }


def crear_filtro_periodo(campo, ids, periodo, campo_fecha):
    filtro_ids = {campo: {"$in": ids}}
    desde = periodo["desde"]
    hasta = periodo["hasta"]
    filtro_fecha = {
        "$or": [
            {campo_fecha: {"$gte": desde, "$lt": hasta}},
            {
                campo_fecha: {
                    "$gte": desde.replace(tzinfo=None).isoformat(timespec="seconds"),
                    "$lt": hasta.replace(tzinfo=None).isoformat(timespec="seconds"),
                }
            },
        ]
    }
    return {"$and": [filtro_ids, filtro_fecha]}


def _leer_fecha_hora(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            return datetime.strptime(valor, "%Y-%m-%d %H:%M").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            print("Formato inválido. Usa AAAA-MM-DD HH:MM, por ejemplo 2026-09-21 00:00.")


def _crear_periodo_personalizado(inicio, fin_inclusivo):
    if inicio > fin_inclusivo:
        raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")

    return {
        "desde": inicio,
        "hasta": fin_inclusivo + timedelta(minutes=1),
    }


def seleccionar_periodo():
    print("\nPeríodo de consulta:")
    print("  1. Últimos 7 días")
    print("  2. Últimos 30 días")
    print("  3. Últimos 90 días")
    print("  4. Rango personalizado")
    print("  5. Todo el historial")

    while True:
        opcion = input("Selecciona una opción [1-5]: ").strip()
        if opcion in {"1", "2", "3"}:
            dias = {"1": 7, "2": 30, "3": 90}[opcion]
            hoy = datetime.now(timezone.utc).date()
            return _crear_periodo(hoy - timedelta(days=dias - 1), hoy)
        if opcion == "4":
            fecha_inicio = _leer_fecha_hora(
                "Fecha y hora inicial (AAAA-MM-DD HH:MM): "
            )
            fecha_fin = _leer_fecha_hora(
                "Fecha y hora final inclusiva (AAAA-MM-DD HH:MM): "
            )
            try:
                return _crear_periodo_personalizado(fecha_inicio, fecha_fin)
            except ValueError as error:
                print(error)
        elif opcion == "5":
            return None
        else:
            print("Opción inválida. Elige un número del 1 al 5.")