import json
from datetime import datetime, timedelta
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(record, file_path="triava_report.pdf", instansi=""):

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)

    story = []

    # ======================
    # PARSE DATA
    # ======================
    vital = json.loads(record.get("vital", "{}"))
    abcde = json.loads(record.get("abcde", "{}"))

    masalah = record.get("masalah", [])
    if isinstance(masalah, str):
        try:
            masalah = json.loads(masalah)
        except:
            masalah = []

    # ======================
    # HEADER (UPGRADED)
    # ======================
    story.append(Paragraph(f"<b>{instansi.upper()}</b>", styles["Heading1"]))
    story.append(Paragraph("TRIAGE EMERGENCY REPORT (ATS)", styles["Heading2"]))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<hr/>", styles["Normal"]))
    story.append(Spacer(1, 2))

    created_at = record.get("created_at")

    try:
        dt = datetime.fromisoformat(str(created_at))
        dt = dt + timedelta(hours=7)  
        waktu = dt.strftime("%d-%m-%Y %H:%M")
    except:
        waktu = str(created_at)

    story.append(Paragraph(f"Tanggal Triase: {waktu} WIB", styles["Normal"]))
    story.append(Spacer(1, 4))

    # ======================
    # IDENTITAS (CLEAN)
    # ======================
    identitas_data = [
        ["Nama Pasien", record.get("nama_pasien", "")],
        ["Umur", record.get("umur", "")],
    ]

    identitas_table = Table(identitas_data, colWidths=[150, 250])
    identitas_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
    ]))

    story.append(Paragraph("<b>IDENTITAS</b>", styles["Heading2"]))
    story.append(identitas_table)
    story.append(Spacer(1, 4))

    # ======================
    # VITAL SIGN
    # ======================
    vital_data = [
        ["TD", f"{vital.get('td_sys','')}/{vital.get('td_dia','')}"],
        ["Nadi", str(vital.get("nadi",""))],
        ["RR", str(vital.get("rr",""))],
        ["Suhu", str(vital.get("suhu",""))],
        ["SpO2", str(vital.get("spo2",""))],
    ]

    vital_table = Table(vital_data, colWidths=[150, 250])
    vital_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
    ]))

    story.append(Paragraph("<b>VITAL SIGN</b>", styles["Heading2"]))
    story.append(vital_table)
    story.append(Spacer(1, 4))

    # ======================
    # ABCDE
    # ======================
    abcde_data = [
        ["Airway", abcde.get("airway","")],
        ["Breathing", abcde.get("breathing","")],
        ["Circulation", abcde.get("circulation","")],
        ["Disability", abcde.get("avpu","")],
        ["Exposure", abcde.get("exposure","")],
    ]

    abcde_table = Table(abcde_data, colWidths=[150, 250])
    abcde_table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.3, colors.grey),
    ]))

    story.append(Paragraph("<b>PRIMARY SURVEY (ABCDE)</b>", styles["Heading2"]))
    story.append(abcde_table)
    story.append(Spacer(1, 4))

    # ======================
    # TRIASE (FOCUS - ATS STYLE)
    # ======================
    triage = record.get("triage_result", "UNKNOWN")

    triage_label_map = {
        "RED": "ATS 1 - MERAH (RESUSITASI)",
        "YELLOW": "ATS 3 - KUNING (URGENT)",
        "GREEN": "ATS 5 - HIJAU (NON-URGENT)",
    }

    triage_text = triage_label_map.get(triage, triage)

    color_map = {
        "RED": colors.red,
        "YELLOW": colors.orange,
        "GREEN": colors.green,
    }

    story.append(Paragraph("<b>TRIAGE CATEGORY (ATS)</b>", styles["Heading2"]))

    triage_table = Table([[triage_text]], colWidths=[400])
    triage_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color_map.get(triage, colors.grey)),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 12),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))

    story.append(triage_table)
    story.append(Spacer(1, 4))

    # ======================
    # MASALAH
    # ======================
    story.append(Paragraph("<b>MASALAH KLINIS</b>", styles["Heading2"]))

    for m in masalah:
        story.append(Paragraph(f"- {m}", styles["Normal"]))

    story.append(Spacer(1, 6))

    # ======================
    # PLAN
    # ======================
    story.append(Paragraph("<b>TATALAKSANA AWAL</b>", styles["Heading2"]))
    story.append(Paragraph(record.get("plan", ""), styles["Normal"]))

    # ======================
    # FOOTER (LEGAL FEEL)
    # ======================
    story.append(Spacer(1, 4))
    story.append(Paragraph("<hr/>", styles["Normal"]))

    story.append(Paragraph(
        f"Petugas: {record.get('petugas','')}", styles["Normal"]
    ))

    story.append(Paragraph(
        f"Waktu: {waktu} WIB", styles["Normal"]
    ))

    story.append(Paragraph(
        f"Generated by Triava - {instansi}", styles["Normal"]
    ))

    # ======================
    # BUILD
    # ======================
    doc.build(story)

    return file_path