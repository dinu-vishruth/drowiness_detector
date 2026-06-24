import os
import csv
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(session, user, alert_events):
    """
    Generates a PDF report for a session and returns a BytesIO buffer.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor('#00f2ea'),
        spaceAfter=15,
        alignment=0
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#a0aec0'),
        spaceAfter=30
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1a202c'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'DocNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=8
    )

    bold_style = ParagraphStyle(
        'DocBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=8
    )
    
    story = []
    
    # Title & Subtitle
    story.append(Paragraph("AI Alertness & Drowsiness Prevention System", title_style))
    story.append(Paragraph(f"Focus Session Report &mdash; Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    story.append(Spacer(1, 10))
    
    # Section 1: User & Session Summary
    story.append(Paragraph("Session Summary", h2_style))
    
    # Details table
    start_str = session.start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_str = session.end_time.strftime('%Y-%m-%d %H:%M:%S')
    
    summary_data = [
        [Paragraph("<b>User:</b>", normal_style), Paragraph(user.username, normal_style),
         Paragraph("<b>Focus Score:</b>", normal_style), Paragraph(f"{session.focus_score:.1f}%", bold_style)],
        [Paragraph("<b>Start Time:</b>", normal_style), Paragraph(start_str, normal_style),
         Paragraph("<b>Avg Alertness:</b>", normal_style), Paragraph(f"{session.avg_alertness:.1f}%", bold_style)],
        [Paragraph("<b>End Time:</b>", normal_style), Paragraph(end_str, normal_style),
         Paragraph("<b>Drowsiness Incidents:</b>", normal_style), Paragraph(str(session.alerts_count), bold_style)],
        [Paragraph("<b>Duration:</b>", normal_style), Paragraph(session.formatted_duration, normal_style),
         Paragraph("<b>Yawns Count:</b>", normal_style), Paragraph(str(session.yawns_count), normal_style)],
        [Paragraph("<b>Blinks Count:</b>", normal_style), Paragraph(str(session.blinks_count), normal_style),
         Paragraph("<b>Head Nods Count:</b>", normal_style), Paragraph(str(session.nods_count), normal_style)]
    ]
    
    summary_table = Table(summary_data, colWidths=[100, 160, 130, 130])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#edf2f7')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Section 2: Alerts & Interventions Logs
    story.append(Paragraph("Alert & Intervention History", h2_style))
    
    if not alert_events:
        story.append(Paragraph("No drowsiness incidents were recorded during this session! Excellent work!", normal_style))
    else:
        # Table of events
        event_headers = ["Time", "Alert Level", "Trigger Reason"]
        event_data = [event_headers]
        
        for idx, event in enumerate(alert_events):
            rel_time = event.timestamp.strftime('%H:%M:%S')
            severity = event.severity_level
            reason = event.trigger_reason
            
            # Format colors based on level
            bg_color = '#fed7d7' if severity.lower() == 'critical' else '#feebc8'
            text_color = '#c53030' if severity.lower() == 'critical' else '#c05621'
            
            severity_p = Paragraph(f"<font color='{text_color}'><b>{severity.upper()}</b></font>", normal_style)
            
            event_data.append([
                Paragraph(rel_time, normal_style),
                severity_p,
                Paragraph(reason, normal_style)
            ])
            
        event_table = Table(event_data, colWidths=[130, 150, 240])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        # Color table rows based on severity
        for idx in range(1, len(event_data)):
            severity_str = alert_events[idx - 1].severity_level.lower()
            row_bg = colors.HexColor('#fffaf0') if severity_str == 'warning' else colors.HexColor('#fff5f5')
            event_table.setStyle(TableStyle([
                ('BACKGROUND', (0, idx), (-1, idx), row_bg)
            ]))
            
        story.append(event_table)
        
    story.append(Spacer(1, 35))
    
    # Section 3: Recommendations Disclaimer
    story.append(Paragraph("<b>Health & Productivity Tips:</b>", bold_style))
    tips = [
        "Take a 5-minute break for every 45-60 minutes of focus to keep average alertness high.",
        "Ensure your workspace is well-illuminated; dim lighting increases natural eye strain and drowsiness.",
        "If you yawning frequently, perform a quick physical stretch or drink a glass of cold water.",
        "Maintain upright head posture. Adjust your monitor height to keep eyes leveled and prevent nodding."
    ]
    for tip in tips:
        story.append(Paragraph(f"&bull; {tip}", normal_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_csv_report(session, user, alert_events):
    """
    Generates a CSV report for a session and returns a string content.
    """
    output = []
    
    # Write metadata
    output.append(["AI Alertness & Drowsiness Prevention System - Session Report"])
    output.append(["Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    output.append([])
    
    # Write summary
    output.append(["Session Summary"])
    output.append(["Username", user.username])
    output.append(["Start Time", session.start_time.strftime('%Y-%m-%d %H:%M:%S')])
    output.append(["End Time", session.end_time.strftime('%Y-%m-%d %H:%M:%S')])
    output.append(["Duration (seconds)", session.duration_seconds])
    output.append(["Duration (formatted)", session.formatted_duration])
    output.append(["Average Alertness (%)", round(session.avg_alertness, 2)])
    output.append(["Focus Score (%)", round(session.focus_score, 2)])
    output.append(["Alerts Count", session.alerts_count])
    output.append(["Yawns Count", session.yawns_count])
    output.append(["Blinks Count", session.blinks_count])
    output.append(["Head Nods Count", session.nods_count])
    output.append([])
    
    # Write Alert Logs
    output.append(["Alert Log"])
    output.append(["Timestamp", "Severity Level", "Trigger Reason"])
    for event in alert_events:
        output.append([
            event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            event.severity_level,
            event.trigger_reason
        ])
        
    # Convert list of rows to string
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(output)
    return si.getvalue()
