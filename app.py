import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from database import conectar_db
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def colorear_celda(celda, color):
    tc_pr = celda._tc.get_or_add_tcPr()
    sombreado = OxmlElement("w:shd")
    sombreado.set(qn("w:fill"), color)
    tc_pr.append(sombreado)
load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
if not app.config["SECRET_KEY"]:
    raise RuntimeError("Configura la variable de entorno SECRET_KEY")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=bool(os.getenv("RAILWAY_ENVIRONMENT_ID")),
    DEBUG=False,
)
csrf = CSRFProtect(app)

@app.after_request
def proteger_respuesta(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "inicio"
class Enfermera(UserMixin):
    def __init__(self, id_enfermera, nombre, correo):
        self.id = str(id_enfermera)
        self.nombre = nombre
        self.correo = correo
@login_manager.user_loader
def cargar_enfermera(id_enfermera):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT id_enfermera, nombre_completo, correo
               FROM enfermeras
               WHERE id_enfermera = %s""",
            (id_enfermera,)
        )
        datos = cursor.fetchone()
        if datos:
            return Enfermera(
                datos["id_enfermera"],
                datos["nombre_completo"],
                datos["correo"]
            )
        return None
    finally:
        cursor.close()
        conexion.close()
@app.route("/", methods=["GET", "POST"])
def inicio():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        contrasena = request.form.get("contrasena", "")
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT * FROM enfermeras WHERE correo = %s",
                (correo,)
            )
            datos = cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()
        if datos and check_password_hash(
            datos["contrasena_hash"], contrasena
        ):
            enfermera = Enfermera(
                datos["id_enfermera"],
                datos["nombre_completo"],
                datos["correo"]
            )
            login_user(enfermera)
            return redirect(url_for("dashboard"))
        flash("Correo o contraseña incorrectos.", "danger")
    return render_template("login.html")
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    estudiante = None
    if request.method == "POST":
        numero_control = request.form.get(
            "numero_control", ""
        ).strip()
        if not numero_control:
            flash("Ingresa un número de control.", "warning")
        else:
            conexion = conectar_db()
            cursor = conexion.cursor(dictionary=True)
            try:
                cursor.execute(
                    """
                    SELECT numero_control,
                           nombre_completo,
                           carrera,
                           sexo,
                           edad
                    FROM estudiantes
                    WHERE numero_control = %s
                    """,
                    (numero_control,)
                )
                estudiante = cursor.fetchone()
            finally:
                cursor.close()
                conexion.close()
            if estudiante is None:
                flash(
                    "No se encontró un estudiante "
                    "con ese número de control.",
                    "warning"
                )
    return render_template(
        "dashboard.html",
        estudiante=estudiante
    )
@app.route("/registrar-atencion", methods=["POST"])
@login_required
def registrar_atencion():
    numero_control = request.form.get(
        "numero_control", ""
    ).strip()
    motivo = request.form.get(
        "motivo_visita", ""
    ).strip()
    signos = request.form.get(
        "signos_vitales", ""
    ).strip()
    procedimiento = request.form.get(
        "procedimiento", ""
    ).strip()
    observaciones = request.form.get(
        "observaciones", ""
    ).strip()
    if not numero_control or not motivo or not procedimiento:
        flash(
            "Completa los campos obligatorios.",
            "warning"
        )
        return redirect(url_for("dashboard"))
    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO atenciones (
                numero_control,
                id_enfermera,
                motivo_visita,
                signos_vitales,
                procedimiento,
                observaciones
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                numero_control,
                int(current_user.id),
                motivo,
                signos or None,
                procedimiento,
                observaciones or None
            )
        )
        conexion.commit()
        flash(
            "Atención registrada correctamente.",
            "success"
        )
    except Exception:
        if conexion:
            conexion.rollback()
        app.logger.exception(
            "No se pudo registrar la atención"
        )
        flash(
            "No se pudo guardar la atención.",
            "danger"
        )
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
    return redirect(url_for("dashboard"))
@app.route("/historial")
@login_required
def historial():
    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                a.id_atencion,
                a.fecha_atencion,
                e.numero_control,
                e.nombre_completo AS estudiante,
                e.carrera,
                a.motivo_visita,
                a.signos_vitales,
                a.procedimiento,
                a.observaciones,
                n.nombre_completo AS enfermera
            FROM atenciones a
            INNER JOIN estudiantes e
                ON a.numero_control = e.numero_control
            INNER JOIN enfermeras n
                ON a.id_enfermera = n.id_enfermera
            ORDER BY
                a.fecha_atencion DESC,
                a.id_atencion DESC
        """)
        atenciones = cursor.fetchall()
        return render_template(
            "historial.html",
            atenciones=atenciones
        )
    except Exception:
        app.logger.exception(
            "Error al consultar el historial"
        )
        flash(
            "No se pudo cargar el historial.",
            "danger"
        )
        return redirect(url_for("dashboard"))
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
@app.route("/reporte-mensual")
@login_required
def reporte_mensual():
    hoy = datetime.now()
    try:
        anio = int(request.args.get("anio", hoy.year))
        mes = int(request.args.get("mes", hoy.month))
        if not 2000 <= anio <= 2100:
            raise ValueError("Año fuera de rango")
        datetime(anio, mes, 1)
    except (ValueError, TypeError):
        flash("Selecciona un mes y año válidos.", "warning")
        return redirect(url_for("historial"))
    conexion = None
    cursor = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                a.id_atencion,
                a.fecha_atencion,
                e.numero_control,
                e.nombre_completo AS estudiante,
                a.motivo_visita,
                a.procedimiento,
                a.observaciones,
                n.nombre_completo AS enfermera
            FROM atenciones a
            INNER JOIN estudiantes e
                ON a.numero_control = e.numero_control
            INNER JOIN enfermeras n
                ON a.id_enfermera = n.id_enfermera
            WHERE YEAR(a.fecha_atencion) = %s
              AND MONTH(a.fecha_atencion) = %s
            ORDER BY
                a.fecha_atencion ASC,
                a.id_atencion ASC
        """, (anio, mes))
        atenciones = cursor.fetchall()
    except Exception:
        app.logger.exception("Error al consultar las atenciones")
        flash("No se pudo generar el reporte.", "danger")
        return redirect(url_for("historial"))
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
    meses = [
        "enero", "febrero", "marzo", "abril",
        "mayo", "junio", "julio", "agosto",
        "septiembre", "octubre", "noviembre",
        "diciembre"
    ]
    nombre_mes = meses[mes - 1]
    # Crear el documento Word
    documento = Document()
    # Encabezado institucional
    seccion = documento.sections[0]
    seccion.header_distance = Inches(0.3)
    encabezado = seccion.header
    tabla_logos = encabezado.add_table(
        rows=1,
        cols=3,
        width=Inches(6.8)
    )
    tabla_logos.autofit = False
    carpeta_img = Path(app.root_path) / "static" / "img"
    logos = [
        ("educacion.png", 1.9),
        ("tecnm.png", 1.5),
        ("cuidatec.png", 1.5)
    ]
    for indice, (nombre, ancho) in enumerate(logos):
        ruta = carpeta_img / nombre
        celda = tabla_logos.cell(0, indice)
        parrafo = celda.paragraphs[0]
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if ruta.is_file():
            parrafo.add_run().add_picture(
                str(ruta),
                width=Inches(ancho)
            )
        else:
            raise FileNotFoundError(
                f"Falta el logotipo: {ruta}"
            )
    seccion = documento.sections[0]
    seccion.top_margin = Inches(0.8)
    seccion.bottom_margin = Inches(0.8)
    seccion.left_margin = Inches(0.85)
    seccion.right_margin = Inches(0.85)
    estilo = documento.styles["Normal"]
    estilo.font.name = "Arial"
    estilo.font.size = Pt(11)
    estilo.paragraph_format.space_after = Pt(8)
    # Encabezado institucional
    titulo = documento.add_paragraph()
    titulo.alignment = 1
    titulo.add_run(
        "TECNOLÓGICO NACIONAL DE MÉXICO\n"
        "CAMPUS MATEHUALA"
    ).bold = True
    documento.add_paragraph("")
    titulo = documento.add_paragraph()
    titulo.alignment = 1
    titulo.add_run(
        "BITÁCORA\nSERVICIO DE ENFERMERÍA"
    ).bold = True
    subtitulo = documento.add_paragraph()
    subtitulo.alignment = 1
    subtitulo.add_run(
        '“CuidaTec” cuida tu salud.'
    ).italic = True
    documento.add_paragraph("")
    # Primera parte: presentación
    documento.add_paragraph(
        "El módulo “CuidaTec” tiene como titular "
        "a la Licenciada en Enfermería "
        "Mariana Alejandra Torres Mendoza, "
        "encargada del módulo."
    )
    documento.add_paragraph(
        "Dentro del módulo CuidaTec se brinda "
        "el servicio de enfermería a la población "
        "del Tecnológico Nacional de México, "
        "Campus Matehuala, mediante acciones "
        "de atención primaria a la salud."
    )
    # Problemáticas tomadas de las atenciones
    motivos = []
    for atencion in atenciones:
        motivo = (atencion["motivo_visita"] or "").strip()
        if motivo and motivo.casefold() not in [
            m.casefold() for m in motivos
        ]:
            motivos.append(motivo)
    if motivos:
        texto_motivos = "; ".join(motivos)
        documento.add_paragraph(
            f"Durante el mes de {nombre_mes} de {anio}, "
            "entre las problemáticas y motivos de "
            "atención registrados en el módulo "
            f"se encuentran: {texto_motivos}."
        )
    else:
        documento.add_paragraph(
            f"Durante el mes de {nombre_mes} de {anio} "
            "no se encontraron atenciones registradas "
            "en el sistema."
        )
    documento.add_paragraph(
        f"A continuación, se presenta la bitácora "
        f"de actividades correspondiente al mes "
        f"de {nombre_mes} de {anio}, elaborada "
        "a partir de las atenciones registradas "
        "en SIRE."
    )
    # Tercera parte: bitácora
    documento.add_heading(
        "BITÁCORA MENSUAL DE ATENCIONES",
        level=1
    )
    documento.add_paragraph(
        f"Periodo: {nombre_mes.capitalize()} de {anio}"
    )
    documento.add_paragraph(
        f"Total de atenciones: {len(atenciones)}"
    )
    tabla = documento.add_table(rows=1, cols=3)
    tabla.style = "Table Grid"
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False
    # Calcular el espacio disponible en la hoja
    ancho_disponible = (
        seccion.page_width
        - seccion.left_margin
        - seccion.right_margin
    )
    # Distribuir el ancho de las columnas
    anchos = [
        int(ancho_disponible * 0.18),
        int(ancho_disponible * 0.12),
        int(ancho_disponible * 0.70)
    ]
    for i, ancho in enumerate(anchos):
        tabla.columns[i].width = ancho
        tabla.rows[0].cells[i].width = ancho
    for celda in tabla.rows[0].cells:
        colorear_celda(celda, "C9E2F3")
    encabezados = tabla.rows[0].cells
    encabezados[0].text = "FECHA"
    encabezados[1].text = "HORA"
    encabezados[2].text = "ACTIVIDADES"
    for celda in encabezados:
        for parrafo in celda.paragraphs:
            for run in parrafo.runs:
                run.bold = True
    # Agrupar atenciones por fecha
    actividades_por_dia = {}
    for atencion in atenciones:
        fecha = atencion["fecha_atencion"].date()
        if fecha not in actividades_por_dia:
            actividades_por_dia[fecha] = []
        actividades_por_dia[fecha].append(atencion)
    # Generar las filas de la tabla
    for fecha, registros in actividades_por_dia.items():
        for registro in registros:
            fila = tabla.add_row().cells
            # Ajustar el ancho de las celdas
            for i, ancho in enumerate(anchos):
                fila[i].width = ancho
            # Alternar colores de las filas
            if len(tabla.rows) % 2 == 0:
                for celda in fila:
                    colorear_celda(celda, "EAF4FB")
            # Fecha y hora de la atención
            fila[0].text = fecha.strftime("%d/%m/%Y")
            fila[1].text = registro[
                "fecha_atencion"
            ].strftime("%H:%M")
            # Obtener los datos de la atención
            motivo = registro["motivo_visita"]
            procedimiento = registro["procedimiento"]
            observaciones = registro["observaciones"]
            # Construir la descripción
            descripcion = (
                f"Se brindó atención de enfermería "
                f"por el siguiente motivo: {motivo}. "
                f"Procedimiento realizado: {procedimiento}."
            )
            if observaciones:
                descripcion += (
                    f" Observaciones: {observaciones}."
                )
            # Agregar la actividad
            parrafo = fila[2].paragraphs[0]
            parrafo.add_run(descripcion)
            parrafo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            # Formato de las celdas
            for celda in fila:
                for p in celda.paragraphs:
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(4)
            fila[0].paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )
            fila[1].paragraphs[0].alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )
    # Si no existen atenciones
    if not atenciones:
        fila = tabla.add_row().cells
        for i, ancho in enumerate(anchos):
            fila[i].width = ancho
        fila[0].text = "—"
        fila[1].text = "—"
        fila[2].text = (
            "No se registraron atenciones "
            "durante este periodo."
        )
    # Guardar el Word en memoria
    archivo = BytesIO()
    documento.save(archivo)
    archivo.seek(0)
    nombre_archivo = (
        f"SIRE_Bitacora_{anio}_{mes:02d}.docx"
    )
    return send_file(
        archivo,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )
@app.route("/salir", methods=["POST"])
@login_required
def salir():
    logout_user()
    return redirect(url_for("inicio"))
if __name__ == "__main__":
    app.run(host="0.0.0.0" if os.getenv("RAILWAY_ENVIRONMENT_ID") else "127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
