from datetime import date
from io import StringIO, BytesIO
import csv
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
from flask import Blueprint, Response, render_template, request
from database.db import consultar
from routes.helpers import roles_permitidos
from servicios.reuniones import formatear_hora

reportes_bp=Blueprint("reportes",__name__,url_prefix="/reportes")


def _filtros():
    desde=request.args.get("desde","").strip(); hasta=request.args.get("hasta","").strip(); estado=request.args.get("estado","").strip(); fs=[]; p=[]
    from routes.helpers import usuario_actual
    usuario=usuario_actual()
    if usuario and usuario.get("rol_nombre") != "Super Admin" and usuario.get("id_institucion"):
        fs.append("c.id_institucion=%s"); p.append(usuario["id_institucion"])
    if desde: fs.append("c.fecha>=%s"); p.append(desde)
    if hasta: fs.append("c.fecha<=%s"); p.append(hasta)
    if estado: fs.append("ec.nombre=%s"); p.append(estado)
    return ((" WHERE "+" AND ".join(fs)) if fs else ""),p,desde,hasta,estado


def _filas_reporte():
    w,p,_,_,_=_filtros()
    return consultar(f"""SELECT c.id,c.fecha,c.hora,c.lugar,ec.nombre estado,m.nombre motivo,
        CONCAT(e.nombres,' ',e.apellidos) estudiante,CONCAT(d.nombres,' ',d.apellidos) docente,
        CONCAT(a.nombres,' ',a.apellidos) acudiente,c.observaciones
        FROM citas c JOIN estados_cita ec ON ec.id=c.id_estado JOIN motivos m ON m.id=c.id_motivo
        JOIN estudiantes e ON e.id_estudiante=c.id_estudiante JOIN docentes d ON d.id_docente=c.id_docente
        JOIN acudientes a ON a.id_acudiente=c.id_acudiente{w}
        ORDER BY c.fecha DESC,c.hora DESC,c.id DESC""",tuple(p))


def _valor_hoja_calculo(valor):
    if not isinstance(valor, str):
        return valor
    inicio = valor.lstrip(" \t\r\n")
    if valor.startswith(("\t", "\r", "\n")) or inicio.startswith(("=", "+", "-", "@")):
        return "'" + valor
    return valor


@reportes_bp.route("/")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def index():
    w,p,desde,hasta,estado=_filtros()
    resumen=consultar(f"SELECT COUNT(*) total,SUM(ec.nombre='Pendiente') pendientes,SUM(ec.nombre='Confirmada') confirmadas,SUM(ec.nombre='Realizada') realizadas,SUM(ec.nombre='Cancelada') canceladas,SUM(ec.nombre='No asistió') no_asistio FROM citas c JOIN estados_cita ec ON ec.id=c.id_estado{w}",tuple(p),uno=True) or {}
    citas=_filas_reporte()[:1000]
    return render_template("reportes/index.html",resumen=resumen,citas=citas,estados=consultar("SELECT nombre FROM estados_cita ORDER BY id"),desde=desde,hasta=hasta,estado=estado)


@reportes_bp.route("/exportar.csv")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def exportar_csv():
    rows=_filas_reporte(); out=StringIO(); writer=csv.writer(out); writer.writerow(["Cita","Fecha","Hora","Lugar","Estado","Motivo","Estudiante","Docente","Acudiente","Observaciones"])
    for r in rows: writer.writerow([_valor_hoja_calculo(r["id"]),_valor_hoja_calculo(r["fecha"]),_valor_hoja_calculo(formatear_hora(r["hora"])),_valor_hoja_calculo(r["lugar"]),_valor_hoja_calculo(r["estado"]),_valor_hoja_calculo(r["motivo"]),_valor_hoja_calculo(r["estudiante"]),_valor_hoja_calculo(r["docente"]),_valor_hoja_calculo(r["acudiente"]),_valor_hoja_calculo(r["observaciones"] or "")])
    return Response("\ufeff"+out.getvalue(),mimetype="text/csv; charset=utf-8",headers={"Content-Disposition":f'attachment; filename="eduturnos_reporte_{date.today().isoformat()}.csv"'})


def _celda_word(valor, encabezado=False):
    texto = escape(str(valor if valor is not None else ""))
    negrita = "<w:rPr><w:b/></w:rPr>" if encabezado else ""
    sombreado = '<w:shd w:fill="EAF3FF"/>' if encabezado else ""
    return (
        f"<w:tc><w:tcPr>{sombreado}<w:tcW w:w=\"1400\" w:type=\"dxa\"/></w:tcPr>"
        f"<w:p><w:r>{negrita}<w:t xml:space=\"preserve\">{texto}</w:t></w:r></w:p></w:tc>"
    )


def _crear_docx_reporte(rows):
    encabezados = ("Cita", "Fecha", "Hora", "Lugar", "Estado", "Motivo", "Estudiante", "Docente", "Acudiente", "Observaciones")
    claves = ("id", "fecha", "hora", "lugar", "estado", "motivo", "estudiante", "docente", "acudiente", "observaciones")
    filas = ["<w:tr>" + "".join(_celda_word(valor, True) for valor in encabezados) + "</w:tr>"]
    for registro in rows:
        valores = [registro.get(clave) for clave in claves]
        valores[2] = formatear_hora(valores[2])
        filas.append("<w:tr>" + "".join(_celda_word(valor or "") for valor in valores) + "</w:tr>")
    documento = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body><w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="30"/></w:rPr>'
        '<w:t>EDUTURNOS - Reporte de citaciones</w:t></w:r></w:p>'
        '<w:tbl><w:tblPr><w:tblW w:w="14000" w:type="dxa"/><w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:color="B8CDE5"/><w:left w:val="single" w:sz="4" w:color="B8CDE5"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="B8CDE5"/><w:right w:val="single" w:sz="4" w:color="B8CDE5"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="B8CDE5"/><w:insideV w:val="single" w:sz="4" w:color="B8CDE5"/>'
        '</w:tblBorders></w:tblPr><w:tblGrid>' + '<w:gridCol w:w="1400"/>' * 10 + '</w:tblGrid>'
        + "".join(filas)
        + '</w:tbl><w:sectPr><w:pgSz w:w="16838" w:h="11906" w:orient="landscape"/>'
        '<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="360" w:footer="360" w:gutter="0"/>'
        '</w:sectPr></w:body></w:document>'
    )
    tipos = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>')
    relaciones = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>')
    salida = BytesIO()
    with ZipFile(salida, "w", ZIP_DEFLATED) as archivo:
        archivo.writestr("[Content_Types].xml", tipos)
        archivo.writestr("_rels/.rels", relaciones)
        archivo.writestr("word/document.xml", documento)
    return salida.getvalue()


@reportes_bp.route("/exportar.docx")
@roles_permitidos("Super Admin", "Rector", "Administrador / Coordinador")
def exportar_word():
    contenido = _crear_docx_reporte(_filas_reporte())
    return Response(
        contenido,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="eduturnos_reporte_{date.today().isoformat()}.docx"'},
    )


@reportes_bp.route("/exportar.xlsx")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def exportar_xlsx():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment
    except ImportError:
        return Response("La exportación Excel no está instalada. Ejecuta la instalación de dependencias.",status=503,mimetype="text/plain")
    rows=_filas_reporte(); wb=Workbook(); ws=wb.active; ws.title="Citaciones"; headers=["Cita","Fecha","Hora","Lugar","Estado","Motivo","Estudiante","Docente","Acudiente","Observaciones"]; ws.append(headers)
    for cell in ws[1]: cell.font=Font(bold=True); cell.alignment=Alignment(horizontal="center")
    for r in rows: ws.append([_valor_hoja_calculo(r["id"]),_valor_hoja_calculo(r["fecha"]),_valor_hoja_calculo(formatear_hora(r["hora"])),_valor_hoja_calculo(r["lugar"]),_valor_hoja_calculo(r["estado"]),_valor_hoja_calculo(r["motivo"]),_valor_hoja_calculo(r["estudiante"]),_valor_hoja_calculo(r["docente"]),_valor_hoja_calculo(r["acudiente"]),_valor_hoja_calculo(r["observaciones"] or "")])
    for column in ws.columns:
        width=min(max(max(len(str(c.value or "")) for c in column)+2,10),40); ws.column_dimensions[column[0].column_letter].width=width
    out=BytesIO(); wb.save(out); out.seek(0)
    return Response(out.getvalue(),mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":f'attachment; filename="eduturnos_reporte_{date.today().isoformat()}.xlsx"'})


@reportes_bp.route("/exportar.pdf")
@roles_permitidos("Super Admin","Rector","Administrador / Coordinador")
def exportar_pdf():
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    except ImportError:
        return Response("La exportación PDF no está instalada. Ejecuta la instalación de dependencias.",status=503,mimetype="text/plain")
    rows=_filas_reporte(); buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=landscape(A4),rightMargin=24,leftMargin=24,topMargin=24,bottomMargin=24); styles=getSampleStyleSheet(); story=[Paragraph("EDUTURNOS · Reporte de citaciones",styles["Title"]),Spacer(1,10)]
    data=[["#","Fecha","Hora","Estado","Motivo","Estudiante","Docente","Lugar"]]
    for r in rows: data.append([str(r["id"]),str(r["fecha"]),formatear_hora(r["hora"]),r["estado"],r["motivo"],r["estudiante"],r["docente"],r["lugar"]])
    table=Table(data,repeatRows=1,colWidths=[30,65,55,75,90,130,130,130]); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#165dca")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#dce3ed")),("FONTSIZE",(0,0),(-1,-1),7),("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(table); doc.build(story); buf.seek(0)
    return Response(buf.getvalue(),mimetype="application/pdf",headers={"Content-Disposition":f'attachment; filename="eduturnos_reporte_{date.today().isoformat()}.pdf"'})
