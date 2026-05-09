import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor

def generate_cti_pdf(data: dict) -> io.BytesIO:
    """
    Generates a structured PDF report based on CTI findings.
    Expected data dict format:
    {
        "query": str,
        "query_response": str,
        "classification": str,
        "classification_confidence": float,
        "vulnerabilities": list of dicts [{"id", "severity", "description"}],
        "risk_score": float,
        "risk_label": str
    }
    """
    buffer = io.BytesIO()
    
    # Setup document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=HexColor('#1f2937')
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10,
        textColor=HexColor('#374151')
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=14
    )
    
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=HexColor('#6b7280'),
        spaceAfter=30
    )
    
    elements = []
    
    # 1. Title & Metadata
    elements.append(Paragraph("CTI Analysis Report", title_style))
    current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    elements.append(Paragraph(f"Generated on: {current_time}", meta_style))
    elements.append(Spacer(1, 10))
    
    # 2. Risk Score
    risk_score = data.get("risk_score", 0.0)
    risk_label = data.get("risk_label", "Unknown")
    color_hex = "#dc2626" if risk_score > 75 else "#ea580c" if risk_score > 50 else "#16a34a"
    
    risk_style = ParagraphStyle(
        'RiskStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=HexColor(color_hex),
        spaceAfter=15
    )
    
    elements.append(Paragraph("Overall Risk Assessment", heading_style))
    elements.append(Paragraph(f"Score: {risk_score}/100 - Level: {risk_label}", risk_style))
    elements.append(Spacer(1, 10))
    
    # 3. Query Summary
    elements.append(Paragraph("Query Summary", heading_style))
    query = data.get("query", "No query provided.")
    elements.append(Paragraph(f"<b>Query:</b> {query}", normal_style))
    
    response = data.get("query_response", "No response provided.")
    # Clean up markdown for PDF rendering
    response = response.replace("\n", "<br/>")
    elements.append(Paragraph(f"<b>Response:</b><br/>{response}", normal_style))
    elements.append(Spacer(1, 10))
    
    # 4. Threat Classification
    elements.append(Paragraph("Threat Classification", heading_style))
    cls = data.get("classification", "N/A")
    conf = data.get("classification_confidence", 0.0)
    elements.append(Paragraph(f"<b>Category:</b> {cls}", normal_style))
    elements.append(Paragraph(f"<b>Confidence:</b> {conf * 100:.1f}%", normal_style))
    elements.append(Spacer(1, 10))
    
    # 5. Vulnerability Analysis
    elements.append(Paragraph("Vulnerability Analysis", heading_style))
    vulns = data.get("vulnerabilities", [])
    if vulns:
        for v in vulns:
            v_id = v.get("id", "Unknown ID")
            v_sev = v.get("severity", "N/A")
            v_desc = v.get("description", "No description.")
            elements.append(Paragraph(f"<b>{v_id}</b> ({v_sev})", normal_style))
            elements.append(Paragraph(f"{v_desc}", normal_style))
            elements.append(Spacer(1, 5))
    else:
        elements.append(Paragraph("No specific vulnerabilities analyzed.", normal_style))
        
    # Build the PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
