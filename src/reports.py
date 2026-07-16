from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from datetime import datetime

def generate_health_report_pdf(patient_id: str, bmi_val: float, bmi_cat: str, risk_strata: str, clinical_insights: str) -> bytes:
    """
    Generates a structured, professional clinical summary PDF in-memory.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Styling
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = styles['BodyText']
    
    # Title & Metadata
    story.append(Paragraph("CareAI Clinical Intelligence Summary Report", title_style))
    story.append(Paragraph(f"<b>Generated On:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Paragraph(f"<b>Patient Identifier:</b> {patient_id}", body_style))
    story.append(Spacer(1, 15))
    
    # Vitals & Metrics Table
    story.append(Paragraph("1. Extracted Anthropometric & Risk Metrics", section_heading))
    data = [
        ['Metric Diagnostic Parameter', 'Recorded Value / Status'],
        ['Calculated Body Mass Index (BMI)', f"{bmi_val} ({bmi_cat})"],
        ['Cardiovascular Risk Stratum', risk_strata]
    ]
    
    t = Table(data, colWidths=[250, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # AI Clinical Insights
    story.append(Paragraph("2. CareAI Deep Clinical Analysis Insights", section_heading))
    story.append(Paragraph(clinical_insights.replace('\n', '<br/>'), body_style))
    story.append(Spacer(1, 20))
    
    # Legal Disclaimer
    disclaimer_style = ParagraphStyle('Disclaimer', parent=body_style, fontSize=8, textColor=colors.gray)
    story.append(Paragraph("<b>MANDATORY MEDICAL DISCLAIMER:</b> This document contains automated analysis powered by AI algorithms. It is strictly for educational and baseline monitoring integration purposes. It does NOT constitute medical advice. Please consult a qualified health professional immediately for clinical diagnostic validation.", disclaimer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()