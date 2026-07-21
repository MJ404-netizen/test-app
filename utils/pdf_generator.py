from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

def generate_pdf_report(gender, gender_code, age, answers, question_texts, categories, 
                        total_score, percentage, stress_level, stress_type, 
                        category_scores, top_stress_areas):
    """Generate PDF report using reportlab"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.navy,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    story.append(Paragraph("Stress Test Report", title_style))
    story.append(Spacer(1, 12))
    
    # Date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
    story.append(Spacer(1, 20))
    
    # User Information
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
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(user_table)
    story.append(Spacer(1, 20))
    
    # Stress Type
    story.append(Paragraph("Stress Type Classification", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    stress_type_colors = {
        "Eustress": colors.blue,
        "Distress": colors.red,
        "No Stress": colors.green
    }
    
    stress_type_style = ParagraphStyle(
        'StressType',
        parent=styles['Normal'],
        fontSize=16,
        textColor=stress_type_colors.get(stress_type, colors.black),
        alignment=TA_CENTER,
        spaceAfter=10
    )
    story.append(Paragraph(f"<b>{stress_type}</b>", stress_type_style))
    story.append(Spacer(1, 10))
    
    # Stress Level
    story.append(Paragraph(f"Stress Level: {stress_level} ({percentage:.1f}%)", styles['Normal']))
    story.append(Paragraph(f"Total Score: {total_score}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Category Breakdown
    story.append(Paragraph("Category Breakdown", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    if category_scores:
        cat_data = [["Category", "Average Score (1-5)"]]
        for cat, score in category_scores.items():
            clean_cat = cat.split()[1] if len(cat.split()) > 1 else cat
            cat_data.append([clean_cat, f"{score:.1f}"])
        
        cat_table = Table(cat_data, colWidths=[3*inch, 2*inch])
        cat_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOLD', (0, 0), (-1, 0), True),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgray),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 20))
    
    # Top Stress Areas
    if top_stress_areas:
        story.append(Paragraph("Top Stress Areas", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        for i, item in enumerate(top_stress_areas[:3], 1):
            story.append(Paragraph(f"{i}. {item['question']}", styles['Normal']))
            story.append(Paragraph(f"   Score: {item['score']}/5 - {item['level']} Level", styles['Normal']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 10))
    
    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    if stress_type == "Eustress":
        recommendations = [
            "Channel your energy into challenging projects and goals",
            "Maintain your healthy routines that are working well",
            "Consider taking on new learning opportunities",
            "Practice mindfulness and enjoy your accomplishments"
        ]
    elif stress_type == "Distress":
        recommendations = [
            "Seek support from a counselor, therapist, or trusted friend",
            "Practice relaxation techniques daily (deep breathing, meditation, yoga)",
            "Prioritize self-care: adequate sleep, nutrition, and exercise",
            "Set boundaries and learn to say no",
            "Break overwhelming tasks into smaller, manageable steps"
        ]
    else:
        recommendations = [
            "Stay engaged with new challenges to maintain growth",
            "Continue developing coping skills for future challenges",
            "Keep nurturing your relationships and social network",
            "Practice gratitude and appreciate your balanced state"
        ]
    
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 6))
    story.append(Spacer(1, 20))
    
    # Detailed Answers
    story.append(PageBreak())
    story.append(Paragraph("Detailed Responses", styles['Heading1']))
    story.append(Spacer(1, 10))
    
    answer_data = [["Q#", "Category", "Question", "Score", "Response"]]
    for q_id, answer in sorted(answers.items()):
        if q_id >= 3:
            category_name = "Other"
            for cat_name, cat_data in categories.items():
                if q_id in cat_data["ids"]:
                    category_name = cat_name.split()[1] if len(cat_name.split()) > 1 else cat_name
                    break
            
            question_text = question_texts.get(q_id, f"Q{q_id}")
            if len(question_text) > 50:
                question_text = question_text[:47] + "..."
            
            try:
                score = int(answer.split(" - ")[0])
            except:
                score = "-"
            
            answer_data.append([str(q_id), category_name, question_text, str(score), answer])
    
    answer_table = Table(answer_data, colWidths=[0.4*inch, 0.8*inch, 2.2*inch, 0.5*inch, 1.5*inch])
    answer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOLD', (0, 0), (-1, 0), True),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgray),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(answer_table)
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=TA_CENTER
    )
    story.append(Spacer(1, 30))
    story.append(Paragraph("This report is for informational purposes only.", footer_style))
    story.append(Paragraph("If you're experiencing severe stress, please consult a mental health professional.", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer