# utils/report_generator.py
"""
Report Generator
Create PDF reports for skill gap analysis.
Uses ReportLab library.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from models.employee import Employee
from models.gap_analysis import GapAnalysis
from models.skill import Skill


def generate_employee_report(employee_id):
    """
    Generate a PDF report for a single employee.
    
    Parameters:
    employee_id (int): Employee ID.
    
    Returns:
    BytesIO: In-memory PDF file ready for download.
    """
    employee = Employee.query.get(employee_id)
    if not employee:
        return None
    
    # Create a buffer for the PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, spaceAfter=12)
    story.append(Paragraph(f"Skill Gap Report for {employee.full_name()}", title_style))
    story.append(Spacer(1, 12))
    
    # Employee details
    details = [
        ["Employee Code", employee.employee_code],
        ["Email", employee.email],
        ["Department", employee.department.name if employee.department else "N/A"],
        ["Job Role", employee.job_role.title if employee.job_role else "N/A"],
        ["Readiness Score", f"{employee.get_readiness_score()}%"],
    ]
    table = Table(details, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (0,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    
    # Skill Gap Details
    story.append(Paragraph("Skill Gap Analysis", styles['Heading2']))
    gaps = GapAnalysis.query.filter_by(employee_id=employee.id).all()
    if gaps:
        gap_data = [["Skill", "Required", "Current", "Gap Score"]]
        for g in gaps:
            skill = Skill.query.get(g.skill_id)
            gap_score_text = {0: "No Gap", 1: "Minor", 2: "Major"}.get(g.gap_score, "Unknown")
            gap_data.append([
                skill.name if skill else "Unknown",
                g.required_proficiency,
                g.current_proficiency,
                gap_score_text
            ])
        gap_table = Table(gap_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        gap_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        story.append(gap_table)
    else:
        story.append(Paragraph("No gap analysis found for this employee.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_department_summary_report(department_id):
    """
    Generate a summary PDF for a department (all employees).
    Not fully implemented – placeholder for expansion.
    """
    # Similar structure but loops over employees
    pass