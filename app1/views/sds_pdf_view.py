from django.shortcuts import render, redirect, get_object_or_404
from app1.forms import *
from app1.models import *
from app1.constants import *
from app1.utils import *
from django.utils.html import escapejs
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Frame, PageTemplate, Flowable, Image as RLImage, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from django.contrib.staticfiles import finders
from io import BytesIO
from django.http import HttpResponse

import datetime

def generate_msds_pdf(request, msds_id):
    msds = get_object_or_404(MSDS, id=msds_id)

    buffer = BytesIO()

    # Define the document using BaseDocTemplate for custom layouts
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=72,
        bottomMargin=72,
        title="Safety Data Sheet",
        author="Extraction Solutions",
        subject="SDS"
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="SectionHeading", fontName="Helvetica-Bold", fontSize=16, spaceAfter=12))
    styles.add(ParagraphStyle(name="SubHeading", fontName="Helvetica-Bold", fontSize=13, spaceAfter=8))
    styles.add(ParagraphStyle(name="FieldLabel", fontName="Helvetica-Bold", fontSize=10, textColor=colors.black))
    styles.add(ParagraphStyle(name="FieldValue", fontName="Helvetica", fontSize=10))
    styles.add(ParagraphStyle(name="Footer", alignment=2, fontSize=8, textColor=colors.grey))

    # Watermark function: Draws a large version of the logo as a background.
    def watermark_canvas(canvas, doc):
        w_path = finders.find('images/watermark_logo.png')
        if w_path:
            page_width, page_height = A4
            canvas.saveState()
            # Scale the image to cover the page
            # If your image is transparent or lightened, it will appear as a watermark.
            canvas.drawImage(w_path, 0, 0, width=page_width, height=page_height, preserveAspectRatio=True, mask='auto')
            canvas.restoreState()

    # Header function to draw the small logo outside margins (as done before)
    def header_canvas(canvas, doc):
        logo_path = finders.find('images/ExtracSol.png')
        if logo_path:
            page_width, page_height = A4

            # Adjust the image size slightly smaller
            logo_width = 0.9 * inch  # ~64.8 points
            logo_height = 0.9 * inch

            # Place the image near the top, above the text frame
            # The text frame starts at ~769.89 pt from bottom.
            # We'll place the image bottom at 775 pt to ensure no overlap.
            x = 0.5 * inch
            y = 775

            canvas.saveState()
            canvas.drawImage(
                logo_path, x, y,
                width=logo_width, height=logo_height,
                preserveAspectRatio=True, mask='auto'
            )
            canvas.restoreState()


    # Footer function to draw footer text
    def footer_canvas(canvas, doc):
        canvas.saveState()
        footer_text = f"SDS generated on {datetime.datetime.now().strftime('%Y-%m-%d')} | Page {doc.page}"
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(A4[0] - 36, 20, footer_text)
        canvas.restoreState()

    # Create a Frame for the main content with the defined margins
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')

    # Create a PageTemplate that uses the frame.
    # - onPage=watermark_canvas will draw the background first
    # - After that, onPage=header_canvas can also be called. If you need both watermark and header,
    #   combine both calls or call one after another.
    # Here we chain them by drawing the watermark first, then the header.
    def combined_onPage(canvas, doc):
        watermark_canvas(canvas, doc)
        header_canvas(canvas, doc)


    page_template = PageTemplate(id='main', frames=[frame], onPage=combined_onPage, onPageEnd=footer_canvas)
    doc.addPageTemplates([page_template])

    # Build the story
    story = []
    story.append(Paragraph("Safety Data Sheet (SDS)", styles["Title"]))
    story.append(Spacer(1, 0.2*inch))
    sec1_header = Paragraph("Section 1: Identification", styles["SectionHeading"])

    fields = [
    ("Product Name:", msds.product_name),
    ("Product Number:", msds.product_number),
    ("Index Number:", msds.index_number),
    ("REACH No:", msds.reach_no),
    ("CAS Number:", msds.cas_number),
    ("Manufacturer Name:", msds.manufacturer_name),
    ("Manufacturer Address:", msds.manufacturer_address),
    ("Phone Number:", msds.phone_number),
    ("Emergency Phone:", msds.emergency_phone),
    ("Recommended Use:", msds.recommended_use),
    ("Restrictions on Use:", msds.restrictions_on_use)
        ]

    data = []
    for label, value in fields:
        # If value is empty or None, default to "N/A"
        val = value.strip() if value else ""  # Ensure we handle None safely
        if val:  # Only add the row if val is not empty after stripping
            data.append([
                Paragraph(label, styles["FieldLabel"]), 
                Paragraph(val, styles["FieldValue"])
            ])

    table_sec1 = Table(data, colWidths=[2*inch, 4*inch])
    table_sec1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
        ('INNERGRID', (0,0), (-1,-1), 0.33, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))

    spacer_bet_secs = Spacer(1, 0.2*inch)
    spacer_inbet = Spacer(1, 0.1*inch)
    sec1 = KeepTogether([sec1_header, spacer_inbet, table_sec1])    
    story.append(sec1)

    # Section 2 Heading
    sec2_heading = Paragraph("Section 2: Hazard(s) Identification", styles["SectionHeading"])

    # Classification and Hazard Statements
    classifications_str = msds.classification or ""
    classification_bullets = process_statements(classifications_str) if classifications_str else "N/A"

    h_str = msds.hazard_statements or ""
    h_b = process_statements(h_str) if h_str else "N/A"

    section2_data = [
        [Paragraph("Classification:", styles["FieldLabel"]),
        Paragraph(classification_bullets, styles["FieldValue"])],
        [Paragraph("Hazard Statements:", styles["FieldLabel"]),
        Paragraph(h_b, styles["FieldValue"])]
    ]

    section2_table = Table(section2_data, colWidths=[2 * inch, 4 * inch])
    section2_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
    ]))

    sec2_head_table1 = KeepTogether([sec2_heading, spacer_inbet, section2_table])
    story.append(sec2_head_table1)
    story.append(spacer_inbet)

    # Label Elements

    label_elements = msds.label_elements or []
    if label_elements:
        label_sec2_head = Paragraph("Label Elements", styles["SubHeading"])
        images = []
        for element in label_elements:
            desc = element.get("description")
            if desc in DESC_TO_IMAGE:
                logger.debug(f"DESC_TO_IMAGE[desc]: {DESC_TO_IMAGE[desc]}")
                logger.debug(f"type(DESC_TO_IMAGE[desc]): {type(DESC_TO_IMAGE[desc])}")
                img_path = finders.find(DESC_TO_IMAGE[desc])
                logger.debug(f"img_path: {img_path}")
                if img_path:
                    rotated_img = RotatedImage(img_path, angle=-45, scale=0.10)
                    images.append(rotated_img)

        max_per_row = 3
        image_rows = [images[i:i + max_per_row] for i in range(0, len(images), max_per_row)]
        
        if image_rows:
            # For the first row, keep the label and the table together.
            first_row_table = Table(
                data=[image_rows[0]],  # First row of images
                colWidths=[1.5 * inch] * len(image_rows[0])
            )
            first_row_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 16),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 16)
            ]))
            # Keep the header, spacer and first row table together on the same page.
            story.append(KeepTogether([label_sec2_head, spacer_inbet, first_row_table]))
            
            # For additional rows, add each row separately (without repeating the label).
            for row_images in image_rows[1:]:
                row_table = Table(
                    data=[row_images],
                    colWidths=[1.5 * inch] * len(row_images)
                )
                row_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 16),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 16)
                ]))
                story.append(KeepTogether([row_table]))

        # Add a fallback message if no images are provided
        if not images:
            story.append(Paragraph("No label elements provided.", styles["FieldValue"]))

    story.append(spacer_inbet)

    # Signal Word
    signal_word = f"""<para align="center"><font size=10>
    <b>Signal Word:</b>&nbsp;{msds.signal_word}</font></para>"""
    story.append(Paragraph(signal_word, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    # Precautionary Statements
    precau_subh = Paragraph("Precautionary Statements", styles["SubHeading"])

    # Process precautionary statements
    general_bullets = process_statements(msds.general_statements)
    prevention_bullets = process_statements(msds.prevention_statements)
    response_bullets = process_statements(msds.response_statements)
    storage_bullets = process_statements(msds.storage_statements)
    disposal_bullets = process_statements(msds.disposal_statements)

    precautionary_data = []
    if general_bullets:
        precautionary_data.append([Paragraph("General:", styles["FieldLabel"]),
                                Paragraph(general_bullets, styles["FieldValue"])])
    if prevention_bullets:
        precautionary_data.append([Paragraph("Prevention:", styles["FieldLabel"]),
                                Paragraph(prevention_bullets, styles["FieldValue"])])
    if response_bullets:
        precautionary_data.append([Paragraph("Response:", styles["FieldLabel"]),
                                Paragraph(response_bullets, styles["FieldValue"])])
    if storage_bullets:
        precautionary_data.append([Paragraph("Storage:", styles["FieldLabel"]),
                                Paragraph(storage_bullets, styles["FieldValue"])])
    if disposal_bullets:
        precautionary_data.append([Paragraph("Disposal:", styles["FieldLabel"]),
                                Paragraph(disposal_bullets, styles["FieldValue"])])

    if precautionary_data:
        precautionary_table = Table(precautionary_data, colWidths=[2 * inch, 4 * inch])
        precautionary_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        precau = KeepTogether([precau_subh, spacer_inbet, precautionary_table])
        story.append(precau)

    else:
        story.append(Paragraph("No precautionary statements provided.", styles["FieldValue"]))
    story.append(spacer_bet_secs)

    if msds.other_hazards != '':
        honc_text = f"""<para align="justify"><font size=10>
        <b>Hazards not otherwise classified (HNOC):</b>{msds.other_hazards} 
        </font></para>"""
        story.append(Paragraph(honc_text, styles["Normal"]))
        story.append(spacer_bet_secs)

    # Section 3
    sec3_h = Paragraph("Section 3: Composition/information on ingredients", styles["SectionHeading"])

    section3_data = []

    # Define headers
    section3_headers = [
        Paragraph("Substance/Mixture", styles["FieldLabel"]),
        Paragraph("Chemical Name", styles["FieldLabel"]),
        Paragraph("Synonyms", styles["FieldLabel"]),
        Paragraph("Concentration", styles["FieldLabel"]),
        Paragraph("Other Identifiers", styles["FieldLabel"]),
    ]
    section3_data.append(section3_headers)

    # Define values
    s_or_m = msds.substance_or_mixture
    substance_or_mixture = Paragraph("Substance", styles["FieldValue"]) if s_or_m == 'substance' else Paragraph("Mixture", styles["FieldValue"])

    section3_values = [
        substance_or_mixture,
        Paragraph(msds.chemical_name or '', styles["FieldValue"]),
        Paragraph(msds.synonyms or '', styles["FieldValue"]),
        Paragraph(msds.concentration or '', styles["FieldValue"]),
        Paragraph(msds.other_unique_identifiers or '', styles["FieldValue"])
    ]
    section3_data.append(section3_values)

    page_width, _ = A4
    usable_width = page_width - 36 - 36

    # Adjust column widths
    col_widths_sec3 = [usable_width * 0.2,  # 20% for "Substance/Mixture"
                usable_width * 0.25, # 25% for "Chemical Name"
                usable_width * 0.2,  # 20% for "Synonyms"
                usable_width * 0.15,  # 20% for "Concentration"
                usable_width * 0.20] # 15% for "Other Identifiers"

    # Create table
    section3_table = Table(section3_data, colWidths=col_widths_sec3)
    section3_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Border for the entire table
    ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align everything horizontally
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align everything vertically
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))


    sec3 = KeepTogether([sec3_h, section3_table, spacer_bet_secs])
    story.append(sec3)

    # Section 4
    sec4_h = Paragraph("Section 4: First aid measures", styles["SectionHeading"])

    section4_data = []

    section4_headers = [
        Paragraph("Exposure route", styles["FieldLabel"]),
        Paragraph("Symptom", styles["FieldLabel"]),
        Paragraph("Medical attention", styles["FieldLabel"])
    ]
    section4_data.append(section4_headers)

    # Define values

    section4_data.append([Paragraph("Inhalation",styles["FieldLabel"]),
    Paragraph(msds.symp_inhal,styles["FieldValue"]),
    Paragraph(msds.aid_inhal,styles["FieldValue"])
    ])

    section4_data.append([Paragraph("Ingestion",styles["FieldLabel"]),
    Paragraph(msds.symp_inges,styles["FieldValue"]),
    Paragraph(msds.aid_inges,styles["FieldValue"])
    ])

    section4_data.append([Paragraph("Eye Contact",styles["FieldLabel"]),
    Paragraph(msds.symp_eye,styles["FieldValue"]),
    Paragraph(msds.aid_eye,styles["FieldValue"])
    ])

    section4_data.append([Paragraph("Skin contact",styles["FieldLabel"]),
    Paragraph(msds.symp_skin,styles["FieldValue"]),
    Paragraph(msds.aid_skin,styles["FieldValue"])
    ])

    col_widths_sec4 = [usable_width * 0.2,  
                usable_width * 0.4, 
                usable_width * 0.4]       

    # Create table
    section4_table = Table(section4_data, colWidths=col_widths_sec4, repeatRows=1)

    section4_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Border for the entire table
    ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align everything horizontally
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align everything vertically
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))

    sec4 = KeepTogether([sec4_h, spacer_inbet, section4_table])

    if msds.immediate_attention != '':
        fa_text = f"""<para align="justify"><font size=10>
        <b>Indication of immediate medical attention and special treatment needed:</b>{msds.immediate_attention} 
        </font></para>"""
        fa_text_flow = Paragraph(fa_text, styles["Normal"])
        story.append(sec4)
        story.append(fa_text_flow)
        story.append(spacer_bet_secs)
    else:
        story.append(sec4)
        story.append(spacer_bet_secs)
        

    # Section 5
    section5_header = Paragraph("Section 5: Fire-fighting measures", styles["SectionHeading"])
    section5_spacer = Spacer(1, 0.1 * inch)

    section5_data = []

    # Define values
    section5_data.append([Paragraph("Extinguishing Media", styles["FieldLabel"]),
                        Paragraph(process_statements(msds.suitable_extinguishing_media), styles["FieldValue"])])

    section5_data.append([Paragraph("Specific hazards arising from the chemical", styles["FieldLabel"]),
                        Paragraph(msds.specific_hazards_arising, styles["FieldValue"])])

    section5_data.append([Paragraph("Special protective measures to control fire", styles["FieldLabel"]),
                        Paragraph(process_statements(msds.special_protective_actions), styles["FieldValue"])])

    # Create table
    section5_table = Table(section5_data)

    section5_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Border for the entire table
        ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Highlight header row
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align everything horizontally
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align everything vertically
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))

    # Group header and table with KeepTogether
    section5 = KeepTogether([section5_header, section5_spacer, section5_table])
    story.append(section5)
    story.append(Spacer(1, 0.2 * inch))

    # Section 6
    section6_header = Paragraph("Section 6: Accidental release measures", styles["SectionHeading"])
    section6_spacer = Spacer(1, 0.1 * inch)

    section6_data = []

    # Define values
    if msds.personal_precautions != '':
        section6_data.append([Paragraph("Personal Precautions", styles["FieldLabel"]),
                            Paragraph(process_statements(msds.personal_precautions), styles["FieldValue"])])

    if msds.protective_equipment != '':
        section6_data.append([Paragraph("Protective Equipment", styles["FieldLabel"]),
                            Paragraph(msds.protective_equipment, styles["FieldValue"])])

    if msds.emergency_procedures != '':
        section6_data.append([Paragraph("Emergency Procedures", styles["FieldLabel"]),
                            Paragraph(msds.emergency_procedures, styles["FieldValue"])])

    if msds.environmental_precautions != '':
        section6_data.append([Paragraph("Environmental Precautions", styles["FieldLabel"]),
                            Paragraph(msds.environmental_precautions, styles["FieldValue"])])

    if msds.methods_and_materials_for_containment != '':
        section6_data.append([Paragraph("Methods and Materials for Containment", styles["FieldLabel"]),
                            Paragraph(msds.methods_and_materials_for_containment, styles["FieldValue"])])

    # Create table
    if len(section6_data) > 1:
        section6_table = Table(section6_data)

        section6_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Border for the entire table
            ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Highlight header row
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align everything horizontally
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align everything vertically
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))

        # Group header and table with KeepTogether
        section6 = KeepTogether([section6_header, section6_spacer, section6_table])
        story.append(section6)
        story.append(spacer_bet_secs)

    #Section 7

    section7_header = Paragraph("Section 7: Handling and storage", styles["SectionHeading"])
    section7_spacer = Spacer(1, 0.1 * inch)

    section7_data = []

    section7_data.append([Paragraph("Precautions for safe handling", styles["FieldLabel"]),
                            Paragraph("Conditions for safe storage", styles["FieldLabel"])])

    section7_data.append([Paragraph(process_statements(msds.precautions_for_safe_handling), styles["FieldValue"]),
                            Paragraph(msds.conditions_for_safe_storage, styles["FieldValue"])])

    col_widths_sec7 = [usable_width * 0.45,
                usable_width * 0.55]

    # Create table
    section7_table = Table(section7_data, colWidths=col_widths_sec7)
    section7_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Border for the entire table
    ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align everything horizontally
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align everything vertically
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))


    section7 = KeepTogether([section7_header, section7_spacer, section7_table])
    story.append(section7)
    story.append(Spacer(1, 0.2 * inch))

    #Section 8

    section8_header = Paragraph("Section 8: Exposure Controls/Personal Protection", styles["SectionHeading"])
    section8_spacer = Spacer(1, 0.1 * inch)

    section8_data = []

    section8_data.append([Paragraph("Control parameters", styles["FieldLabel"]),
                            Paragraph("Appropriate engineering controls", styles["FieldLabel"]),
                            Paragraph("Individual protection measures", styles["FieldLabel"])
                            ])
                        
    section8_data.append([Paragraph(msds.control_parameters, styles["FieldValue"]),
    Paragraph(msds.appropriate_engineering_controls, styles["FieldValue"]),
    Paragraph(msds.individual_protection_measures, styles["FieldValue"])
    ])

    col_widths_sec8 = [usable_width * 0.33,
                usable_width * 0.33,
                usable_width * 0.33]

    # Create table
    section8_table = Table(section8_data, colWidths=col_widths_sec8)
    section8_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Border for the entire table
    ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align everything horizontally
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align everything vertically
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))


    section8 = KeepTogether([section8_header, section8_spacer, section8_table])
    story.append(section8)
    story.append(Spacer(1, 0.2 * inch))

    #Section 9

    section9_header = Paragraph("Section 9: Physical and chemical properties", styles["SectionHeading"])
    section9_spacer = Spacer(1, 0.1 * inch)

    section9_data = []

    # Add header row
    section9_data.append([
        Paragraph("Property", styles["FieldLabel"]),
        Paragraph("Value", styles["FieldLabel"])
    ])

    # List of values with conditions to skip empty fields
    section9_values = [
        ("Physical State/Appearance:", msds.phys),
        ("Colour:", msds.colour),
        ("Odor:", msds.odor),
        ("pH:", msds.pH),
        ("Melting Point/Freezing Point:", msds.t_change),
        ("Boiling Point:", msds.boiling_point),
        ("Flash Point:", msds.flash_point),
        ("Evaporation Rate:", msds.evaporation_rate),
        ("Flammability Information:", msds.flammability_information),
        ("Vapor Pressure:", msds.vapor_pressure),
        ("Density and/or Relative Density:", msds.density),
        ("Relative Vapour Density:", msds.relative_vapour_density),
        ("Solubility:", msds.solubility),
        ("Partition Coefficient (n-octanol/water):", msds.partition),
        ("Auto-Ignition Temperature:", msds.auto_ignition_temperature),
        ("Decomposition Temperature:", msds.decomposition_temperature),
        ("Kinematic Viscosity:", msds.kinematic_viscosity),
        ("Particle Characteristics:", msds.particle_characteristics)
    ]

    # Add only non-empty values to section9_data
    for label, value in section9_values:
        if value:  # Skip blank or None values
            section9_data.append([
                Paragraph(label, styles["FieldLabel"]),
                Paragraph(value, styles["FieldValue"])
            ])

    # Define column widths
    col_widths_sec9 = [usable_width * 0.45, usable_width * 0.55]

    # Create the table
    section9_table = Table(section9_data, colWidths=col_widths_sec9)

    section9_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Outer border
    ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Highlight first column
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align content
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align vertically
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))


    # Group header and table with KeepTogether
    section9 = KeepTogether([section9_header, section9_spacer, section9_table])
    story.append(section9)
    story.append(Spacer(1, 0.2 * inch))

    #Section 10

    section10_header = Paragraph("Section 10: Stability and Reactivity", styles["SectionHeading"])
    section10_spacer = Spacer(1, 0.1 * inch)

    section10_data = []    

    section10_data.append([
        Paragraph("Property", styles["FieldLabel"]),
        Paragraph("Value", styles["FieldLabel"])
    ])

    section10_values = [
        ("Reactivity:", msds.reactivity),
        ("Chemical stability:", msds.chemical_stability),
        ("Possibility of hazardous reactions:", msds.possibility_of_hazardous_reactions),
        ("Conditions to avoid:", msds.conditions_to_avoid),
        ("Incompatible materials:", msds.incompatible_materials),
        ("Hazardous decomposition products:", msds.hazardous_decomposition_products)
    ]

    # Add only non-empty values to section9_data
    for label, value in section10_values:
        if value:  # Skip blank or None values
            section10_data.append([
                Paragraph(label, styles["FieldLabel"]),
                Paragraph(value, styles["FieldValue"])
            ])

    # Define column widths
    col_widths_sec10 = [usable_width * 0.45, usable_width * 0.55]

    # Create the table
    section10_table = Table(section10_data, colWidths=col_widths_sec10)

    section10_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Outer border
    ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Highlight first column
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align content
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align vertically
    ('LEFTPADDING', (0, 0), (-1, -1), 4),
    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))


    # Group header and table with KeepTogether
    section10 = KeepTogether([section10_header, section10_spacer, section10_table])
    story.append(section10)
    story.append(Spacer(1, 0.2 * inch))

    # Section 11: Toxicological Information
    section11_header = Paragraph("Section 11: Toxicological Information", styles["SectionHeading"])
    section11_spacer = Spacer(1, 0.1 * inch)

    section11_data = []

    # Add header row
    section11_data.append([
        Paragraph("Property", styles["FieldLabel"]),
        Paragraph("Value", styles["FieldLabel"])
    ])

    # Define section11_values with new fields
    section11_values = [
        ("Inhalation Route of Exposure:", msds.inhalation_route),
        ("Ingestion Route of Exposure:", msds.ingestion_route),
        ("Skin Contact Route of Exposure:", msds.skin_contact_route),
        ("Eye Contact Route of Exposure:", msds.eye_contact_route),
        ("Symptoms Related to Physical, Chemical, and Toxicological Characteristics:", msds.symptoms),
        ("Delayed Effects:", msds.delayed_effects),
        ("Immediate Effects:", msds.immediate_effects),
        ("Chronic Effects:", msds.chronic_effects),
        ("Numerical Measures of Toxicity:", process_statements(msds.acute_toxicity_estimates))
    ]

    # Add only non-empty values to section11_data
    for label, value in section11_values:
        if value:  # Skip blank or None values
            section11_data.append([
                Paragraph(label, styles["FieldLabel"]),
                Paragraph(value, styles["FieldValue"])
            ])

    # Define column widths
    col_widths_sec11 = [usable_width * 0.45, usable_width * 0.55]

    # Create the table
    section11_table = Table(section11_data, colWidths=col_widths_sec11)

    section11_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Outer border
        ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Highlight first column
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align content
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align vertically
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
    ]))

    # Group header and table with KeepTogether
    section11 = KeepTogether([section11_header, section11_spacer, section11_table])
    story.append(section11)
    story.append(Spacer(1, 0.2 * inch))

    # Section 12: Ecological Information
    section12_header = Paragraph("Section 12: Ecological Information", styles["SectionHeading"])
    section12_spacer = Spacer(1, 0.1 * inch)

    section12_data = []

    # Add header row
    section12_data.append([
        Paragraph("Property", styles["FieldLabel"]),
        Paragraph("Value", styles["FieldLabel"])
    ])

    # Define section12_values with new fields
    section12_values = [
        ("Ecotoxicity:", msds.ecotoxicity),
        ("Persistence and Degradability:", msds.persistence_and_degradability),
        ("Bioaccumulative Potential:", msds.bioaccumulative_potential),
        ("Mobility in Soil:", msds.mobility_in_soil),
        ("Other Adverse Effects:", msds.other_adverse_effects)
    ]

    # Add only non-empty values to section12_data
    for label, value in section12_values:
        if value:  # Skip blank or None values
            section12_data.append([
                Paragraph(label, styles["FieldLabel"]),
                Paragraph(value, styles["FieldValue"])
            ])

    if len(section12_data) > 1:

        # Define column widths
        col_widths_sec12 = [usable_width * 0.45, usable_width * 0.55]

        # Create the table
        section12_table = Table(section12_data, colWidths=col_widths_sec12)

        section12_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Outer border
            ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # Highlight header row
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Highlight first column
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align content
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align vertically
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))

        # Group header and table with KeepTogether
        section12 = KeepTogether([section12_header, section12_spacer, section12_table])
        story.append(section12)
        story.append(Spacer(1, 0.2 * inch))

    # Section 13: Disposal Considerations
    section13_header = Paragraph("Section 13: Disposal Considerations", styles["SectionHeading"])
    section13_spacer = Spacer(1, 0.1 * inch)

    if msds.disposal_methods != '':
        disposal_methods_text = Paragraph(
        f"""<para align="justify"><font size=10> {msds.disposal_methods}</font></para>""",
        styles["Normal"]
        )   

        # Group header and table with KeepTogether
        section13 = KeepTogether([section13_header, section13_spacer, disposal_methods_text])
        story.append(section13)
        story.append(Spacer(1, 0.2 * inch))

    # Section 14: Transport Information
    section14_header = Paragraph("Section 14: Transport Information", styles["SectionHeading"])
    section14_spacer = Spacer(1, 0.1 * inch)

    section14_data = []

    # Define section14_values with the new fields
    section14_values = [
        ("UN Number:", msds.UN_number),
        ("UN Proper Shipping Name:", msds.UN_proper_shipping_name),
        ("Transport Hazard Class:", msds.transport_hazard_class),
        ("Packing Group:", msds.packing_group),
        ("Environmental Hazards:", msds.environmental_hazards),
        ("Special Precautions:", msds.special_precautions),
        ("Transport in Bulk:", msds.transport_in_bulk)
    ]

    # Add only non-empty values to section14_data
    for label, value in section14_values:
        if value:  # Skip blank or None values
            section14_data.append([
                Paragraph(label, styles["FieldLabel"]),
                Paragraph(value, styles["FieldValue"])
            ])

    # Define column widths
    col_widths_sec14 = [usable_width * 0.45, usable_width * 0.55]

    if len(section14_data) > 1:

        # Create the table
        section14_table = Table(section14_data, colWidths=col_widths_sec14)

        section14_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),       # Outer border
            ('INNERGRID', (0, 0), (-1, -1), 0.33, colors.grey), # Grid lines
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),  # Highlight first column
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),              # Center-align content
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),             # Center-align vertically
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
        ]))

        # Group header and table with KeepTogether

        section14 = KeepTogether([section14_header, section14_spacer, section14_table])
        story.append(section14)
        story.append(Spacer(1, 0.1 * inch))

    input_string_un_picto = msds.UN_picto or ''

    if input_string_un_picto != '':
        un_url_list = input_string_un_picto.split(',')

        # Adjust paths to be relative to the static directory
        un_paths = [url.split("/static/")[-1].lstrip('/') for url in un_url_list]
        logger.debug(f"Adjusted un_paths: {un_paths}")

        un_images = []

        for path in un_paths:
            un_img_path = finders.find(path)
            logger.debug(f"un_img_path: {un_img_path}")

            if not un_img_path:
                logger.warning(f"Image not found for path: {path}")
            else:
                un_rot_imag = RotatedImage(un_img_path, angle=315, scale=0.025)
                un_images.append(un_rot_imag)         

        un_max_per_row = 3
        sec14_img_rows = [un_images[i:i + un_max_per_row] for i in range(0, len(un_images), un_max_per_row)]

        all_tables = []  # Collect all tables

        # Iterate over each row and create a table for it
        for un_row_images in sec14_img_rows:
            un_row_len = len(un_row_images)
            
            # Create a Table for the current row with the exact number of columns
            un_label_table = Table(
                data=[un_row_images],  # Single row table
                colWidths=[1.5 * inch] * un_row_len  # Adjust column widths to match the number of images
            )

            # Apply styling to the table
            un_label_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 16),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 16)
            ]))

            # Wrap the table in KeepTogether and add it to the list
            all_tables.append(KeepTogether([un_label_table]))

        # Combine all tables into a single KeepTogether section
        sec14_un_picto = KeepTogether([
            Paragraph("UN Model Regulation Pictograms", styles["SubHeading"]),
            Spacer(1, 0.1 * inch),
            *all_tables  # Spread the list of tables
        ])

        # Append to the story
        story.append(sec14_un_picto)

    story.append(Spacer(1, 0.2 * inch))

    if msds.safety_health_environmental_regulations.strip() != '':
        section15_header = Paragraph("Section 15: Regulatory Information", styles["SectionHeading"])
        section15_spacer = Spacer(1, 0.1 * inch)

        # Wrap the string in a Paragraph
        sec15_text = Paragraph(
            f"""<para align="justify"><font size=10>{msds.safety_health_environmental_regulations}</font></para>""",
            styles["Normal"]
        )

        sec15 = KeepTogether([section15_header, section15_spacer, sec15_text, Spacer(1, 0.2 * inch)])
        story.append(sec15)


    section16_header = Paragraph("Section 16: Other Information", styles["SectionHeading"])
    section16_spacer = Spacer(1, 0.1 * inch)

    # Other Information Paragraph
    other_info = Paragraph(
        f"""<para align="justify"><font size=10>
        <b>Other information:</b> {msds.other_information}
        </font></para>""",
        styles["Normal"]
    )

    # Disclaimer Paragraph
    if msds.disclaimer.strip() != '':
        disclaimer = Paragraph(
            f"""<para align="justify"><font size=10>
            <b>Disclaimer:</b> {msds.disclaimer}
            </font></para>""",
            styles["Normal"]
        )

    # Version Paragraph
    if msds.version.strip() != '':
        version = Paragraph(
            f"""<para align="justify"><font size=10>
            <b>Version:</b> {msds.version}
            </font></para>""",
            styles["Normal"]
        )

    # Date of Preparation Paragraph
    if msds.date_of_preparation is not None:
        date_of_preparation = Paragraph(
            f"""<para align="justify"><font size=10>
            <b>Date of Preparation:</b> {msds.date_of_preparation.strftime('%Y-%m-%d')}</font></para>""",
            styles["Normal"]
        )

    # Last Revision Date Paragraph
    if msds.last_revision_date is not None:
        last_revision_date = Paragraph(
        f"""<para align="justify"><font size=10><b>Last Revision Date:</b> {msds.last_revision_date.strftime('%Y-%m-%d')}</font></para>""",
        styles["Normal"]
        )


    # Adding all components to the story
    sec16 = [section16_header, section16_spacer, other_info]

    if msds.disclaimer.strip() != '':
        sec16.append(disclaimer)

    if msds.version.strip() != '':
        sec16.append(version)

    if msds.date_of_preparation is not None:
        sec16.append(date_of_preparation)

    if msds.last_revision_date is not None:
        sec16.append(last_revision_date)

    whole_sec16 = KeepTogether(sec16)
    story.append(whole_sec16)

    doc.build(story)

    # Get the PDF value
    pdf = buffer.getvalue()
    buffer.close()

    # Return a response to the browser
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="SDS_Test.pdf"'
    response.write(pdf)
    return response