from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import re

def generate_pdf_report(gender, gender_code, age, answers, question_texts, categories, 
                        total_score, percentage, stress_type, 
                        category_scores, top_stress_areas, svm_confidence=None, generated_time="Unknown"):
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=72, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []
    
    # --- Title & Date ---
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.blue, alignment=TA_CENTER, spaceAfter=30)
    story.append(Paragraph("Stress Test Report", title_style))
    story.append(Spacer(1, 12))
    
    date_style = ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=10, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Paragraph(f"Generated: {generated_time}", date_style))
    story.append(Spacer(1, 20))
    
    # --- User Information ---
    story.append(Paragraph("Personal Information", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    user_data = [
        ["Gender:", gender, "Gender Code:", str(gender_code)],
        ["Age:", str(age), "Questions Answered:", str(len(answers))]
    ]
    
    # CHANGED: Increased colWidths from 1.2*inch to 1.8*inch
    user_table = Table(user_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch, 1.8*inch])
    user_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOLD', (0, 0), (0, -1), True),
        ('BOLD', (2, 0), (2, -1), True),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # CHANGED: Added padding to make the rows taller and look better
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
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

    # --- Specific Recommendations for Top Stress Areas ---
    if top_stress_areas:
        specific_tips_html = ""
        shown_tips = set()
        for item in top_stress_areas[:3]:
            q_lower = item["question"].lower()
            if "sleep" in q_lower and "sleep" not in shown_tips: 
                specific_tips_html += "<li><b>Sleep Tips:</b> Maintain a consistent sleep schedule.</li>"
                shown_tips.add("sleep")
            elif ("anxiety" in q_lower or "tension" in q_lower) and "anxiety" not in shown_tips: 
                specific_tips_html += "<li><b>Anxiety Management:</b> Practice deep breathing exercises.</li>"
                shown_tips.add("anxiety")
            elif ("competition" in q_lower or "peers" in q_lower) and "competition" not in shown_tips: 
                specific_tips_html += "<li><b>Peer Competition:</b> Focus on your personal growth.</li>"
                shown_tips.add("competition")
            elif ("academic" in q_lower or "workload" in q_lower or "classes" in q_lower) and "academic" not in shown_tips: 
                specific_tips_html += "<li><b>Academic Stress:</b> Break tasks into smaller chunks.</li>"
                shown_tips.add("academic")
            elif "relationship" in q_lower and "relationship" not in shown_tips: 
                specific_tips_html += "<li><b>Relationships:</b> Communicate openly.</li>"
                shown_tips.add("relationship")
            elif ("confidence" in q_lower or "performance" in q_lower) and "confidence" not in shown_tips: 
                specific_tips_html += "<li><b>Building Confidence:</b> Celebrate small wins.</li>"
                shown_tips.add("confidence")
            elif ("health" in q_lower or "illness" in q_lower) and "health" not in shown_tips: 
                specific_tips_html += "<li><b>Health Concerns:</b> Schedule a check-up.</li>"
                shown_tips.add("health")
            elif ("lonely" in q_lower or "isolated" in q_lower) and "lonely" not in shown_tips: 
                specific_tips_html += "<li><b>Social Connection:</b> Join a club or group activity.</li>"
                shown_tips.add("lonely")
            elif ("environment" in q_lower or "hostel" in q_lower or "working" in q_lower) and "environment" not in shown_tips: 
                specific_tips_html += "<li><b>Environment:</b> Create a comfortable workspace.</li>"
                shown_tips.add("environment")
            elif ("heartbeat" in q_lower or "palpitations" in q_lower) and "heartbeat" not in shown_tips: 
                specific_tips_html += "<li><b>Physical Symptoms:</b> Practice deep breathing.</li>"
                shown_tips.add("heartbeat")
            elif "irritated" in q_lower and "irritated" not in shown_tips: 
                specific_tips_html += "<li><b>Irritability:</b> Practice mindfulness.</li>"
                shown_tips.add("irritated")
            elif ("extracurricular" in q_lower or "activities" in q_lower) and "activities" not in shown_tips: 
                specific_tips_html += "<li><b>Work-Life Balance:</b> Prioritize activities.</li>"
                shown_tips.add("activities")
            elif "weight" in q_lower and "weight" not in shown_tips: 
                specific_tips_html += "<li><b>Weight Management:</b> Consult a nutritionist.</li>"
                shown_tips.add("weight")
            
        if specific_tips_html:
            story.append(Paragraph("Specific Recommendations for Your Top Stress Areas", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            tips = re.findall(r'<li>(.*?)</li>', specific_tips_html)
            
            for tip in tips:
                story.append(Paragraph(f"• {tip}", styles['Normal']))
                story.append(Spacer(1, 6))
                
            story.append(Spacer(1, 20))
    
    # --- Detailed Responses ---
    story.append(PageBreak())
    story.append(Paragraph("Detailed Responses", styles['Heading1']))
    story.append(Spacer(1, 10))
    
    cell_style = ParagraphStyle('TableCell', parent=styles['Normal'], fontSize=8, leading=12, alignment=TA_LEFT)
    
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
        try:
            q_id_int = int(q_id)
        except ValueError:
            continue 

        if q_id_int >= 3:
            category_name = "Other"
            for cat_name, cat_data in categories.items():
                if q_id_int in cat_data["ids"]:
                    category_name = cat_name.split()[1] if len(cat_name.split()) > 1 else cat_name
                    break
            
            question_text = str(question_texts.get(q_id_int, f"Q{q_id_int}")).replace("\n", " ").replace("\t", " ").strip()
            answer_text = str(answer).replace("\n", " ").replace("\t", " ").strip()
            
            try:
                score = int(answer.split(" - ")[0])
            except:
                score = "-"
            
            answer_data.append([
                Paragraph(str(q_id_int), cell_style),
                Paragraph(category_name, cell_style),
                Paragraph(question_text, cell_style), 
                Paragraph(str(score), cell_style),
                Paragraph(answer_text, cell_style)
            ])
    
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
    
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    story.append(Spacer(1, 30))
    story.append(Paragraph("This report is for informational purposes only.", footer_style))
    story.append(Paragraph("If you're experiencing severe stress, please consult a mental health professional.", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer