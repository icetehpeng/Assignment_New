"""
PDF Report Generator for health reports and doctor visits
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self, db_conn=None, db_available=False):
        """Initialize report generator"""
        self.db_conn = db_conn
        self.db_available = db_available
    
    def generate_health_report(self, username: str, days: int = 30) -> Optional[BytesIO]:
        """Generate comprehensive health report for doctor visit"""
        try:
            # Try to import reportlab for PDF generation
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            logger.error("reportlab not installed. Install with: pip install reportlab")
            return None
        
        if not self.db_available or not self.db_conn:
            logger.error("Database not available for report generation")
            return None
        
        try:
            # Create PDF buffer
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0078FF'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            story.append(Paragraph("📋 Health Report", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Report metadata
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()
            
            if not user:
                logger.error(f"User {username} not found")
                return None
            
            meta_data = [
                ["Patient Name:", username],
                ["Report Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Report Period:", f"Last {days} days"],
            ]
            meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E0E6ED')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Vital Signs Summary
            story.append(Paragraph("❤️ Vital Signs Summary", styles['Heading2']))
            cursor.execute(f"""
                SELECT vital_type, AVG(value) as avg_value, MIN(value) as min_value, MAX(value) as max_value
                FROM vital_signs
                WHERE username=%s AND timestamp > DATE_SUB(NOW(), INTERVAL {days} DAY)
                GROUP BY vital_type
            """, (username,))
            
            vitals_data = [["Vital Type", "Average", "Min", "Max"]]
            for row in cursor.fetchall():
                vitals_data.append([
                    row[0],
                    f"{row[1]:.1f}",
                    f"{row[2]:.1f}",
                    f"{row[3]:.1f}"
                ])
            
            if len(vitals_data) > 1:
                vitals_table = Table(vitals_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                vitals_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0078FF')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(vitals_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Medication Compliance
            story.append(Paragraph("💊 Medication Compliance", styles['Heading2']))
            cursor.execute(f"""
                SELECT medication_name, COUNT(*) as times_taken
                FROM medication_logs
                WHERE username=%s AND timestamp > DATE_SUB(NOW(), INTERVAL {days} DAY)
                GROUP BY medication_name
            """, (username,))
            
            med_data = [["Medication", "Times Taken"]]
            for row in cursor.fetchall():
                med_data.append([row[0], str(row[1])])
            
            if len(med_data) > 1:
                med_table = Table(med_data, colWidths=[3*inch, 2*inch])
                med_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF5E00')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(med_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Activity Summary
            story.append(Paragraph("🚶 Activity Summary", styles['Heading2']))
            cursor.execute(f"""
                SELECT activity_type, COUNT(*) as count, SUM(duration_minutes) as total_minutes
                FROM activities
                WHERE username=%s AND timestamp > DATE_SUB(NOW(), INTERVAL {days} DAY)
                GROUP BY activity_type
            """, (username,))
            
            activity_data = [["Activity Type", "Count", "Total Minutes"]]
            for row in cursor.fetchall():
                activity_data.append([row[0], str(row[1]), str(row[2])])
            
            if len(activity_data) > 1:
                activity_table = Table(activity_data, colWidths=[2*inch, 1.5*inch, 2*inch])
                activity_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00D1FF')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(activity_table)
            
            # Build PDF
            doc.build(story)
            pdf_buffer.seek(0)
            logger.info(f"Health report generated for {username}")
            return pdf_buffer
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return None
    
    def generate_medication_report(self, username: str) -> Optional[BytesIO]:
        """Generate medication compliance report"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER
        except ImportError:
            return None
        
        if not self.db_available or not self.db_conn:
            return None
        
        try:
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            story.append(Paragraph("💊 Medication Report", styles['Heading1']))
            story.append(Spacer(1, 0.3*inch))
            
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT medication_name, dosage, frequency, start_date, end_date, notes
                FROM medications
                WHERE username=%s AND end_date IS NULL
            """, (username,))
            
            med_data = [["Medication", "Dosage", "Frequency", "Start Date"]]
            for row in cursor.fetchall():
                med_data.append([row[0], row[1], row[2], str(row[3])])
            
            if len(med_data) > 1:
                med_table = Table(med_data)
                med_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF5E00')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(med_table)
            
            doc.build(story)
            pdf_buffer.seek(0)
            return pdf_buffer
        
        except Exception as e:
            logger.error(f"Error generating medication report: {e}")
            return None
