from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from datetime import datetime
import os
import platform


# ==========================================================
# CONFIGURACIÓN DE FUENTE
# ==========================================================

def cargar_fuente():
    """
    Busca automáticamente una fuente Unicode
    para soportar ₡, $, tildes, ñ, etc.
    """

    posibles_fuentes = []

    sistema = platform.system()

    if sistema == "Windows":

        posibles_fuentes = [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\calibri.ttf",
        ]

    elif sistema == "Darwin":

        posibles_fuentes = [
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]

    else:

        posibles_fuentes = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        ]

    for fuente in posibles_fuentes:

        if os.path.exists(fuente):

            try:

                pdfmetrics.registerFont(
                    TTFont("UnicodeFont", fuente)
                )

                return "UnicodeFont"

            except Exception:
                pass

    return "Helvetica"


FUENTE = cargar_fuente()


# ==========================================================
# AJUSTAR TEXTO A UN ANCHO
# ==========================================================

def texto_ajustado(texto, max_ancho, fuente, tamaño):

    texto = str(texto)

    if stringWidth(texto, fuente, tamaño) <= max_ancho:
        return [texto]

    palabras = texto.split()

    lineas = []
    linea_actual = ""

    for palabra in palabras:

        prueba = linea_actual + " " + palabra

        if stringWidth(
            prueba.strip(),
            fuente,
            tamaño
        ) <= max_ancho:

            linea_actual = prueba.strip()

        else:

            if linea_actual:
                lineas.append(linea_actual)

            linea_actual = palabra

    if linea_actual:
        lineas.append(linea_actual)

    return lineas


# ==========================================================
# GENERAR PDF
# ==========================================================

def generar_pdf(
    proveedor,
    cedula,
    telefono,
    correo,
    descripcion,
    cantidad,
    precio,
    subtotal,
    iva,
    total,
    moneda,
    impuesto
):

    # ======================================================
    # CARPETA DE PDF
    # ======================================================

    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")

    # ======================================================
    # CONSECUTIVO
    # ======================================================

    consecutivo = datetime.now().strftime(
        "PF-%Y%m%d-%H%M%S"
    )

    archivo = f"pdfs/{consecutivo}.pdf"

    # ======================================================
    # MONEDA
    # ======================================================

    if moneda == "USD":
        simbolo = "$"
    else:
        simbolo = "₡"

    # ======================================================
    # CREAR PDF
    # ======================================================

    pdf = canvas.Canvas(
        archivo,
        pagesize=letter
    )

    ancho, alto = letter

    # ======================================================
    # COLORES
    # ======================================================

    NEGRO = colors.HexColor("#111111")
    GRIS = colors.HexColor("#555555")
    GRIS_CLARO = colors.HexColor("#DDDDDD")
    BLANCO = colors.white

    # ======================================================
    # MÁRGENES
    # ======================================================

    izquierda = 42
    derecha = 570

    # ======================================================
    # ENCABEZADO
    # ======================================================

    try:

        pdf.drawImage(
            "assets/Emma Logo-01 3 (2).png",
            izquierda,
            alto - 78,
            width=115,
            height=42,
            preserveAspectRatio=True,
            mask="auto"
        )

    except Exception:
        pass

    # ======================================================
    # TÍTULO PROFORMA
    # ======================================================

    pdf.setFillColor(NEGRO)

    pdf.setFont(
        FUENTE,
        18
    )

    pdf.drawRightString(
        derecha,
        alto - 55,
        "PROFORMA"
    )

    pdf.setFont(
        FUENTE,
        8
    )

    pdf.drawRightString(
        derecha,
        alto - 70,
        consecutivo
    )

    # ======================================================
    # LÍNEA DEL ENCABEZADO
    # ======================================================

    linea_encabezado = alto - 105

    pdf.setStrokeColor(NEGRO)
    pdf.setLineWidth(1)

    pdf.line(
        izquierda,
        linea_encabezado,
        derecha,
        linea_encabezado
    )

    # ======================================================
    # PROVEEDOR
    # ======================================================

    y = linea_encabezado - 22

    pdf.setFillColor(NEGRO)

    pdf.setFont(
        FUENTE,
        9
    )

    pdf.drawString(
        izquierda,
        y,
        "PROVEEDOR"
    )

    y -= 15

    pdf.setFont(
        FUENTE,
        10
    )

    pdf.drawString(
        izquierda,
        y,
        str(proveedor)[:55]
    )

    y -= 14

    pdf.setFont(
        FUENTE,
        8
    )

    pdf.drawString(
        izquierda,
        y,
        f"Identificación: {cedula}"
    )

    y -= 13

    pdf.drawString(
        izquierda,
        y,
        f"Teléfono: {telefono}"
    )

    y -= 13

    pdf.drawString(
        izquierda,
        y,
        f"Correo: {correo}"
    )

    # ======================================================
    # RECEPTOR
    # ======================================================

    x_receptor = 325

    y2 = linea_encabezado - 22

    pdf.setFont(
        FUENTE,
        9
    )

    pdf.drawString(
        x_receptor,
        y2,
        "RECEPTOR"
    )

    y2 -= 15

    pdf.setFont(
        FUENTE,
        9
    )

    pdf.drawString(
        x_receptor,
        y2,
        "UNIÓN COMERCIAL DE COSTA RICA, S.A."
    )

    y2 -= 14

    pdf.setFont(
        FUENTE,
        8
    )

    pdf.drawString(
        x_receptor,
        y2,
        "Identificación jurídica: 3-101-074154"
    )

    y2 -= 13

    pdf.drawString(
        x_receptor,
        y2,
        "Teléfono: +506 2437-4484"
    )

    # ======================================================
    # INFORMACIÓN DE LA PROFORMA
    # ======================================================

    bloque_y = 555

    pdf.setStrokeColor(NEGRO)
    pdf.setLineWidth(0.8)

    pdf.line(
        izquierda,
        bloque_y + 22,
        derecha,
        bloque_y + 22
    )

    pdf.setFont(
        FUENTE,
        8
    )

    # ------------------------------------------------------
    # COLUMNA IZQUIERDA
    # ------------------------------------------------------

    pdf.drawString(
        izquierda,
        bloque_y,
        "Proforma N.º:"
    )

    pdf.drawString(
        izquierda + 75,
        bloque_y,
        consecutivo
    )

    pdf.drawString(
        izquierda,
        bloque_y - 16,
        "Moneda:"
    )

    pdf.drawString(
        izquierda + 75,
        bloque_y - 16,
        moneda
    )

    # ------------------------------------------------------
    # COLUMNA DERECHA
    # ------------------------------------------------------

    pdf.drawString(
        325,
        bloque_y,
        "Fecha de emisión:"
    )

    pdf.drawString(
        410,
        bloque_y,
        datetime.now().strftime("%d/%m/%Y")
    )

    pdf.drawString(
        325,
        bloque_y - 16,
        "Impuesto:"
    )

    pdf.drawString(
        410,
        bloque_y - 16,
        str(impuesto)
    )

    # ======================================================
    # TABLA
    # ======================================================

    tabla_top = 510

    tabla_izq = izquierda
    tabla_der = derecha

    alto_header = 25

    # ======================================================
    # ENCABEZADO DE TABLA
    # ======================================================

    pdf.setFillColor(NEGRO)

    pdf.rect(
        tabla_izq,
        tabla_top,
        tabla_der - tabla_izq,
        alto_header,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(BLANCO)

    pdf.setFont(
        FUENTE,
        7.5
    )

    pdf.drawString(
        48,
        tabla_top + 9,
        "CÓDIGO"
    )

    pdf.drawString(
        105,
        tabla_top + 9,
        "DESCRIPCIÓN"
    )

    pdf.drawRightString(
        395,
        tabla_top + 9,
        "CANT."
    )

    pdf.drawRightString(
        470,
        tabla_top + 9,
        "PRECIO"
    )

    pdf.drawRightString(
        550,
        tabla_top + 9,
        "TOTAL"
    )

    # ======================================================
    # FILA DE DETALLE
    # ======================================================

    fila_top = tabla_top
    fila_alto = 55

    pdf.setFillColor(BLANCO)

    pdf.rect(
        tabla_izq,
        fila_top - fila_alto,
        tabla_der - tabla_izq,
        fila_alto,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(NEGRO)

    pdf.setFont(
        FUENTE,
        8
    )

    # Código

    pdf.drawString(
        48,
        fila_top - 22,
        "-"
    )

    # ======================================================
    # DESCRIPCIÓN
    # ======================================================

    lineas = texto_ajustado(
        descripcion,
        235,
        FUENTE,
        8
    )

    descripcion_y = fila_top - 18

    for linea in lineas[:3]:

        pdf.drawString(
            105,
            descripcion_y,
            linea
        )

        descripcion_y -= 12

    # ======================================================
    # CANTIDAD
    # ======================================================

    pdf.drawRightString(
        395,
        fila_top - 22,
        str(cantidad)
    )

    # ======================================================
    # PRECIO
    # ======================================================

    pdf.drawRightString(
        470,
        fila_top - 22,
        f"{simbolo}{precio:,.2f}"
    )

    # ======================================================
    # TOTAL
    # ======================================================

    pdf.drawRightString(
        550,
        fila_top - 22,
        f"{simbolo}{subtotal:,.2f}"
    )

    # ======================================================
    # LÍNEA INFERIOR
    # ======================================================

    pdf.setStrokeColor(GRIS_CLARO)
    pdf.setLineWidth(0.7)

    pdf.line(
        tabla_izq,
        fila_top - fila_alto,
        tabla_der,
        fila_top - fila_alto
    )

    # ======================================================
    # NOTAS
    # ======================================================

    notas_y = fila_top - fila_alto - 30

    pdf.setFillColor(NEGRO)

    pdf.setFont(
        FUENTE,
        8
    )

    pdf.drawString(
        izquierda,
        notas_y,
        "NOTAS:"
    )

    pdf.setFont(
        FUENTE,
        7.5
    )

    pdf.drawString(
        izquierda,
        notas_y - 14,
        "Documento generado mediante el Sistema de Gestión de Proformas."
    )

    pdf.drawString(
        izquierda,
        notas_y - 27,
        "Unión Comercial de Costa Rica, S.A."
    )

    # ======================================================
    # TOTALES
    # ======================================================

    total_x = 385

    total_y = notas_y - 8

    pdf.setFont(
        FUENTE,
        8.5
    )

    # ------------------------------------------------------
    # SUBTOTAL
    # ------------------------------------------------------

    pdf.drawString(
        total_x,
        total_y,
        "Subtotal Neto"
    )

    pdf.drawRightString(
        derecha,
        total_y,
        f"{simbolo}{subtotal:,.2f}"
    )

    # ------------------------------------------------------
    # IMPUESTO
    # ------------------------------------------------------

    total_y -= 18

    pdf.drawString(
        total_x,
        total_y,
        "Total Impuesto"
    )

    pdf.drawRightString(
        derecha,
        total_y,
        f"{simbolo}{iva:,.2f}"
    )

    # ======================================================
    # TOTAL FINAL
    # ======================================================
    #
    # Se aumentó la separación para evitar que el cuadro
    # negro quede encima de "Total Impuesto".
    # ======================================================

    total_y -= 55

    ancho_total = 215
    alto_total = 40

    pdf.setFillColor(NEGRO)

    pdf.rect(
        derecha - ancho_total,
        total_y,
        ancho_total,
        alto_total,
        fill=1,
        stroke=0
    )

    pdf.setFillColor(BLANCO)

    pdf.setFont(
        FUENTE,
        10
    )

    pdf.drawString(
        derecha - ancho_total + 12,
        total_y + 15,
        "TOTAL PROFORMA:"
    )

    pdf.drawRightString(
        derecha - 10,
        total_y + 15,
        f"{simbolo}{total:,.2f}"
    )

    # ======================================================
    # PIE DE PÁGINA
    # ======================================================

    pdf.setFillColor(GRIS)

    pdf.setFont(
        FUENTE,
        7
    )

    pdf.drawString(
        izquierda,
        60,
        "Sistema interno de gestión de proformas"
    )

    pdf.drawRightString(
        derecha,
        60,
        "Página 1 de 1"
    )

    # ======================================================
    # GUARDAR PDF
    # ======================================================

    pdf.save()

    return archivo