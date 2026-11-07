from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_pdf_report(gender, gender_code, age, answers, question_texts, categories, 
                        total_score, percentage, stress_type, 
                        category_scores, top_stress_areas, svm_confidence=None):
    """Generate PDF report using reportlab"""
    
    buffer = BytesIO()
    # Use 30pt margins to give us max horizontal space
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=30, leftMargin=30, 
                           topMargin=72, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    story = []
    
    # --- Title & Date ---
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.blue, alignment=TA_CENTER, spaceAfter=30)
    story.append(Paragraph("Stress Test Report", title_style))
    story.append(Spacer(1, 12))
    
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
    story.append(Spacer(1, 20))
    
    # --- User Information ---
    story.append(Paragraph("Personal Information", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    user_data = [
        ["Gender:", gender, "Gender Code:", str(gender_code)],
        ["Age:", str(age), "Questions Answered:", str(len(answers))]
    ]
    
    user_table = Table(user_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    user_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOLD', (0, 0), (0, -1), True),
        ('BOLD', (2, 0), (2, -1), True),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(user_table)
    story.append(Spacer(1, 20))
    
    # --- Stress Type Classification ---
    story.append(Paragraph("Stress Type Classification", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    stress_type_colors = {"Eustress": colors.blue, "Distress": colors.red, "No Stress": colors.green}
    stress_type_style = ParagraphStyle(
        'StressType', parent=styles['Normal'], fontSize=16, 
        textColor=stress_type_colors.get(stress_type, colors.black), 
        alignment=TA_CENTER, spaceAfter=10
    )
    
    story.append(Paragraph(f"<b>{stress_type}</b>", stress_type_style))
    if svm_confidence is not None:
        story.append(Paragraph(f"<i>Model confidence: {svm_confidence*100:.1f}% (SVM classifier)</i>", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # --- Category Breakdown ---
    story.append(Paragraph("Category Breakdown", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    if category_scores:
        cat_data = [["Category", "Average Score (1-5)"]]
        for cat, score in category_scores.items():
            clean_cat = cat.split()[1] if len(cat.split()) > 1 else cat
            cat_data.append([clean_cat, f"{score:.1f}"])
        
        cat_table = Table(cat_data, colWidths=[4*inch, 2*inch])
        cat_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOLD', (0, 0), (-1, 0), True),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 20))
    
    # --- Top 5 Stress Areas ---
    if top_stress_areas:
        story.append(Paragraph("Top 5 Stress Areas", styles['Heading2']))
        story.append(Spacer(1, 10))
        for i, item in enumerate(top_stress_areas[:5], 1):
            story.append(Paragraph(f"{i}. {item['question']}", styles['Normal']))
            story.append(Paragraph(f"   {item['category']} • Score: {item['score']}/5 - {item['level']} Level", styles['Normal']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 10))
    
    # --- Personalized Recommendations ---
    story.append(Paragraph("Personalized Recommendations", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    if stress_type == "Eustress":
        recs = [
            "<b>Self care:</b> Prioritize self-care activities to maintain well-being and prevent eustress from turning into distress",
            "<b>Channel your energy:</b> Use this motivating stress to tackle challenging projects and goals",
            "<b>Maintain balance:</b> Continue your healthy routines that are working well",
            "<b>Set new challenges:</b> Consider taking on new learning opportunities or responsibilities",
            "<b>Practice mindfulness:</b> Stay present and enjoy your accomplishments",
            "<b>Share your strategies:</b> Help others who may be struggling with stress"
        ]
    elif stress_type == "Distress":
        recs = [
            "<b>Seek support:</b> Talk to a counselor, therapist, or trusted friend",
            "<b>Practice relaxation:</b> Try deep breathing, meditation, or yoga daily",
            "<b>Prioritize self-care:</b> Ensure adequate sleep, nutrition, and exercise",
            "<b>Set boundaries:</b> Learn to say no and protect your time",
            "<b>Break tasks down:</b> Divide overwhelming tasks into smaller, manageable steps",
            "<b>Consider professional help:</b> If distress persists, seek professional mental health support",
            "<b>Self Assessment:</b> Regularly assess your stress levels and triggers"
        ]
    else:
        recs = [
            "<b>Stay engaged:</b> Consider new challenges to maintain growth and development",
            "<b>Build resilience:</b> Continue developing coping skills for future challenges",
            "<b>Maintain connections:</b> Keep nurturing your relationships and social network",
            "<b>Practice gratitude:</b> Appreciate your current balanced state",
            "<b>Plan ahead:</b> Set goals that will keep you motivated and fulfilled"
        ]
        
    for rec in recs:
        story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 6))
    story.append(Spacer(1, 20))
    
    # --- Detailed Responses ---
    story.append(PageBreak())
    story.append(Paragraph("Detailed Responses", styles['Heading1']))
    story.append(Spacer(1, 10))
    
    # Create a specific style for the table cells
    cell_style = ParagraphStyle(
        'TableCell', 
        parent=styles['Normal'], 
        fontSize=8,       
        leading=12,       
        alignment=TA_LEFT
    )
    
    answer_data = [
        [
            Paragraph("<b>Q#</b>", cell_style), 
            Paragraph("<b>Category</b>", cell_style), 
            Paragraph("<b>Question</b>", cell_style), 
            Paragraph("<b>Score</b>", cell_style), 
            Paragraph("<b>Response</b>", cell_style)
        ]
    ]
    
    for q_id, answer in sorted(answers.items()):
        if q_id >= 3:
            category_name = "Other"
            for cat_name, cat_data in categories.items():
                if q_id in cat_data["ids"]:
                    category_name = cat_name.split()[1] if len(cat_name.split()) > 1 else cat_name
                    break
            
            # 1. FULL text, no truncation
            question_text = str(question_texts.get(q_id, f"Q{q_id}")).replace("\n", " ").replace("\t", " ").strip()
            answer_text = str(answer).replace("\n", " ").replace("\t", " ").strip()
            
            try:
                score = int(answer.split(" - ")[0])
            except:
                score = "-"
            
            # 2. Wrap in Paragraph
            answer_data.append([
                Paragraph(str(q_id), cell_style),
                Paragraph(category_name, cell_style),
                Paragraph(question_text, cell_style), 
                Paragraph(str(score), cell_style),
                Paragraph(answer_text, cell_style)
            ])
    
    # 3. NO rowHeights. Dynamic wrapping with wider Question column (3.8 inches)
    answer_table = Table(answer_data, colWidths=[0.4*inch, 0.9*inch, 3.8*inch, 0.5*inch, 1.85*inch])
    
    answer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOLD', (0, 0), (-1, 0), True),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),     
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),       
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),       
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),     
        ('ALIGN', (4, 0), (4, -1), 'LEFT'),       
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),     
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(answer_table)
    
    # --- Footer ---
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Spacer(1, 30))
    story.append(Paragraph("This report is for informational purposes only.", footer_style))
    story.append(Paragraph("If you're experiencing severe stress, please consult a mental health professional.", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer