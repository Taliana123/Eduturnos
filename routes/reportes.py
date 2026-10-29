from datetime import date
from io import StringIO, BytesIO
import csv
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
