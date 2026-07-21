import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import base64
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stress Test Results",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CSS ----------
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .stApp {
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff) !important;
        }
        
        .result-card {
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            padding: 25px 30px;
            margin: 15px 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10);
            border-left: 6px solid #4CAF50;
        }
        
        .result-card-warning {
            border-left: 6px solid #FF9800;
        }
        
        .result-card-danger {
            border-left: 6px solid #F44336;
        }
        
        .result-card-info {
            border-left: 6px solid #2196F3;
        }
        
        .stat-number {
            font-size: 48px;
            font-weight: 700;
            color: #1B5E20;
            text-align: center;
        }
        
        .stat-label {
            font-size: 16px;
            color: #666;
            text-align: center;
            margin-top: 5px;
        }
        
        .stress-level {
            font-size: 24px;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 12px;
            text-align: center;
        }
        
        .stress-low {
            background: #C8E6C9;
            color: #1B5E20;
        }
        
        .stress-moderate {
            background: #FFE0B2;
            color: #E65100;
        }
        
        .stress-high {
            background: #FFCDD2;
            color: #B71C1C;
        }
        
        .stress-eustress {
            background: #BBDEFB;
            color: #0D47A1;
        }
        
        .stress-distress {
            background: #FFCDD2;
            color: #B71C1C;
        }
        
        .stress-no-stress {
            background: #C8E6C9;
            color: #1B5E20;
        }
        
        .recommendation-box {
            background: #E3F2FD;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #1976D2;
        }
        
        .stress-type-box {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10);
            text-align: center;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- CHECK LOGIN ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login to access this page.")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# ---------- CHECK IF TEST IS COMPLETED ----------
if not st.session_state.get("test_completed", False):
    st.warning("⚠️ Please complete the stress test first to view results.")
    if st.button("📝 Take the Test"):
        st.switch_page("pages/stress_test.py")
    st.stop()

# ---------- HEADER ----------
st.title("📊 Stress Test Results")
st.markdown("---")

# ---------- GET USER DATA ----------
gender = st.session_state.get("gender", "Not specified")
gender_code = st.session_state.get("gender_code", "N/A")
age = st.session_state.get("age", "N/A")
answers = st.session_state.get("answers", {})

# ---------- DEFINE QUESTION MAPPING ----------
def get_question_mapping():
    """Get the mapping of question IDs to their text and categories"""
    
    # Question ID to text mapping
    question_texts = {
        1: "What is your gender?",
        2: "What is your age?",
        3: "Have you recently experienced stress in your life?",
        4: "Have you noticed a rapid heartbeat or palpitations?",
        5: "Have you been dealing with anxiety or tension recently? (How Serious is it?)",
        6: "Do you face any sleep problems or difficulties falling asleep?",
        7: "How often have you been dealing with anxiety or tension recently?",
        8: "Have you been getting headaches more than usual?",
        9: "Do you get irritated easily?",
        10: "Do you have trouble concentrating on your academic tasks?",
        11: "Have you been feeling sadness or low mood?",
        12: "Have you been experiencing any illness or health issues?",
        13: "Do you often feel lonely or isolated?",
        14: "Do you feel overwhelmed with your academic workload?",
        15: "Are you in competition with your peers, and does it affect you?",
        16: "Do you find that your relationship often causes you stress?",
        17: "Are you facing any difficulties with your professors or instructors?",
        18: "Is your working environment unpleasant or stressful?",
        19: "Do you struggle to find time for relaxation and leisure activities?",
        20: "Is your hostel or home environment causing you difficulties?",
        21: "Do you lack confidence in your academic performance?",
        22: "Do you lack confidence in your choice of academic subjects?",
        23: "Academic and extracurricular activities conflicting for you?",
        24: "Do you attend classes regularly?",
        25: "Have you gained/lost weight?"
    }
    
    # Category definitions with question IDs
    categories = {
        "🩺 Physical & Health Indicators": {
            "ids": [8, 12, 25],
            "questions": [
                "Have you been getting headaches more than usual?",
                "Have you been experiencing any illness or health issues?",
                "Have you gained/lost weight?"
            ]
        },
        "😰 Emotional & Stress Indicators": {
            "ids": [3, 4, 5, 6, 7, 9, 10, 11, 13],
            "questions": [
                "Have you recently experienced stress in your life?",
                "Have you noticed a rapid heartbeat or palpitations?",
                "Have you been dealing with anxiety or tension recently? (How Serious is it?)",
                "Do you face any sleep problems or difficulties falling asleep?",
                "How often have you been dealing with anxiety or tension recently?",
                "Do you get irritated easily?",
                "Do you have trouble concentrating on your academic tasks?",
                "Have you been feeling sadness or low mood?",
                "Do you often feel lonely or isolated?"
            ]
        },
        "📚 Academic & Environment Stressors": {
            "ids": [14, 15, 17, 18, 20, 21, 22, 23, 24],
            "questions": [
                "Do you feel overwhelmed with your academic workload?",
                "Are you in competition with your peers, and does it affect you?",
                "Are you facing any difficulties with your professors or instructors?",
                "Is your working environment unpleasant or stressful?",
                "Is your hostel or home environment causing you difficulties?",
                "Do you lack confidence in your academic performance?",
                "Do you lack confidence in your choice of academic subjects?",
                "Academic and extracurricular activities conflicting for you?",
                "Do you attend classes regularly?"
            ]
        },
        "💬 Social & Relationship Factors": {
            "ids": [16, 19],
            "questions": [
                "Do you find that your relationship often causes you stress?",
                "Do you struggle to find time for relaxation and leisure activities?"
            ]
        }
    }
    
    return question_texts, categories

# ---------- ANALYZE RESPONSES ----------
def calculate_stress_score(answers):
    """Calculate stress score from answers"""
    stress_answers = {k: v for k, v in answers.items() if k >= 3}
    
    if not stress_answers:
        return 0, 0
    
    scores = []
    for answer in stress_answers.values():
        try:
            score = int(answer.split(" - ")[0])
            scores.append(score)
        except:
            continue
    
    total_score = sum(scores)
    max_possible = len(scores) * 5
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    return total_score, percentage

def get_stress_level(percentage):
    """Get stress level based on percentage"""
    if percentage < 33:
        return "Low Stress", "stress-low", "😊"
    elif percentage < 66:
        return "Moderate Stress", "stress-moderate", "😐"
    else:
        return "High Stress", "stress-high", "😰"

def calculate_stress_type(answers, categories):
    """Calculate stress type (Eustress, Distress, No Stress)"""
    
    # Get scores for each category
    category_scores = {}
    for category_name, category_data in categories.items():
        scores = []
        for q_id in category_data["ids"]:
            if q_id in answers:
                try:
                    score = int(answers[q_id].split(" - ")[0])
                    scores.append(score)
                except:
                    continue
        if scores:
            category_scores[category_name] = sum(scores) / len(scores)
    
    if not category_scores:
        return "No Stress", "stress-no-stress", "😌"
    
    # Calculate overall average
    avg_score = sum(category_scores.values()) / len(category_scores)
    
    # Check for distress patterns (high scores in emotional and physical categories)
    emotional_score = category_scores.get("😰 Emotional & Stress Indicators", 0)
    physical_score = category_scores.get("🩺 Physical & Health Indicators", 0)
    academic_score = category_scores.get("📚 Academic & Environment Stressors", 0)
    social_score = category_scores.get("💬 Social & Relationship Factors", 0)
    
    # Distress: High emotional and physical symptoms
    if emotional_score >= 3.5 and physical_score >= 3.0:
        return "Distress", "stress-distress", "😰"
    
    # Eustress: Moderate emotional with low physical symptoms, high academic engagement
    elif emotional_score >= 2.5 and emotional_score < 3.5 and physical_score < 3.0 and academic_score >= 3.0:
        return "Eustress", "stress-eustress", "💪"
    
    # No Stress: Low scores across all categories
    elif avg_score < 2.0:
        return "No Stress", "stress-no-stress", "😌"
    
    # Default classification
    elif avg_score < 2.5:
        return "No Stress", "stress-no-stress", "😌"
    elif avg_score < 3.5:
        return "Eustress", "stress-eustress", "💪"
    else:
        return "Distress", "stress-distress", "😰"

def calculate_category_scores(answers, categories):
    """Calculate stress scores by category"""
    category_scores = {}
    category_details = {}
    
    for category_name, category_data in categories.items():
        scores = []
        for q_id in category_data["ids"]:
            if q_id in answers:
                try:
                    score = int(answers[q_id].split(" - ")[0])
                    scores.append(score)
                except:
                    continue
        
        if scores:
            avg_score = sum(scores) / len(scores)
            category_scores[category_name] = avg_score
            category_details[category_name] = {
                "average": avg_score,
                "max": max(scores) if scores else 0,
                "min": min(scores) if scores else 0,
                "count": len(scores)
            }
    
    return category_scores, category_details

def get_top_stress_areas(answers, categories, question_texts):
    """Identify top stress areas from all categories"""
    stress_items = []
    
    for category_name, category_data in categories.items():
        for idx, q_id in enumerate(category_data["ids"]):
            if q_id in answers:
                try:
                    score = int(answers[q_id].split(" - ")[0])
                    if score >= 4:  # High stress (4 or 5)
                        stress_items.append({
                            "question": question_texts[q_id],
                            "category": category_name,
                            "score": score,
                            "level": "High" if score == 5 else "Moderate-High"
                        })
                except:
                    continue
    
    stress_items.sort(key=lambda x: x["score"], reverse=True)
    return stress_items[:5]

# ---------- PDF GENERATION FUNCTION ----------
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
        textColor=colors.blue,  # Using 'blue' instead of 'navy'
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
        textColor=colors.grey,
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
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
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
            # Remove emoji for PDF
            clean_cat = cat.split()[1] if len(cat.split()) > 1 else cat
            cat_data.append([clean_cat, f"{score:.1f}"])
        
        cat_table = Table(cat_data, colWidths=[3*inch, 2*inch])
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
            # Find category
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
    
    # Create table with smaller font for answers
    answer_table = Table(answer_data, colWidths=[0.4*inch, 0.8*inch, 2.2*inch, 0.5*inch, 1.5*inch])
    answer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOLD', (0, 0), (-1, 0), True),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(answer_table)
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Spacer(1, 30))
    story.append(Paragraph("This report is for informational purposes only.", footer_style))
    story.append(Paragraph("If you're experiencing severe stress, please consult a mental health professional.", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------- LOAD DATA ----------
question_texts, categories = get_question_mapping()

# ---------- CALCULATE RESULTS ----------
total_score, percentage = calculate_stress_score(answers)
stress_level, stress_class, stress_emoji = get_stress_level(percentage)
stress_type, stress_type_class, stress_type_emoji = calculate_stress_type(answers, categories)
category_scores, category_details = calculate_category_scores(answers, categories)
top_stress_areas = get_top_stress_areas(answers, categories, question_texts)

# ---------- DISPLAY RESULTS ----------
# Row 1: User Info
st.subheader("👤 User Information")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Gender", gender)
with col2:
    st.metric("Gender Code", gender_code)
with col3:
    st.metric("Age", age)
with col4:
    st.metric("Questions Answered", len(answers))

st.markdown("---")

# Row 2: Stress Type Classification
st.subheader("🧠 Your Stress Type Classification")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Display stress type
    st.markdown(f"""
        <div class="stress-type-box">
            <div style="font-size: 72px; margin: 10px 0;">{stress_type_emoji}</div>
            <div class="stress-level {stress_type_class}" style="font-size: 32px;">
                {stress_type}
            </div>
            <div style="margin-top: 15px; font-size: 16px; color: #666;">
                Based on your response patterns across all categories
            </div>
        </div>
    """, unsafe_allow_html=True)

# Stress Type Descriptions
st.markdown("### 📖 Understanding Your Stress Type")

if stress_type == "Eustress":
    st.markdown("""
        <div class="recommendation-box" style="border-left-color: #0D47A1;">
            <h4>💪 Eustress - The "Good" Stress</h4>
            <p><strong>What it means:</strong> You're experiencing positive, motivating stress that helps you perform at your best.</p>
            <ul>
                <li>You feel challenged but capable</li>
                <li>This stress helps you focus and achieve goals</li>
                <li>You're engaged and motivated</li>
                <li>Your physical health indicators are generally good</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
elif stress_type == "Distress":
    st.markdown("""
        <div class="recommendation-box" style="border-left-color: #B71C1C;">
            <h4>😰 Distress - The "Bad" Stress</h4>
            <p><strong>What it means:</strong> You're experiencing overwhelming stress that's negatively affecting your well-being.</p>
            <ul>
                <li>You feel overwhelmed and unable to cope</li>
                <li>Physical symptoms like headaches or sleep issues are present</li>
                <li>Your emotional well-being is significantly impacted</li>
                <li>This stress is interfering with your daily life</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
else:  # No Stress
    st.markdown("""
        <div class="recommendation-box" style="border-left-color: #1B5E20;">
            <h4>😌 No Stress - The Calm State</h4>
            <p><strong>What it means:</strong> You're experiencing very low levels of stress in your life.</p>
            <ul>
                <li>You feel calm and balanced</li>
                <li>You're managing daily challenges well</li>
                <li>Your physical and emotional health are stable</li>
                <li>You have good coping mechanisms</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Row 3: Overall Stress Score
st.subheader("📈 Overall Stress Assessment")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
        <div style="text-align: center;">
            <div class="stress-level {stress_class}">
                {stress_level} ({percentage:.1f}%)
            </div>
            <div style="margin-top: 10px;">
                <span style="font-size: 14px; color: #666;">
                    Total Score: {total_score} / {len([a for a in answers if a >= 3]) * 5}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Row 4: Stress Level Gauge Chart
st.subheader("📊 Stress Level Gauge")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=percentage,
    title={'text': "Stress Level (%)"},
    domain={'x': [0, 1], 'y': [0, 1]},
    gauge={
        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "rgba(33, 150, 243, 0.8)"},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 33], 'color': 'rgba(76, 175, 80, 0.3)'},
            {'range': [33, 66], 'color': 'rgba(255, 193, 7, 0.3)'},
            {'range': [66, 100], 'color': 'rgba(244, 67, 54, 0.3)'}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 90
        }
    }
))

fig.update_layout(
    height=300,
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Row 5: Category Scores
st.subheader("📊 Stress Breakdown by Category")

if category_scores:
    # Create a DataFrame for category scores
    categories_list = list(category_scores.keys())
    scores = list(category_scores.values())
    
    # Create color map
    colors_list = ['#4CAF50' if s < 2.5 else '#FF9800' if s < 3.5 else '#F44336' for s in scores]
    
    fig2 = go.Figure(data=[
        go.Bar(
            x=categories_list,
            y=scores,
            marker_color=colors_list,
            text=[f"{s:.1f}" for s in scores],
            textposition='auto',
            name='Average Score'
        )
    ])
    
    fig2.update_layout(
        title="Average Stress Score by Category (1-5 scale)",
        xaxis_title="Category",
        yaxis_title="Average Score",
        yaxis=dict(range=[0, 5]),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Show category details
    with st.expander("📋 View Category Details"):
        detail_data = []
        for category_name, details in category_details.items():
            detail_data.append({
                "Category": category_name,
                "Average Score": f"{details['average']:.1f}",
                "Highest Score": details['max'],
                "Lowest Score": details['min'],
                "Questions": details['count']
            })
        
        df_details = pd.DataFrame(detail_data)
        st.dataframe(df_details, use_container_width=True, hide_index=True)

st.markdown("---")

# Row 6: Top Stress Areas
st.subheader("🎯 Top Stress Areas")

if top_stress_areas:
    st.write("Here are your top stress areas that may need attention:")
    
    for i, item in enumerate(top_stress_areas, 1):
        color = "#F44336" if item["level"] == "High" else "#FF9800"
        icon = "🔴" if item["level"] == "High" else "🟠"
        
        # Get category icon
        category_icon = ""
        for cat_name in categories.keys():
            if cat_name == item["category"]:
                category_icon = cat_name.split()[0]
                break
        
        st.markdown(f"""
            <div class="result-card result-card-danger" style="border-left-color: {color};">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 24px;">{icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 16px;">{item['question']}</div>
                        <div style="font-size: 14px; color: #666;">
                            {category_icon} {item['category']} • Score: {item['score']}/5 - {item['level']} Level
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("✅ No high-stress areas identified. Keep up the good work!")

st.markdown("---")

# Row 7: Recommendations based on Stress Type
st.subheader("💡 Personalized Recommendations")

if stress_type == "Eustress":
    st.markdown("""
        <div class="recommendation-box" style="border-left-color: #0D47A1;">
            <h4>🌟 Maximizing Your Eustress</h4>
            <ul>
                <li><strong>Channel your energy:</strong> Use this motivating stress to tackle challenging projects and goals</li>
                <li><strong>Maintain balance:</strong> Continue your healthy routines that are working well</li>
                <li><strong>Set new challenges:</strong> Consider taking on new learning opportunities or responsibilities</li>
                <li><strong>Practice mindfulness:</strong> Stay present and enjoy your accomplishments</li>
                <li><strong>Share your strategies:</strong> Help others who may be struggling with stress</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
elif stress_type == "Distress":
    st.markdown("""
        <div class="recommendation-box" style="border-left-color: #B71C1C;">
            <h4>🆘 Managing Distress - Immediate Steps</h4>
            <ul>
                <li><strong>Seek support:</strong> Talk to a counselor, therapist, or trusted friend</li>
                <li><strong>Practice relaxation:</strong> Try deep breathing, meditation, or yoga daily</li>
                <li><strong>Prioritize self-care:</strong> Ensure adequate sleep, nutrition, and exercise</li>
                <li><strong>Set boundaries:</strong> Learn to say no and protect your time</li>
                <li><strong>Break tasks down:</strong> Divide overwhelming tasks into smaller, manageable steps</li>
                <li><strong>Consider professional help:</strong> If distress persists, seek professional mental health support</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
else:  # No Stress
    st.markdown("""
        <div class="recommendation-box" style="border-left-color: #1B5E20;">
            <h4>🌱 Maintaining Your Well-being</h4>
            <ul>
                <li><strong>Stay engaged:</strong> Consider new challenges to maintain growth and development</li>
                <li><strong>Build resilience:</strong> Continue developing coping skills for future challenges</li>
                <li><strong>Maintain connections:</strong> Keep nurturing your relationships and social network</li>
                <li><strong>Practice gratitude:</strong> Appreciate your current balanced state</li>
                <li><strong>Plan ahead:</strong> Set goals that will keep you motivated and fulfilled</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Specific recommendations based on top stress areas
if top_stress_areas:
    st.markdown("### 🎯 Specific Recommendations for Your Top Stress Areas:")
    
    for item in top_stress_areas[:3]:
        question_lower = item["question"].lower()
        
        if "sleep" in question_lower:
            st.info("💤 **Sleep Tips**: Maintain a consistent sleep schedule, avoid screens before bed, create a relaxing bedtime routine")
        elif "anxiety" in question_lower or "tension" in question_lower:
            st.info("🧘 **Anxiety Management**: Practice deep breathing exercises, try mindfulness meditation, talk to someone you trust")
        elif "competition" in question_lower or "peers" in question_lower:
            st.info("🏆 **Peer Competition**: Focus on your personal growth, set realistic goals, celebrate your own achievements, avoid comparing yourself to others")
        elif "academic" in question_lower or "workload" in question_lower or "classes" in question_lower:
            st.info("📚 **Academic Stress**: Break tasks into smaller chunks, use a planner, take regular study breaks, seek help when needed")
        elif "relationship" in question_lower:
            st.info("❤️ **Relationships**: Communicate openly, set healthy boundaries, spend quality time with supportive people")
        elif "confidence" in question_lower or "performance" in question_lower:
            st.info("💪 **Building Confidence**: Celebrate small wins, focus on progress not perfection, seek feedback constructively")
        elif "health" in question_lower or "illness" in question_lower:
            st.info("🏥 **Health Concerns**: Schedule a check-up with a healthcare provider, maintain a healthy diet, stay hydrated")
        elif "lonely" in question_lower or "isolated" in question_lower:
            st.info("🤝 **Social Connection**: Join a club or group activity, reach out to friends, consider volunteering")
        elif "environment" in question_lower or "hostel" in question_lower or "working" in question_lower:
            st.info("🏠 **Environment**: Create a comfortable workspace, talk to management about concerns, consider relocation options")
        elif "heartbeat" in question_lower or "palpitations" in question_lower:
            st.info("❤️ **Physical Symptoms**: Practice deep breathing, reduce caffeine intake, consult a doctor if symptoms persist")
        elif "irritated" in question_lower:
            st.info("😤 **Irritability**: Practice mindfulness, take breaks when feeling overwhelmed, identify triggers")
        elif "extracurricular" in question_lower or "activities" in question_lower:
            st.info("⚖️ **Work-Life Balance**: Prioritize activities, learn to say no, focus on quality over quantity")
        elif "weight" in question_lower:
            st.info("⚖️ **Weight Management**: Consult a nutritionist, maintain a balanced diet, regular exercise, avoid crash diets")
        else:
            st.info(f"💡 **Recommendation**: Consider seeking support from a counselor or trusted advisor")

st.markdown("---")

# Row 8: Detailed Response Summary
st.subheader("📝 Detailed Response Summary")

# Create a DataFrame for all answers with category information
response_data = []
for q_id, answer in sorted(answers.items()):
    if q_id >= 3:  # Only stress questions
        # Find which category this question belongs to
        category_name = "Other"
        for cat_name, cat_data in categories.items():
            if q_id in cat_data["ids"]:
                category_name = cat_name
                break
        
        # Get question text
        question_text = question_texts.get(q_id, f"Q{q_id}")
        
        # Extract score
        try:
            score = int(answer.split(" - ")[0])
        except:
            score = "-"
        
        response_data.append({
            "Question ID": q_id,
            "Category": category_name,
            "Question": question_text[:60] + ("..." if len(question_text) > 60 else ""),
            "Score": score,
            "Response": answer
        })

if response_data:
    df_responses = pd.DataFrame(response_data)
    
    with st.expander("View All Responses"):
        st.dataframe(
            df_responses,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Question ID": st.column_config.NumberColumn("Q#"),
                "Category": st.column_config.TextColumn("Category"),
                "Question": st.column_config.TextColumn("Question"),
                "Score": st.column_config.NumberColumn("Score (1-5)"),
                "Response": st.column_config.TextColumn("Your Answer")
            }
        )

st.markdown("---")

# Row 9: Action Buttons
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🔄 Retake Test", use_container_width=True):
        st.session_state.current_q_index = 0
        st.session_state.answers = {}
        st.session_state.user_responses = {}
        st.session_state.formatted_answers = {}
        st.session_state.test_completed = False
        st.session_state.gender = None
        st.session_state.gender_code = None
        st.session_state.age = None
        st.switch_page("pages/stress_test.py")

with col2:
    # PDF Download Button
    if st.button("📄 Download PDF", use_container_width=True, type="primary"):
        with st.spinner("Generating PDF report..."):
            pdf_buffer = generate_pdf_report(
                gender, gender_code, age, answers, question_texts, categories,
                total_score, percentage, stress_level, stress_type,
                category_scores, top_stress_areas
            )
            
            st.download_button(
                label="📥 Click to Download PDF",
                data=pdf_buffer,
                file_name=f"stress_test_report_{age}_{gender}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="pdf_download"
            )

with col3:
    if st.button("📊 Download Report (TXT)", use_container_width=True):
        report = f"""
STRESS TEST REPORT
===================

Personal Information:
- Gender: {gender} (Code: {gender_code})
- Age: {age}
- Questions Answered: {len(answers)}

Stress Type Classification:
- Type: {stress_type}

Overall Stress Level:
- Level: {stress_level}
- Score: {percentage:.1f}%
- Total Score: {total_score}

Stress Breakdown by Category:
"""
        for category, score in category_scores.items():
            report += f"\n  {category}: {score:.1f}/5"
        
        if top_stress_areas:
            report += "\n\nTop Stress Areas:"
            for item in top_stress_areas[:3]:
                report += f"\n  - {item['question']}: {item['score']}/5 ({item['level']})"
        
        report += "\n\nDetailed Answers:\n"
        for q_id, answer in sorted(answers.items()):
            if q_id >= 3:
                q_text = question_texts.get(q_id, f"Q{q_id}")
                report += f"\nQ{q_id}: {q_text}\n  Answer: {answer}\n"
        
        st.download_button(
            label="📥 Click to Download TXT",
            data=report,
            file_name=f"stress_test_report_{age}_{gender}.txt",
            mime="text/plain",
            use_container_width=True,
            key="txt_download"
        )

with col4:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("main.py")

with col5:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_id = ""
        st.rerun()

# ---------- FOOTER ----------
st.markdown("---")
st.caption("💡 This report is for informational purposes only. If you're experiencing severe stress, please consult a mental health professional.")