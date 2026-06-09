from flask import Blueprint, render_template, request
from db import get_connection

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/reportes')
def menu_reportes():
    conn = None
    cur = None

    asociados_reporte = []
    extracto_reporte = []
    pagos_reporte = []
    mora_reporte = []
    cartera_reporte = []
    productividad_reporte = []
    codeudora_reporte = []

    saldo_extracto = 0

    try:
        conn = get_connection()
        cur = conn.cursor()

        reporte = request.args.get('reporte', 'asociados')

        # -------------------------------
        # 1. LISTADO DE ASOCIADOS
        # -------------------------------
        if reporte == 'asociados':
            estado = request.args.get('estado')
            tipo = request.args.get('tipo')

            consulta = """
                SELECT
                    a.cedula,
                    a.nombre || ' ' || a.apellido AS nombre_completo,
                    CASE
                        WHEN f.cedula IS NOT NULL THEN 'Fundador'
                        ELSE 'Asociado'
                    END AS tipo_asociado,
                    a.fecha_afiliacion,
                    (
                        COALESCE((
                            SELECT COUNT(*)
                            FROM cuenta_ahorro ca
                            WHERE ca.cedula_asociado = a.cedula
                        ), 0)
                        +
                        COALESCE((
                            SELECT COUNT(*)
                            FROM credito c
                            WHERE c.cedula_asociado = a.cedula
                        ), 0)
                    ) AS productos_activos,
                    a.estado
                FROM asociado a
                LEFT JOIN fundador f
                    ON a.cedula = f.cedula
                WHERE 1 = 1
            """

            params = []

            if estado:
                consulta += " AND a.estado = %s"
                params.append(estado)

            if tipo == 'fundador':
                consulta += " AND f.cedula IS NOT NULL"
            elif tipo == 'normal':
                consulta += " AND f.cedula IS NULL"

            consulta += " ORDER BY a.apellido, a.nombre"

            cur.execute(consulta, params)
            resultados = cur.fetchall()

            for fila in resultados:
                asociados_reporte.append({
                    'cedula': fila[0],
                    'nombre': fila[1],
                    'tipo': fila[2],
                    'fecha_afiliacion': fila[3],
                    'productos': fila[4],
                    'estado': fila[5]
                })

        # -------------------------------
        # 2. EXTRACTO DE CUENTA
        # -------------------------------
        elif reporte == 'extracto':
            numero_cuenta = request.args.get('numero_cuenta')
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            canal = request.args.get('canal')
            tipo_movimiento = request.args.get('tipo_movimiento')

            if numero_cuenta:
                consulta = """
                    SELECT
                        m.id_transaccion,
                        m.fecha_hora,
                        m.tipo,
                        m.valor,
                        m.canal,
                        m.numero_cuenta
                    FROM movimiento m
                    WHERE m.numero_cuenta = %s
                """

                params = [numero_cuenta]

                if fecha_inicio:
                    consulta += " AND DATE(m.fecha_hora) >= %s"
                    params.append(fecha_inicio)

                if fecha_fin:
                    consulta += " AND DATE(m.fecha_hora) <= %s"
                    params.append(fecha_fin)

                if canal:
                    consulta += " AND m.canal = %s"
                    params.append(canal)

                if tipo_movimiento:
                    consulta += " AND m.tipo = %s"
                    params.append(tipo_movimiento)

                consulta += " ORDER BY m.fecha_hora DESC"

                cur.execute(consulta, params)
                resultados = cur.fetchall()

                for fila in resultados:
                    extracto_reporte.append({
                        'id_transaccion': fila[0],
                        'fecha_hora': fila[1],
                        'tipo': fila[2],
                        'valor': fila[3],
                        'canal': fila[4],
                        'numero_cuenta': fila[5]
                    })

                consulta_saldo = """
                    SELECT COALESCE(SUM(
                        CASE
                            WHEN tipo IN ('deposito', 'transferencia_entrante') THEN valor
                            WHEN tipo IN ('retiro', 'transferencia_saliente') THEN -valor
                            ELSE 0
                        END
                    ), 0)
                    FROM movimiento
                    WHERE numero_cuenta = %s
                """

                params_saldo = [numero_cuenta]

                if fecha_inicio:
                    consulta_saldo += " AND DATE(fecha_hora) >= %s"
                    params_saldo.append(fecha_inicio)

                if fecha_fin:
                    consulta_saldo += " AND DATE(fecha_hora) <= %s"
                    params_saldo.append(fecha_fin)

                if canal:
                    consulta_saldo += " AND canal = %s"
                    params_saldo.append(canal)

                if tipo_movimiento:
                    consulta_saldo += " AND tipo = %s"
                    params_saldo.append(tipo_movimiento)

                cur.execute(consulta_saldo, params_saldo)
                saldo_extracto = cur.fetchone()[0]

        # -------------------------------
        # 3. HISTORIAL DE PAGOS DE CRÉDITO
        # -------------------------------
        elif reporte == 'pagos':
            numero_credito = request.args.get('numero_credito')

            if numero_credito:
                consulta = """
                    SELECT
                        pc.numero_radicado,
                        pc.numero_cuota,
                        pc.fecha_pago,
                        pc.valor_pagado,
                        pc.estado
                    FROM pago_cuota pc
                    WHERE pc.numero_radicado = %s
                    ORDER BY pc.numero_cuota
                """

                cur.execute(consulta, [numero_credito])
                resultados = cur.fetchall()

                for fila in resultados:
                    pagos_reporte.append({
                        'numero_radicado': fila[0],
                        'numero_cuota': fila[1],
                        'fecha_pago': fila[2],
                        'valor_pagado': fila[3],
                        'estado': fila[4]
                    })

        # -------------------------------
        # 4. ASOCIADOS EN MORA
        # -------------------------------
        elif reporte == 'mora':
            consulta = """
                SELECT
                    a.cedula,
                    a.nombre || ' ' || a.apellido AS asociado,
                    c.numero_radicado,
                    pc.numero_cuota,
                    CURRENT_DATE - pc.fecha_pago AS dias_mora
                FROM pago_cuota pc
                JOIN credito c
                    ON pc.numero_radicado = c.numero_radicado
                JOIN asociado a
                    ON c.cedula_asociado = a.cedula
                WHERE pc.estado IN ('pendiente', 'pagado_con_mora', 'en_mora')
                ORDER BY dias_mora DESC, a.apellido, a.nombre
            """

            cur.execute(consulta)
            resultados = cur.fetchall()

            for fila in resultados:
                mora_reporte.append({
                    'cedula': fila[0],
                    'nombre': fila[1],
                    'numero_radicado': fila[2],
                    'numero_cuota': fila[3],
                    'dias_mora': fila[4]
                })

        # -------------------------------
        # 5. ESTADO DE CARTERA POR LÍNEA Y ESTADO
        # -------------------------------
        elif reporte == 'cartera':
            agencia = request.args.get('agencia')
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')

            consulta = """
                SELECT
                    c.linea_credito,
                    c.estado,
                    COUNT(*) AS numero_creditos,
                    COALESCE(SUM(c.valor_aprobado), 0) AS valor_total_aprobado,
                    ROUND(
                        (
                            COALESCE(SUM(c.valor_aprobado), 0) * 100.0
                        ) / NULLIF((
                            SELECT COALESCE(SUM(c2.valor_aprobado), 0)
                            FROM credito c2
                            WHERE 1 = 1
                            {sub_filtro_agencia}
                            {sub_filtro_fecha_inicio}
                            {sub_filtro_fecha_fin}
                        ), 0),
                        2
                    ) AS porcentaje_total
                FROM credito c
                JOIN agencia ag
                    ON c.codigo_agencia = ag.codigo
                WHERE 1 = 1
            """

            params = []
            sub_filtro_agencia = ""
            sub_filtro_fecha_inicio = ""
            sub_filtro_fecha_fin = ""
            sub_params = []

            if agencia:
                consulta += " AND c.codigo_agencia = %s"
                params.append(agencia)
                sub_filtro_agencia = " AND c2.codigo_agencia = %s"
                sub_params.append(agencia)

            if fecha_inicio:
                consulta += " AND c.fecha_aprobacion >= %s"
                params.append(fecha_inicio)
                sub_filtro_fecha_inicio = " AND c2.fecha_aprobacion >= %s"
                sub_params.append(fecha_inicio)

            if fecha_fin:
                consulta += " AND c.fecha_aprobacion <= %s"
                params.append(fecha_fin)
                sub_filtro_fecha_fin = " AND c2.fecha_aprobacion <= %s"
                sub_params.append(fecha_fin)

            consulta = consulta.format(
                sub_filtro_agencia=sub_filtro_agencia,
                sub_filtro_fecha_inicio=sub_filtro_fecha_inicio,
                sub_filtro_fecha_fin=sub_filtro_fecha_fin
            )

            consulta += """
                GROUP BY c.linea_credito, c.estado
                ORDER BY c.linea_credito, c.estado
            """

            cur.execute(consulta, params + sub_params)
            resultados = cur.fetchall()

            for fila in resultados:
                cartera_reporte.append({
                    'linea_credito': fila[0],
                    'estado': fila[1],
                    'numero_creditos': fila[2],
                    'valor_total_aprobado': fila[3],
                    'porcentaje_total': fila[4] if fila[4] is not None else 0
                })

        # -------------------------------
        # 6. PRODUCTIVIDAD DE ASESORES POR AGENCIA
        # -------------------------------
        elif reporte == 'productividad':
            agencia = request.args.get('agencia')
            fecha_inicio = request.args.get('fecha_inicio')
            fecha_fin = request.args.get('fecha_fin')
            ordenar = request.args.get('ordenar', 'asociados_atendidos')

            columnas_orden = {
                'asesor': 'asesor',
                'agencia': 'agencia',
                'asociados_atendidos': 'asociados_atendidos',
                'creditos_radicados': 'creditos_radicados',
                'valor_total_aprobado': 'valor_total_aprobado',
                'cuentas_abiertas': 'cuentas_abiertas'
            }

            orden_sql = columnas_orden.get(ordenar, 'asociados_atendidos')

            consulta = f"""
                SELECT
                    e.cedula_emple,
                    e.nombre || ' ' || e.apellido AS asesor,
                    ag.nombre AS agencia,
                    COUNT(DISTINCT at.cedula_asociado) AS asociados_atendidos,
                    COUNT(DISTINCT c.numero_radicado) AS creditos_radicados,
                    COALESCE(SUM(DISTINCT c.valor_aprobado), 0) AS valor_total_aprobado,
                    COUNT(DISTINCT ca.numero_cuenta) AS cuentas_abiertas
                FROM empleado e
                JOIN agencia ag
                    ON e.codigo_agencia = ag.codigo
                LEFT JOIN atiende at
                    ON at.cedula_empleado = e.cedula_emple
                LEFT JOIN credito c
                    ON c.codigo_agencia = e.codigo_agencia
                LEFT JOIN cuenta_ahorro ca
                    ON ca.codigo_agencia = e.codigo_agencia
                WHERE 1 = 1
            """

            params = []

            if agencia:
                consulta += " AND e.codigo_agencia = %s"
                params.append(agencia)

            if fecha_inicio:
                consulta += " AND (at.fecha_atencion IS NULL OR at.fecha_atencion >= %s)"
                consulta += " AND (c.fecha_aprobacion IS NULL OR c.fecha_aprobacion >= %s)"
                consulta += " AND (ca.fecha_apertura IS NULL OR ca.fecha_apertura >= %s)"
                params.extend([fecha_inicio, fecha_inicio, fecha_inicio])

            if fecha_fin:
                consulta += " AND (at.fecha_atencion IS NULL OR at.fecha_atencion <= %s)"
                consulta += " AND (c.fecha_aprobacion IS NULL OR c.fecha_aprobacion <= %s)"
                consulta += " AND (ca.fecha_apertura IS NULL OR ca.fecha_apertura <= %s)"
                params.extend([fecha_fin, fecha_fin, fecha_fin])

            consulta += f"""
                GROUP BY e.cedula_emple, e.nombre, e.apellido, ag.nombre
                ORDER BY {orden_sql} DESC, asesor
            """

            print("REPORTE:", reporte)
            print("CONSULTA:", consulta)
            print("PARAMS:", params)

            cur.execute(consulta, params)
            resultados = cur.fetchall()

            for fila in resultados:
                productividad_reporte.append({
                    'cedula_emple': fila[0],
                    'asesor': fila[1],
                    'agencia': fila[2],
                    'asociados_atendidos': fila[3] if fila[3] is not None else 0,
                    'creditos_radicados': fila[4] if fila[4] is not None else 0,
                    'valor_total_aprobado': fila[5] if fila[5] is not None else 0,
                    'cuentas_abiertas': fila[6] if fila[6] is not None else 0
                })
                
        # -------------------------------
        # 7. ASOCIADOS CON CODEUDORA ACTIVA
        # -------------------------------
        elif reporte == 'codeudora':
            estado_credito = request.args.get('estado_credito')
            numero_credito = request.args.get('numero_credito')

            consulta = """
                SELECT
                    c.numero_radicado,
                    t.cedula AS cedula_titular,
                    t.nombre || ' ' || t.apellido AS titular,
                    cd.cedula_codeudor,
                    co.nombre || ' ' || co.apellido AS codeudor,
                    c.valor_aprobado,
                    cd.fecha_firma,
                    c.estado
                FROM codeudor cd
                JOIN credito c
                    ON cd.numero_radicado = c.numero_radicado
                JOIN asociado t
                    ON c.cedula_asociado = t.cedula
                JOIN asociado co
                    ON cd.cedula_codeudor = co.cedula
                WHERE 1 = 1
            """

            params = []

            if estado_credito:
                consulta += " AND c.estado = %s"
                params.append(estado_credito)

            if numero_credito:
                consulta += " AND c.numero_radicado = %s"
                params.append(numero_credito)

            consulta += " ORDER BY c.numero_radicado"

            cur.execute(consulta, params)
            resultados = cur.fetchall()

            for fila in resultados:
                codeudora_reporte.append({
                    'numero_radicado': fila[0],
                    'cedula_titular': fila[1],
                    'titular': fila[2],
                    'cedula_codeudor': fila[3],
                    'codeudor': fila[4],
                    'valor_aprobado': fila[5],
                    'fecha_firma': fila[6],
                    'estado': fila[7]
                })

        return render_template(
            'reportes.html',
            reporte_activo=reporte,
            asociados_reporte=asociados_reporte,
            extracto_reporte=extracto_reporte,
            pagos_reporte=pagos_reporte,
            mora_reporte=mora_reporte,
            cartera_reporte=cartera_reporte,
            productividad_reporte=productividad_reporte,
            codeudora_reporte=codeudora_reporte,
            saldo_extracto=saldo_extracto
        )

    except Exception as e:
        import traceback
        return f"<pre>Error al generar reportes: {e}\n\n{traceback.format_exc()}</pre>"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()