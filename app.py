import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from pathlib import Path

from pdf_generator import generar_pdf


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Sistema de Proformas | Unicomer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB = "proformas.db"


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

    /* ---------- GENERAL ---------- */

    .stApp {
        background-color: #f5f7fa;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* ---------- TÍTULOS ---------- */

    .main-title {
        font-size: 30px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #6b7280;
        font-size: 15px;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #1f2937;
        margin-top: 20px;
        margin-bottom: 12px;
    }

    /* ---------- TARJETAS KPI ---------- */

    .kpi-card {
        background: #ffffff;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        min-height: 125px;
    }

    .kpi-label {
        color: #6b7280;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .kpi-value {
        color: #111827;
        font-size: 28px;
        font-weight: 700;
    }

    .kpi-description {
        color: #9ca3af;
        font-size: 12px;
        margin-top: 5px;
    }

    /* ---------- CONTENEDORES ---------- */

    .dashboard-box {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    /* ---------- BOTONES ---------- */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* ---------- TABLAS ---------- */

    [data-testid="stDataFrame"] {
        border-radius: 10px;
    }

    /* ---------- ALERTA ---------- */

    .info-box {
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 14px;
        border-radius: 6px;
        color: #1e3a8a;
        margin-bottom: 15px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# BASE DE DATOS
# ============================================================

def conectar_db():
    return sqlite3.connect(DB)


def preparar_base_datos():

    con = conectar_db()
    cursor = con.cursor()

    # ---------------- PROVEEDORES ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula TEXT,
            telefono TEXT,
            correo TEXT
        )
    """)

    # ---------------- PROFORMAS ----------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proformas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor TEXT NOT NULL,
            descripcion TEXT,
            cantidad REAL,
            precio REAL,
            subtotal REAL,
            iva REAL,
            total REAL,
            moneda TEXT,
            impuesto TEXT,
            fecha_creacion TEXT,
            ruta_pdf TEXT
        )
    """)

    con.commit()
    con.close()


preparar_base_datos()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def obtener_proveedores():

    con = conectar_db()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM proveedores
        ORDER BY nombre
        """,
        con
    )

    con.close()

    return df


def obtener_proformas():

    con = conectar_db()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM proformas
        ORDER BY id DESC
        """,
        con
    )

    con.close()

    if not df.empty:
        df["fecha_creacion"] = pd.to_datetime(
            df["fecha_creacion"],
            errors="coerce"
        )

    return df


def formato_moneda(valor, moneda):

    if pd.isna(valor):
        return "-"

    if moneda == "CRC":
        return f"₡{valor:,.0f}"

    return f"${valor:,.2f}"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding:10px 0 25px 0;">
            <div style="font-size:42px;">🏢</div>
            <div style="
                font-size:20px;
                font-weight:700;
                color:#1f2937;
            ">
                Sistema de Proformas
            </div>
            <div style="
                font-size:12px;
                color:#6b7280;
                margin-top:4px;
            ">
                Unicomer Costa Rica
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    menu = st.radio(
        "MENÚ PRINCIPAL",
        [
            "📊 Dashboard",
            "📝 Nueva Proforma",
            "📋 Historial",
            "🏢 Proveedores"
        ],
        label_visibility="visible"
    )

    st.divider()

    st.caption("Sistema interno")
    st.caption("Gestión de proformas y proveedores")


# ============================================================
# DASHBOARD
# ============================================================

if menu == "📊 Dashboard":

    st.markdown(
        '<div class="main-title">Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Resumen general de la gestión de proformas'
        '</div>',
        unsafe_allow_html=True
    )

    df = obtener_proformas()

    if df.empty:

        st.info(
            "Todavía no existen proformas registradas. "
            "Cree una nueva proforma para comenzar a visualizar información."
        )

    else:

        # ----------------------------------------------------
        # FILTROS
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">Filtros</div>',
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            fecha_min = df["fecha_creacion"].min().date()
            fecha_max = df["fecha_creacion"].max().date()

            fecha_inicio = st.date_input(
                "Fecha inicial",
                value=fecha_min,
                min_value=fecha_min,
                max_value=fecha_max
            )

        with col2:

            fecha_fin = st.date_input(
                "Fecha final",
                value=fecha_max,
                min_value=fecha_min,
                max_value=fecha_max
            )

        with col3:

            monedas = ["Todas"] + sorted(
                df["moneda"].dropna().unique().tolist()
            )

            moneda_filtro = st.selectbox(
                "Moneda",
                monedas
            )

        df_dash = df[
            (df["fecha_creacion"].dt.date >= fecha_inicio)
            &
            (df["fecha_creacion"].dt.date <= fecha_fin)
        ].copy()

        if moneda_filtro != "Todas":
            df_dash = df_dash[
                df_dash["moneda"] == moneda_filtro
            ]

        # ----------------------------------------------------
        # KPIs
        # ----------------------------------------------------

        cantidad_proformas = len(df_dash)

        cantidad_proveedores = df_dash["proveedor"].nunique()

        cantidad_mes = len(
            df_dash[
                df_dash["fecha_creacion"].dt.month
                == datetime.now().month
            ]
        )

        total_crc = df_dash.loc[
            df_dash["moneda"] == "CRC",
            "total"
        ].sum()

        total_usd = df_dash.loc[
            df_dash["moneda"] == "USD",
            "total"
        ].sum()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">
                        TOTAL PROFORMAS
                    </div>
                    <div class="kpi-value">
                        {cantidad_proformas:,}
                    </div>
                    <div class="kpi-description">
                        Registros en el período seleccionado
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">
                        PROVEEDORES
                    </div>
                    <div class="kpi-value">
                        {cantidad_proveedores:,}
                    </div>
                    <div class="kpi-description">
                        Proveedores con actividad
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">
                        ACTIVIDAD DEL MES
                    </div>
                    <div class="kpi-value">
                        {cantidad_mes:,}
                    </div>
                    <div class="kpi-description">
                        Proformas registradas este mes
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col4:

            if moneda_filtro == "CRC":

                monto_texto = f"₡{total_crc:,.0f}"

            elif moneda_filtro == "USD":

                monto_texto = f"${total_usd:,.2f}"

            else:

                monto_texto = (
                    f"₡{total_crc:,.0f} + "
                    f"${total_usd:,.2f}"
                )

            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-label">
                        MONTO COTIZADO
                    </div>
                    <div class="kpi-value" style="font-size:21px;">
                        {monto_texto}
                    </div>
                    <div class="kpi-description">
                        Total de proformas
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # GRÁFICO DE EVOLUCIÓN
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">'
            '📈 Evolución de proformas'
            '</div>',
            unsafe_allow_html=True
        )

        df_meses = df_dash.copy()

        df_meses["mes"] = (
            df_meses["fecha_creacion"]
            .dt.to_period("M")
            .astype(str)
        )

        resumen_mensual = (
            df_meses
            .groupby(["mes", "moneda"])
            .size()
            .reset_index(name="cantidad")
        )

        if not resumen_mensual.empty:

            fig = px.bar(
                resumen_mensual,
                x="mes",
                y="cantidad",
                color="moneda",
                barmode="group",
                text="cantidad",
                labels={
                    "mes": "Mes",
                    "cantidad": "Proformas",
                    "moneda": "Moneda"
                }
            )

            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor="white",
                plot_bgcolor="white",
                legend_title_text="",
                hovermode="x unified"
            )

            fig.update_traces(
                textposition="outside"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ----------------------------------------------------
        # SEGUNDA FILA
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        # ----------------------------------------------------
        # TOP PROVEEDORES
        # ----------------------------------------------------

        with col1:

            st.markdown(
                '<div class="section-title">'
                '🏢 Proveedores con más proformas'
                '</div>',
                unsafe_allow_html=True
            )

            top_proveedores = (
                df_dash
                .groupby("proveedor")
                .size()
                .reset_index(name="cantidad")
                .sort_values(
                    "cantidad",
                    ascending=False
                )
                .head(10)
            )

            if not top_proveedores.empty:

                fig_prov = px.bar(
                    top_proveedores.sort_values(
                        "cantidad"
                    ),
                    x="cantidad",
                    y="proveedor",
                    orientation="h",
                    text="cantidad",
                    labels={
                        "cantidad": "Proformas",
                        "proveedor": "Proveedor"
                    }
                )

                fig_prov.update_layout(
                    height=400,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20
                    ),
                    paper_bgcolor="white",
                    plot_bgcolor="white"
                )

                st.plotly_chart(
                    fig_prov,
                    use_container_width=True
                )

        # ----------------------------------------------------
        # MONEDAS
        # ----------------------------------------------------

        with col2:

            st.markdown(
                '<div class="section-title">'
                '💵 Distribución por moneda'
                '</div>',
                unsafe_allow_html=True
            )

            moneda_data = (
                df_dash
                .groupby("moneda")
                .size()
                .reset_index(name="cantidad")
            )

            if not moneda_data.empty:

                fig_moneda = px.pie(
                    moneda_data,
                    names="moneda",
                    values="cantidad",
                    hole=0.55
                )

                fig_moneda.update_layout(
                    height=400,
                    margin=dict(
                        l=20,
                        r=20,
                        t=20,
                        b=20
                    ),
                    paper_bgcolor="white",
                    legend_title_text=""
                )

                st.plotly_chart(
                    fig_moneda,
                    use_container_width=True
                )

        # ----------------------------------------------------
        # MONTOS POR MES
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">'
            '💰 Monto cotizado por mes'
            '</div>',
            unsafe_allow_html=True
        )

        df_monto = df_dash.copy()

        df_monto["mes"] = (
            df_monto["fecha_creacion"]
            .dt.to_period("M")
            .astype(str)
        )

        monto_mensual = (
            df_monto
            .groupby(["mes", "moneda"])["total"]
            .sum()
            .reset_index()
        )

        if not monto_mensual.empty:

            fig_monto = px.line(
                monto_mensual,
                x="mes",
                y="total",
                color="moneda",
                markers=True,
                labels={
                    "mes": "Mes",
                    "total": "Monto",
                    "moneda": "Moneda"
                }
            )

            fig_monto.update_layout(
                height=400,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                ),
                paper_bgcolor="white",
                plot_bgcolor="white",
                hovermode="x unified"
            )

            st.plotly_chart(
                fig_monto,
                use_container_width=True
            )

        # ----------------------------------------------------
        # ÚLTIMAS PROFORMAS
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">'
            '📋 Últimas proformas'
            '</div>',
            unsafe_allow_html=True
        )

        ultimas = df_dash.head(10).copy()

        if not ultimas.empty:

            ultimas["Fecha"] = (
                ultimas["fecha_creacion"]
                .dt.strftime("%d/%m/%Y %H:%M")
            )

            ultimas["Total"] = ultimas.apply(
                lambda row:
                    formato_moneda(
                        row["total"],
                        row["moneda"]
                    ),
                axis=1
            )

            tabla = ultimas[
                [
                    "id",
                    "proveedor",
                    "descripcion",
                    "Fecha",
                    "Total",
                    "moneda"
                ]
            ].rename(
                columns={
                    "id": "ID",
                    "proveedor": "Proveedor",
                    "descripcion": "Descripción",
                    "moneda": "Moneda"
                }
            )

            st.dataframe(
                tabla,
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# NUEVA PROFORMA
# ============================================================

elif menu == "📝 Nueva Proforma":

    st.markdown(
        '<div class="main-title">Nueva Proforma</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Complete la información para generar una nueva proforma.'
        '</div>',
        unsafe_allow_html=True
    )

    proveedores = obtener_proveedores()

    if proveedores.empty:

        st.warning(
            "No existen proveedores registrados. "
            "Primero debe crear un proveedor."
        )

    else:

        # ----------------------------------------------------
        # PROVEEDOR
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">Información del proveedor</div>',
            unsafe_allow_html=True
        )

        nombres = proveedores["nombre"].tolist()

        proveedor_nombre = st.selectbox(
            "Proveedor",
            nombres
        )

        proveedor_info = proveedores[
            proveedores["nombre"] == proveedor_nombre
        ].iloc[0]

        col1, col2, col3 = st.columns(3)

        with col1:

            st.text_input(
                "Cédula / Identificación",
                value=str(
                    proveedor_info["cedula"]
                    or ""
                ),
                disabled=True
            )

        with col2:

            st.text_input(
                "Teléfono",
                value=str(
                    proveedor_info["telefono"]
                    or ""
                ),
                disabled=True
            )

        with col3:

            st.text_input(
                "Correo",
                value=str(
                    proveedor_info["correo"]
                    or ""
                ),
                disabled=True
            )

        # ----------------------------------------------------
        # DETALLE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section-title">Detalle de la proforma</div>',
            unsafe_allow_html=True
        )

        descripcion = st.text_area(
            "Descripción",
            placeholder="Ingrese el detalle de los productos o servicios..."
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            cantidad = st.number_input(
                "Cantidad",
                min_value=1,
                value=1,
                step=1
            )

        with col2:

            precio = st.number_input(
                "Precio unitario",
                min_value=0.0,
                value=0.0,
                step=100.0
            )

        with col3:

            moneda = st.selectbox(
                "Moneda",
                ["CRC", "USD"]
            )

        with col4:

            impuesto = st.selectbox(
                "Impuesto",
                [
                    "IVA 13%",
                    "Exento"
                ]
            )

        # ----------------------------------------------------
        # CÁLCULOS
        # ----------------------------------------------------

        subtotal = cantidad * precio

        if impuesto == "IVA 13%":

            iva = subtotal * 0.13

        else:

            iva = 0

        total = subtotal + iva

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Subtotal",
                formato_moneda(
                    subtotal,
                    moneda
                )
            )

        with col2:

            st.metric(
                "Impuesto",
                formato_moneda(
                    iva,
                    moneda
                )
            )

        with col3:

            st.metric(
                "TOTAL",
                formato_moneda(
                    total,
                    moneda
                )
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # GENERAR
        # ----------------------------------------------------

        if st.button(
            "📄 Generar Proforma",
            type="primary",
            use_container_width=True
        ):

            if not descripcion.strip():

                st.error(
                    "Debe ingresar una descripción."
                )

            elif precio <= 0:

                st.error(
                    "El precio debe ser mayor que cero."
                )

            else:

                try:

                    ruta_pdf = generar_pdf(
                        proveedor_nombre,
                        proveedor_info["cedula"],
                        proveedor_info["telefono"],
                        proveedor_info["correo"],
                        descripcion,
                        cantidad,
                        precio,
                        subtotal,
                        iva,
                        total,
                        moneda,
                        impuesto
                    )

                    con = conectar_db()

                    cursor = con.cursor()

                    cursor.execute(
                        """
                        INSERT INTO proformas (
                            proveedor,
                            descripcion,
                            cantidad,
                            precio,
                            subtotal,
                            iva,
                            total,
                            moneda,
                            impuesto,
                            fecha_creacion,
                            ruta_pdf
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            proveedor_nombre,
                            descripcion,
                            cantidad,
                            precio,
                            subtotal,
                            iva,
                            total,
                            moneda,
                            impuesto,
                            datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            str(ruta_pdf)
                        )
                    )

                    con.commit()
                    con.close()

                    st.success(
                        "✅ Proforma generada correctamente."
                    )

                    # ------------------------------------------------
                    # DESCARGA
                    # ------------------------------------------------

                    ruta = Path(ruta_pdf)

                    if ruta.exists():

                        with open(
                            ruta,
                            "rb"
                        ) as archivo:

                            st.download_button(
                                "📥 Descargar PDF",
                                data=archivo,
                                file_name=ruta.name,
                                mime="application/pdf",
                                use_container_width=True
                            )

                except Exception as e:

                    st.error(
                        f"Ocurrió un error al generar la proforma: {e}"
                    )


# ============================================================
# HISTORIAL
# ============================================================

elif menu == "📋 Historial":

    st.markdown(
        '<div class="main-title">Historial de Proformas</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Consulta, descarga y exportación de las proformas generadas.'
        '</div>',
        unsafe_allow_html=True
    )

    df = obtener_proformas()

    if df.empty:

        st.info(
            "No existen proformas registradas."
        )

    else:

        # ----------------------------------------------------
        # FILTROS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            proveedores_filtro = [
                "Todos"
            ] + sorted(
                df["proveedor"]
                .dropna()
                .unique()
                .tolist()
            )

            proveedor_filtro = st.selectbox(
                "Proveedor",
                proveedores_filtro
            )

        with col2:

            moneda_filtro = st.selectbox(
                "Moneda",
                [
                    "Todas",
                    "CRC",
                    "USD"
                ]
            )

        with col3:

            fecha_filtro = st.date_input(
                "Fecha",
                value=None
            )

        with col4:

            texto_busqueda = st.text_input(
                "Buscar",
                placeholder="Proveedor o descripción"
            )

        df_filtrado = df.copy()

        if proveedor_filtro != "Todos":

            df_filtrado = df_filtrado[
                df_filtrado["proveedor"]
                == proveedor_filtro
            ]

        if moneda_filtro != "Todas":

            df_filtrado = df_filtrado[
                df_filtrado["moneda"]
                == moneda_filtro
            ]

        if fecha_filtro:

            df_filtrado = df_filtrado[
                df_filtrado["fecha_creacion"].dt.date
                == fecha_filtro
            ]

        if texto_busqueda:

            texto = texto_busqueda.lower()

            df_filtrado = df_filtrado[
                df_filtrado["proveedor"]
                .fillna("")
                .str.lower()
                .str.contains(texto)
                |
                df_filtrado["descripcion"]
                .fillna("")
                .str.lower()
                .str.contains(texto)
            ]

        # ----------------------------------------------------
        # MÉTRICAS
        # ----------------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Proformas encontradas",
                len(df_filtrado)
            )

        with col2:

            total_crc_hist = df_filtrado.loc[
                df_filtrado["moneda"] == "CRC",
                "total"
            ].sum()

            st.metric(
                "Total CRC",
                f"₡{total_crc_hist:,.0f}"
            )

        with col3:

            total_usd_hist = df_filtrado.loc[
                df_filtrado["moneda"] == "USD",
                "total"
            ].sum()

            st.metric(
                "Total USD",
                f"${total_usd_hist:,.2f}"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # EXPORTAR CSV
        # ----------------------------------------------------

        columnas_exportar = [
            "proveedor",
            "fecha_creacion",
            "descripcion",
            "cantidad",
            "precio",
            "subtotal",
            "iva",
            "total",
            "moneda",
            "impuesto"
        ]

        df_exportar = df_filtrado[
            columnas_exportar
        ].copy()

        df_exportar = df_exportar.rename(
            columns={
                "proveedor": "Proveedor",
                "fecha_creacion": "Fecha",
                "descripcion": "Descripción",
                "cantidad": "Cantidad",
                "precio": "Precio Unitario",
                "subtotal": "Subtotal",
                "iva": "IVA",
                "total": "Total",
                "moneda": "Moneda",
                "impuesto": "Impuesto"
            }
        )

        csv = df_exportar.to_csv(
            index=False,
            encoding="utf-8-sig"
        )

        st.download_button(
            label="📥 Descargar Historial en CSV",
            data=csv,
            file_name=(
                "historial_proformas_"
                + datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )
                + ".csv"
            ),
            mime="text/csv",
            use_container_width=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # TABLA
        # ----------------------------------------------------

        if df_filtrado.empty:

            st.warning(
                "No se encontraron resultados con los filtros seleccionados."
            )

        else:

            for _, row in df_filtrado.iterrows():

                fecha = row["fecha_creacion"]

                if pd.notna(fecha):

                    fecha_texto = fecha.strftime(
                        "%d/%m/%Y %H:%M"
                    )

                else:

                    fecha_texto = "-"

                titulo = (
                    f"#{row['id']} | "
                    f"{row['proveedor']} | "
                    f"{fecha_texto}"
                )

                with st.expander(titulo):

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.write(
                            "**Proveedor**"
                        )

                        st.write(
                            row["proveedor"]
                        )

                    with col2:

                        st.write(
                            "**Descripción**"
                        )

                        st.write(
                            row["descripcion"]
                        )

                    with col3:

                        st.write(
                            "**Total**"
                        )

                        st.write(
                            formato_moneda(
                                row["total"],
                                row["moneda"]
                            )
                        )

                    with col4:

                        st.write(
                            "**Impuesto**"
                        )

                        st.write(
                            row["impuesto"]
                        )

                    ruta_pdf = row["ruta_pdf"]

                    if ruta_pdf:

                        ruta = Path(ruta_pdf)

                        if ruta.exists():

                            with open(
                                ruta,
                                "rb"
                            ) as archivo:

                                st.download_button(
                                    "📄 Descargar PDF",
                                    data=archivo,
                                    file_name=ruta.name,
                                    mime="application/pdf",
                                    key=f"pdf_{row['id']}"
                                )

                    if st.button(
                        "🗑️ Eliminar",
                        key=f"delete_{row['id']}"
                    ):

                        con = conectar_db()

                        cursor = con.cursor()

                        cursor.execute(
                            "DELETE FROM proformas WHERE id = ?",
                            (row["id"],)
                        )

                        con.commit()
                        con.close()

                        st.success(
                            "Proforma eliminada."
                        )

                        st.rerun()


# ============================================================
# PROVEEDORES
# ============================================================

elif menu == "🏢 Proveedores":

    st.markdown(
        '<div class="main-title">Proveedores</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Administración de proveedores registrados en el sistema.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # REGISTRAR PROVEEDOR
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '➕ Registrar proveedor'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        nombre = st.text_input(
            "Nombre del proveedor"
        )

        cedula = st.text_input(
            "Cédula / Identificación"
        )

    with col2:

        telefono = st.text_input(
            "Teléfono"
        )

        correo = st.text_input(
            "Correo electrónico"
        )

    if st.button(
        "💾 Guardar proveedor",
        type="primary"
    ):

        if not nombre.strip():

            st.error(
                "Debe ingresar el nombre del proveedor."
            )

        else:

            con = conectar_db()

            cursor = con.cursor()

            cursor.execute(
                """
                INSERT INTO proveedores (
                    nombre,
                    cedula,
                    telefono,
                    correo
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    nombre,
                    cedula,
                    telefono,
                    correo
                )
            )

            con.commit()
            con.close()

            st.success(
                "✅ Proveedor registrado correctamente."
            )

            st.rerun()

    # --------------------------------------------------------
    # LISTADO
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📋 Proveedores registrados'
        '</div>',
        unsafe_allow_html=True
    )

    proveedores = obtener_proveedores()

    if proveedores.empty:

        st.info(
            "No hay proveedores registrados."
        )

    else:

        tabla_proveedores = proveedores[
            [
                "id",
                "nombre",
                "cedula",
                "telefono",
                "correo"
            ]
        ].rename(
            columns={
                "id": "ID",
                "nombre": "Proveedor",
                "cedula": "Cédula",
                "telefono": "Teléfono",
                "correo": "Correo"
            }
        )

        st.dataframe(
            tabla_proveedores,
            use_container_width=True,
            hide_index=True
        )