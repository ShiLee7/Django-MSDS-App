from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import Table, TableStyle, Spacer, BaseDocTemplate, Frame, PageTemplate, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from io import BytesIO
from app1.models import ChemTable
from django.contrib.staticfiles import finders
from reportlab.lib.units import inch

import datetime

def generate_chemtable_pdf(request, chemtable_id):
    chemtable = get_object_or_404(ChemTable, id=chemtable_id)
    chemicals = chemtable.chemicals.all()

    buffer = BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=landscape(A4),  # Landscape orientation
        rightMargin=36,
        leftMargin=36,
        topMargin=72,
        bottomMargin=72,
        title="Cuadro de constantes",
        author="Extraction Solutions",
        subject="Chemtable"
    )

    def watermark_canvas(canvas, doc):
        w_path = finders.find('images/watermark_logo.png')
        if w_path:
            page_width, page_height = landscape(A4)
            canvas.saveState()
            canvas.drawImage(w_path, 0, 0, width=page_width, height=page_height, preserveAspectRatio=True, mask='auto')
            canvas.restoreState()

    def header_canvas(canvas, doc):
        logo_path = finders.find('images/ExtracSol.png')
        if logo_path:
            logo_width = 0.9 * inch
            logo_height = 0.9 * inch
            x = 0.5 * inch
            y = landscape(A4)[1] - logo_height - 10  # Pega el logo arriba
            canvas.saveState()
            canvas.drawImage(
                logo_path, x, y,
                width=logo_width, height=logo_height,
                preserveAspectRatio=True, mask='auto'
            )
            canvas.restoreState()

    def footer_canvas(canvas, doc):
        canvas.saveState()
        footer_text = f"Generado el {datetime.datetime.now().strftime('%Y-%m-%d')} | Página {doc.page}"
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(landscape(A4)[0] - 36, 20, footer_text)
        canvas.restoreState()

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')

    def combined_onPage(canvas, doc):
        watermark_canvas(canvas, doc)
        header_canvas(canvas, doc)

    page_template = PageTemplate(id='main', frames=[frame], onPage=combined_onPage, onPageEnd=footer_canvas)
    doc.addPageTemplates([page_template])

    styles = getSampleStyleSheet()
    cell_style = ParagraphStyle(
    name='TableCell',
    fontSize=8,
    leading=10,
    alignment=1,  # 1 is TA_CENTER for horizontal centering
    spaceAfter=0,
    spaceBefore=0,
    )

    header_style = ParagraphStyle(
    name='TableHeader',
    parent=cell_style,
    fontName='Helvetica-Bold',
    backColor='#FFC300',  # yellow background
    )

    story = []

    styles = getSampleStyleSheet()
    story.append(Paragraph(f"<b>Cuadro de constantes</b>", styles['Title']))
    story.append(Spacer(1, 12))

    # Columnas igual que tu HTML
    header_cells = [
    "Número CAS", "Nombre", "Fórmula Molecular", "Pto de Ebullición",
    "Densidad", "Pto de Fusión", "Estado Físico", "Solubilidad", "Toxicidad"
    ]
    data = [
        [Paragraph(str(h), header_style) for h in header_cells]
    ]

    for chem in chemicals:
        data.append([
            Paragraph(str(chem.cas_number), cell_style),
            Paragraph(str(chem.chemical_name), cell_style),
            Paragraph(str(chem.molecular_formula), cell_style),
            Paragraph(str(chem.boiling_point), cell_style),
            Paragraph(str(chem.density), cell_style),
            Paragraph(str(chem.t_change), cell_style),
            Paragraph(str(chem.phys), cell_style),
            Paragraph(str(chem.solubility), cell_style),
            Paragraph(str(chem.acute_toxicity_estimates), cell_style),
        ])

    page_width, _ = landscape(A4)
    usable_width = page_width - doc.leftMargin - doc.rightMargin

    col_widths = [
        0.10, 0.17, 0.12, 0.10, 0.10, 0.11, 0.12, 0.09, 0.09
    ]
    column_widths = [usable_width * w for w in col_widths]

    table = Table(data, repeatRows=1, hAlign='LEFT', colWidths=column_widths)
    table.setStyle(TableStyle([
        # Background and color for headers
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FFC300")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        # Alignment for all cells (including headers)
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        # Font and size
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        # Table grid and row backgrounds
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.whitesmoke, colors.lightgrey]),
        # Wordwrap for all cells
        ('WORDWRAP', (0,0), (-1,-1), 'CJK'),
    ]))

    story.append(table)

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Cuadro_de_constantes_{chemtable_id}.pdf"'
    response.write(pdf)
    return response