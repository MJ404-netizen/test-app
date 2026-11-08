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
from datetime import datetime, timezone, timedelta
import json
import os
from utils.txt_generator import generate_txt_report
from utils.svm_predictor import predict_stress_type
from utils.pdf_generator import generate_pdf_report

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Stress Test Results",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- LOAD IMAGES AS BASE64 ----------
def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip1sAAAAASUVORK5CYII="
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

profile_img_base64 = get_base64_image("sources/profile.png")
home_img_base64 = get_base64_image("sources/home.png")

# ---------- CSS ----------
hide_streamlit_style = f"""
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* --- PUSH CONTENT LOWER --- */
        .block-container {{
            padding-top: 5rem !important; 
            padding-bottom: 2rem !important;
        }}
        .stApp > header {{
            display: none !important;
        }}
        h1 {{
            margin-top: -1rem !important;
            padding-top: 0 !important;
        }}
        /* --------------------------- */

        .stApp {{
            background: linear-gradient(#c7f9ff, #dafbff, #fbffdb, #d5f7cb, #c7f9ff) !important;
        }}
        
        .result-card {{
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            padding: 25px 30px;
            margin: 15px 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.10);
            border-left: 6px solid #4CAF50;
        }}
        
        .stress-type-title {{
            font-size: 24px;
            font-weight: 600;
            padding: 10px 20px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stress-eustress {{ background: #BBDEFB; color: #0D47A1; }}
        .stress-distress {{ background: #FFCDD2; color: #B71C1C; }}
        .stress-no-stress {{ background: #C8E6C9; color: #1B5E20; }}
        
        .recommendation-box {{
            background: #E3F2FD;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #1976D2;
        }}

        /* ---------- OVAL ACTION BUTTONS (BOTTOM) ---------- */
        div[data-testid="stHorizontalBlock"] div.stButton > button,
        div[data-testid="stHorizontalBlock"] div.stDownloadButton > button {{
            border-radius: 50px !important;
            padding: 10px 20px !important;
            width: 150px !important;
            height: 60px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-weight: 600 !important;
            font-size: 16px !important; 
            border: none !important;
            transition: all 0.2s ease !important;
        }}

        /* Force the text inside these specific buttons to be 16px */
        div[data-testid="stHorizontalBlock"] div.stButton > button p,
        div[data-testid="stHorizontalBlock"] div.stDownloadButton > button p {{
            font-size: 12px !important;
            font-weight: 600 !important;
            margin: 0 !important;
            color: white !important;
        }}

        /* ---------- TXT DOWNLOAD BUTTON TEXT COLOUR ---------- */
        .st-key-download_txt_btn button,
        .st-key-download_txt_btn button *,
        .st-key-download_txt_btn button p,
        .st-key-download_txt_btn button span,
        .st-key-download_txt_btn button div {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }}

        /* Hover effects for action buttons */
        div[data-testid="stHorizontalBlock"] div.stButton > button:hover,
        div[data-testid="stHorizontalBlock"] div.stDownloadButton > button:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15) !important;
        }}

        /* ---------- GO TO LOGIN BUTTON (When not logged in) ---------- */
        /* This targets buttons OUTSIDE the horizontal block (like Go to Login) */
        div.stButton > button {{
            width: 100% !important;
            border-radius: 60px !important;
            padding: 15px 20px !important;
            font-size: 24px !important;
            font-weight: 700 !important;
            border: none !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            text-align: center !important;
            min-height: 60px !important;
            background: #4CAF50 !important;
            color: white !important;
            margin-top: 15px !important;
        }}
        div.stButton > button:hover {{
            background: #43A047 !important;
            box-shadow: 0 14px 34px rgba(76, 175, 80, 0.40) !important;
            transform: translateY(-3px);
        }}
        div.stButton > button p {{
            color: white !important;
            font-size: 24px !important;
            font-weight: 700 !important;
        }}

        /* ---------- FORCE NAVIGATION TO ABSOLUTE CORNERS ---------- */
        div[data-testid="stHorizontalBlock"]:has(.st-key-home_button) {{
            position: relative !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            margin-top: -3rem !important; 
            margin-bottom: 2rem !important;
        }}

        .st-key-home_button {{
            position: absolute !important;
            left: 0 !important;
            top: 0 !important;
        }}

        .st-key-home_button button {{
            width: 50px !important;
            height: 50px !important;
            min-width: 50px !important;
            min-height: 50px !important;
            padding: 0 !important;
            margin: 0 !important;
            background-color: transparent !important;
            background-image: url("data:image/png;base64,{home_img_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border: none !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}

        .st-key-home_button button:hover {{
            transform: scale(1.08) !important;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25) !important;
        }}

        .st-key-home_button button p {{
            display: none !important;
        }}

        .st-key-logout_button {{
            position: absolute !important;
            right: 0 !important;
            top: 0 !important;
        }}

        .st-key-logout_button button {{
            width: 50px !important;
            height: 50px !important;
            min-width: 50px !important;
            min-height: 50px !important;
            padding: 0 !important;
            margin: 0 !important;
            background-color: transparent !important;
            background-image: url("data:image/png;base64,{profile_img_base64}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            border: none !important;
            border-radius: 50% !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }}

        .st-key-logout_button button:hover {{
            transform: scale(1.08) !important;
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25) !important;
        }}

        .st-key-logout_button button p {{
            display: none !important;
        }}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ---------- CHECK LOGIN ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login to access this page.")
    if st.button("🔐 Go to Login"):
        st.switch_page("pages/login.py")
    st.stop()

# ---------- TOP NAVIGATION: FORCED LEFT & RIGHT ----------
with st.container():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown('<div class="st-key-home_button">', unsafe_allow_html=True)
        if st.button("Home", key="home_button", help="Go to Home"):
            st.session_state.viewing_history = False
            st.switch_page("pages/test_page.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="st-key-logout_button">', unsafe_allow_html=True)
        if st.button("Logout", key="logout_button", help="Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------- CHECK IF TEST IS COMPLETED ----------
if not st.session_state.get("test_completed", False):
    st.warning("⚠️ Please complete the stress test first to view results.")
    if st.button("📝 Take the Test"):
        st.switch_page("pages/test_questions.py")
    st.stop()

# ---------- HEADER ----------
st.write("")
st.title("📊 Stress Test Results")

# ---------- GET USER DATA ----------
gender = st.session_state.get("gender", "Not specified")
gender_code = st.session_state.get("gender_code", "N/A")
age = st.session_state.get("age", "N/A")
answers = st.session_state.get("answers", {})

# ---------- DEFINE QUESTION MAPPING ----------
def get_question_mapping():
    question_texts = {
        1: "What is your gender?", 2: "What is your age?", 3: "Have you recently experienced stress in your life?",
        4: "Have you noticed a rapid heartbeat or palpitations?", 5: "Have you been dealing with anxiety or tension recently? (How Serious is it?)",
        6: "Do you face any sleep problems or difficulties falling asleep?", 7: "How often have you been dealing with anxiety or tension recently?",
        8: "Have you been getting headaches more than usual?", 9: "Do you get irritated easily?", 10: "Do you have trouble concentrating on your academic tasks?",
        11: "Have you been feeling sadness or low mood?", 12: "Have you been experiencing any illness or health issues?", 13: "Do you often feel lonely or isolated?",
        14: "Do you feel overwhelmed with your academic workload?", 15: "Are you in competition with your peers, and does it affect you?",
        16: "Do you find that your relationship often causes you stress?", 17: "Are you facing any difficulties with your professors or instructors?",
        18: "Is your working environment unpleasant or stressful?", 19: "Do you struggle to find time for relaxation and leisure activities?",
        20: "Is your hostel or home environment causing you difficulties?", 21: "Do you lack confidence in your academic performance?",
        22: "Do you lack confidence in your choice of academic subjects?", 23: "Academic and extracurricular activities conflicting for you?",
        24: "Do you attend classes regularly?", 25: "Have you gained/lost weight?"
    }
    
    categories = {
        "🩺 Physical & Health Indicators": {"ids": [8, 12, 25], "questions": []},
        "😰 Emotional & Stress Indicators": {"ids": [3, 4, 5, 6, 7, 9, 10, 11, 13], "questions": []},
        "📚 Academic & Environment Stressors": {"ids": [14, 15, 17, 18, 20, 21, 22, 23, 24], "questions": []},
        "💬 Social & Relationship Factors": {"ids": [16, 19], "questions": []}
    }
    return question_texts, categories

# ---------- ANALYZE RESPONSES ----------
def calculate_stress_score(answers):
    stress_answers = {int(k): v for k, v in answers.items() if int(k) >= 3}
    if not stress_answers: return 0, 0
    scores = []
    for answer in stress_answers.values():
        try:
            score = int(answer.split(" - ")[0])
            scores.append(score)
        except: continue
    total_score = sum(scores)
    max_possible = len(scores) * 5
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    return total_score, percentage

def calculate_stress_type(answers, categories):
    answers = {int(k): v for k, v in answers.items()}
    category_scores = {}
    for category_name, category_data in categories.items():
        scores = []
        for q_id in category_data["ids"]:
            if q_id in answers:
                try:
                    score = int(answers[q_id].split(" - ")[0])
                    scores.append(score)
                except: continue
        if scores: category_scores[category_name] = sum(scores) / len(scores)
    if not category_scores: return "No Stress", "stress-no-stress", "😌"
    avg_score = sum(category_scores.values()) / len(category_scores)
    emotional = category_scores.get("😰 Emotional & Stress Indicators", 0)
    physical = category_scores.get("🩺 Physical & Health Indicators", 0)
    academic = category_scores.get("📚 Academic & Environment Stressors", 0)
    
    if emotional >= 3.5 and physical >= 3.0: return "Distress", "stress-distress", "😰"
    elif 2.5 <= emotional < 3.5 and physical < 3.0 and academic >= 3.0: return "Eustress", "stress-eustress", "💪"
    elif avg_score < 2.0: return "No Stress", "stress-no-stress", "😌"
    elif avg_score < 2.5: return "No Stress", "stress-no-stress", "😌"
    elif avg_score < 3.5: return "Eustress", "stress-eustress", "💪"
    else: return "Distress", "stress-distress", "😰"

def calculate_category_scores(answers, categories):
    answers = {int(k): v for k, v in answers.items()}
    category_scores, category_details = {}, {}
    for category_name, category_data in categories.items():
        scores = []
        for q_id in category_data["ids"]:
            if q_id in answers:
                try:
                    score = int(answers[q_id].split(" - ")[0])
                    scores.append(score)
                except: continue
        if scores:
            avg_score = sum(scores) / len(scores)
            category_scores[category_name] = avg_score
            category_details[category_name] = {"average": avg_score, "max": max(scores), "min": min(scores), "count": len(scores)}
    return category_scores, category_details

def get_top_stress_areas(answers, categories, question_texts):
    answers = {int(k): v for k, v in answers.items()}
    stress_items = []
    for category_name, category_data in categories.items():
        for q_id in category_data["ids"]:
            if q_id in answers:
                try:
                    score = int(answers[q_id].split(" - ")[0])
                    if score >= 4:
                        stress_items.append({"question": question_texts[q_id], "category": category_name, "score": score, "level": "High" if score == 5 else "Moderate-High"})
                except: continue
    stress_items.sort(key=lambda x: x["score"], reverse=True)
    return stress_items[:5]

def save_test_history(answers, gender, gender_code, age, stress_type, percentage, svm_confidence, category_scores, top_stress_areas, svm_probabilities):
    username = st.session_state.get("username", "default")
    history_file = f"user_history_{username}.json"
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f: history = json.load(f)
        except: history = []
        
    utc_now = datetime.now(timezone.utc)
    my_time = utc_now + timedelta(hours=8)
    current_time = my_time.strftime("%Y-%m-%d %H:%M:%S")
    
    entry = {
        "date": current_time, 
        "gender": gender, 
        "gender_code": gender_code, 
        "age": age, 
        "stress_type": stress_type, 
        "percentage": percentage, 
        "svm_confidence": svm_confidence,
        "svm_probabilities": svm_probabilities,
        "category_scores": category_scores,
        "top_stress_areas": top_stress_areas,
        "answers": answers, 
        "total_questions": len(answers)
    }
    
    history.insert(0, entry)
    history = history[:100]
    with open(history_file, 'w') as f: json.dump(history, f, indent=2)
    return entry

# ---------- LOAD DATA ----------
question_texts, categories = get_question_mapping()

# ---------- CALCULATE RESULTS ----------
if st.session_state.get("viewing_history", False):
    total_score = 0 
    percentage = st.session_state.get("saved_percentage", 0)
    stress_type = st.session_state.get("saved_stress_type", "No Stress")
    svm_confidence = st.session_state.get("saved_svm_confidence", None)
    svm_probabilities = st.session_state.get("saved_svm_probabilities", None)
    category_scores = st.session_state.get("saved_category_scores", {})
    top_stress_areas = st.session_state.get("saved_top_stress_areas", [])
    
    _, category_details = calculate_category_scores(answers, categories)
else:
    total_score, percentage = calculate_stress_score(answers)
    svm_confidence = None
    svm_probabilities = None
    svm_error = None

    try:
        svm_output = predict_stress_type(answers=answers, gender_code=gender_code, age=age)
        stress_type, svm_confidence, svm_probabilities = svm_output['type'], svm_output['confidence'], svm_output['probabilities']
    except Exception as e:
        svm_error = str(e)
        stress_type, _, _ = calculate_stress_type(answers, categories)

    category_scores, category_details = calculate_category_scores(answers, categories)
    top_stress_areas = get_top_stress_areas(answers, categories, question_texts)

    if svm_error: st.warning(f"⚠️ SVM model unavailable — using rule-based fallback. ({svm_error})")

STRESS_TYPE_STYLE = {"Eustress": ("stress-eustress", "💪"), "Distress": ("stress-distress", "😰"), "No Stress": ("stress-no-stress", "😌")}
stress_type_class, stress_type_emoji = STRESS_TYPE_STYLE.get(stress_type, ("stress-no-stress", "😌"))

should_save = not st.session_state.get("viewing_history", False) and not st.session_state.get("history_saved", False)
if should_save:
    save_test_history(answers, gender, gender_code, age, stress_type, percentage, svm_confidence, category_scores, top_stress_areas, svm_probabilities)
    st.session_state.history_saved = True

utc_now = datetime.now(timezone.utc)
my_time = utc_now + timedelta(hours=8)
file_date_str = my_time.strftime('%Y%m%d')
current_time_str = my_time.strftime("%Y-%m-%d %H:%M") 

# ---------- DISPLAY RESULTS ----------
st.markdown(f"""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #4CAF50; margin-top: 15px; padding: 25px;">
<h3 style="margin-top: 0; color: #000000; text-align: left; margin-bottom: 20px;">👤 User Information</h3>
<div style="display: flex; justify-content: space-between; width: 100%;">
<div style="flex: 1;"><div style="font-size: 14px; color: #666; margin-bottom: 5px;">Gender</div><div style="font-size: 28px; font-weight: 600; color: #333;">{gender}</div></div>
<div style="flex: 1;"><div style="font-size: 14px; color: #666; margin-bottom: 5px;">Gender Code</div><div style="font-size: 28px; font-weight: 600; color: #333;">{gender_code}</div></div>
<div style="flex: 1;"><div style="font-size: 14px; color: #666; margin-bottom: 5px;">Age</div><div style="font-size: 28px; font-weight: 600; color: #333;">{age}</div></div>
<div style="flex: 1;"><div style="font-size: 14px; color: #666; margin-bottom: 5px;">Questions Answered</div><div style="font-size: 28px; font-weight: 600; color: #333;">{len(answers)}</div></div>
</div></div>""", unsafe_allow_html=True)

if svm_confidence is not None:
    conf_html = f'<div style="margin-top:15px;font-size:16px;color:#333;">🤖 <b>Model confidence:</b> {svm_confidence*100:.1f}%</div>'
    source_note = "Predicted by SVM classifier"
else:
    conf_html = ""
    source_note = "Based on rule-based analysis"

st.markdown(f"""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #9C27B0; margin-top: 15px; text-align: center;">
<h3 style="margin-top: 0; color: #000000; text-align: left; margin-bottom: 20px;">🧠 Your Stress Type Classification</h3>
<div style="font-size: 72px; margin: 10px 0;">{stress_type_emoji}</div>
<div class="stress-type-title {stress_type_class}" style="font-size: 32px; display: inline-block; padding: 10px 30px; margin-bottom: 15px;">{stress_type}</div>
{conf_html}<div style="margin-top: 12px; font-size: 14px; color: #888;">{source_note}</div></div>""", unsafe_allow_html=True)

if svm_probabilities:
    st.markdown("### 📊 Prediction Confidence Breakdown")
    prob_df = pd.DataFrame({'Stress Type': list(svm_probabilities.keys()), 'Probability': [v * 100 for v in svm_probabilities.values()]})
    color_map = {'Distress': '#F44336', 'Eustress': '#2196F3', 'No Stress': '#4CAF50'}
    fig_prob = go.Figure(go.Bar(x=prob_df['Stress Type'], y=prob_df['Probability'], marker_color=[color_map.get(c, '#999') for c in prob_df['Stress Type']], text=[f"{p:.1f}%" for p in prob_df['Probability']], textposition='auto'))
    fig_prob.update_layout(yaxis_title="Probability (%)", yaxis=dict(range=[0, 100]), height=300, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_prob, use_container_width=True)
    if svm_confidence is not None and svm_confidence < 0.6:
        st.warning(f"⚠️ Model confidence is only {svm_confidence*100:.1f}%. Your responses span multiple stress patterns. Consider retaking the test or consulting a professional.")

if stress_type == "Eustress":
    st.markdown("""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #0D47A1;"><h3>💪 Eustress - The "Good" Stress</h3><p><strong>What it means: You're experiencing positive, motivating stress that helps you perform at your best.</strong></p><ul><li>You feel challenged but capable</li><li>This stress helps you focus and achieve goals</li><li>You're engaged and motivated</li><li>Your physical health indicators are generally good</li></ul></div>""", unsafe_allow_html=True)
elif stress_type == "Distress":
    st.markdown("""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #B71C1C;"><h3>😰 Distress - The "Bad" Stress</h3><p><strong>What it means: You're experiencing overwhelming stress that's negatively affecting your well-being.</strong></p><ul><li>You feel overwhelmed and unable to cope</li><li>Physical symptoms like headaches or sleep issues are present</li><li>Your emotional well-being is significantly impacted</li><li>This stress is interfering with your daily life</li></ul></div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #1B5E20;"><h3>😌 No Stress - The Calm State</h3><p><strong>What it means: You're experiencing very low levels of stress in your life.</strong></p><ul><li>You feel calm and balanced</li><li>You're managing daily challenges well</li><li>Your physical and emotional health are stable</li><li>You have good coping mechanisms</li></ul></div>""", unsafe_allow_html=True)

if category_scores:
    st.markdown("### 📊 Stress Breakdown by Category")
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        categories_list = list(category_scores.keys())
        scores = list(category_scores.values())
        colors_list = ['#4CAF50' if s < 2.5 else '#FF9800' if s < 3.5 else '#F44336' for s in scores]
        fig2 = go.Figure(data=[go.Bar(x=categories_list, y=scores, marker_color=colors_list, text=[f"{s:.1f}" for s in scores], textposition='auto', name='Average Score')])
        fig2.update_layout(title="Average Stress Score by Category (1-5 scale)", xaxis_title="Category", yaxis_title="Average Score", yaxis=dict(range=[0, 5]), height=350, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    with st.expander("📋 View Category Details"):
        df_details = pd.DataFrame([{"Category": name, "Average Score": f"{d['average']:.1f}", "Highest Score": d['max'], "Lowest Score": d['min'], "Questions": d['count']} for name, d in category_details.items()])
        st.dataframe(df_details, use_container_width=True, hide_index=True)

if top_stress_areas:
    areas_html = "".join([f'<div style="display: flex; align-items: flex-start; gap: 15px; padding: 12px 0; margin-bottom: 5px;"><div style="font-size: 24px; margin-top: 2px;">{"🔴" if item["level"] == "High" else "🟠"}</div><div style="flex: 1;"><div style="font-weight: 600; font-size: 16px; color: #333;">{item["question"]}</div><div style="font-size: 14px; color: #666; margin-top: 4px;">{item["category"]} • Score: {item["score"]}/5 - {item["level"]} Level</div></div></div>' for item in top_stress_areas])
    st.markdown(f"""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #F44336; margin-top: 15px;"><h3 style="margin-top: 0; color: #000000;">🎯 Top Stress Areas</h3><p style="color: #666; margin-bottom: 15px;">Here are your top stress areas that may need attention:</p>{areas_html}</div>""", unsafe_allow_html=True)
else:
    st.info("✅ No high-stress areas identified. Keep up the good work!")

if stress_type == "Eustress":
    st.markdown("""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #0D47A1;">
    <h3 style="margin-top: 0; color: #000000;">💡 Personalized Recommendations</h3>
    <ul>
        <li><strong>Self care:</strong> Prioritize self-care activities to maintain well-being and prevent eustress from turning into distress</li>
        <li><strong>Channel your energy:</strong> Use this motivating stress to tackle challenging projects and goals</li>
        <li><strong>Maintain balance:</strong> Continue your healthy routines that are working well</li>
        <li><strong>Set new challenges:</strong> Consider taking on new learning opportunities or responsibilities</li>
        <li><strong>Practice mindfulness:</strong> Stay present and enjoy your accomplishments</li>
        <li><strong>Share your strategies:</strong> Help others who may be struggling with stress</li>
    </ul>
    </div>""", unsafe_allow_html=True)
elif stress_type == "Distress":
    st.markdown("""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #B71C1C;">
    <h3 style="margin-top: 0; color: #000000;">💡 Personalized Recommendations</h3>
    <ul>
        <li><strong>Seek support:</strong> Talk to a counselor, therapist, or trusted friend</li>
        <li><strong>Practice relaxation:</strong> Try deep breathing, meditation, or yoga daily</li>
        <li><strong>Prioritize self-care:</strong> Ensure adequate sleep, nutrition, and exercise</li>
        <li><strong>Set boundaries:</strong> Learn to say no and protect your time</li>
        <li><strong>Break tasks down:</strong> Divide overwhelming tasks into smaller, manageable steps</li>
        <li><strong>Consider professional help:</strong> If distress persists, seek professional mental health support</li>
        <li><strong>Self Assessment:</strong> Regularly assess your stress levels and triggers</li>
    </ul>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #1B5E20;">
    <h3 style="margin-top: 0; color: #000000;">💡 Personalized Recommendations</h3>
    <ul>
        <li><strong>Stay engaged:</strong> Consider new challenges to maintain growth and development</li>
        <li><strong>Build resilience:</strong> Continue developing coping skills for future challenges</li>
        <li><strong>Maintain connections:</strong> Keep nurturing your relationships and social network</li>
        <li><strong>Practice gratitude:</strong> Appreciate your current balanced state</li>
        <li><strong>Plan ahead:</strong> Set goals that will keep you motivated and fulfilled</li>
    </ul>
    </div>""", unsafe_allow_html=True)

if top_stress_areas:
    specific_tips_html = ""
    shown_tips = set()
    for item in top_stress_areas[:3]:
        q_lower = item["question"].lower()
        if "sleep" in q_lower and "sleep" not in shown_tips: specific_tips_html += "<li><strong>Sleep Tips:</strong> Maintain a consistent sleep schedule.</li>"; shown_tips.add("sleep")
        elif ("anxiety" in q_lower or "tension" in q_lower) and "anxiety" not in shown_tips: specific_tips_html += "<li><strong>Anxiety Management:</strong> Practice deep breathing exercises.</li>"; shown_tips.add("anxiety")
        elif ("competition" in q_lower or "peers" in q_lower) and "competition" not in shown_tips: specific_tips_html += "<li><strong>Peer Competition:</strong> Focus on your personal growth.</li>"; shown_tips.add("competition")
        elif ("academic" in q_lower or "workload" in q_lower or "classes" in q_lower) and "academic" not in shown_tips: specific_tips_html += "<li><strong>Academic Stress:</strong> Break tasks into smaller chunks.</li>"; shown_tips.add("academic")
        elif "relationship" in q_lower and "relationship" not in shown_tips: specific_tips_html += "<li><strong>Relationships:</strong> Communicate openly.</li>"; shown_tips.add("relationship")
        elif ("confidence" in q_lower or "performance" in q_lower) and "confidence" not in shown_tips: specific_tips_html += "<li><strong>Building Confidence:</strong> Celebrate small wins.</li>"; shown_tips.add("confidence")
        elif ("health" in q_lower or "illness" in q_lower) and "health" not in shown_tips: specific_tips_html += "<li><strong>Health Concerns:</strong> Schedule a check-up.</li>"; shown_tips.add("health")
        elif ("lonely" in q_lower or "isolated" in q_lower) and "lonely" not in shown_tips: specific_tips_html += "<li><strong>Social Connection:</strong> Join a club or group activity.</li>"; shown_tips.add("lonely")
        elif ("environment" in q_lower or "hostel" in q_lower or "working" in q_lower) and "environment" not in shown_tips: specific_tips_html += "<li><strong>Environment:</strong> Create a comfortable workspace.</li>"; shown_tips.add("environment")
        elif ("heartbeat" in q_lower or "palpitations" in q_lower) and "heartbeat" not in shown_tips: specific_tips_html += "<li><strong>Physical Symptoms:</strong> Practice deep breathing.</li>"; shown_tips.add("heartbeat")
        elif "irritated" in q_lower and "irritated" not in shown_tips: specific_tips_html += "<li><strong>Irritability:</strong> Practice mindfulness.</li>"; shown_tips.add("irritated")
        elif ("extracurricular" in q_lower or "activities" in q_lower) and "activities" not in shown_tips: specific_tips_html += "<li><strong>Work-Life Balance:</strong> Prioritize activities.</li>"; shown_tips.add("activities")
        elif "weight" in q_lower and "weight" not in shown_tips: specific_tips_html += "<li><strong>Weight Management:</strong> Consult a nutritionist.</li>"; shown_tips.add("weight")
    
    if specific_tips_html:
        st.markdown(f"""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #FF9800; margin-top: 15px;"><h3 style="margin-top: 0; color: #000000;">🎯 Specific Recommendations for Your Top Stress Areas</h3><ul style="margin-bottom: 0;">{specific_tips_html}</ul></div>""", unsafe_allow_html=True)

# Row 8: Detailed Response Summary
response_data = []
# Force ascending order by converting keys to integers for sorting
sorted_answers = sorted(answers.items(), key=lambda x: int(x[0]))

for q_id, answer in sorted_answers:
    q_id_int = int(q_id)
    if q_id_int >= 3:
        category_name = next((cat for cat, data in categories.items() if q_id_int in data["ids"]), "Other")
        question_text = question_texts.get(q_id_int, f"Q{q_id_int}")
        try: score = int(answer.split(" - ")[0])
        except: score = "-"
        response_data.append({"Question ID": q_id_int, "Category": category_name, "Question": question_text[:60] + ("..." if len(question_text) > 60 else ""), "Score": score, "Response": answer})

if response_data:
    st.markdown("""<div class="recommendation-box" style="background: #FFFFFF; border-left-color: #FF9800; margin-top: 15px; padding-bottom: 5px; border-bottom-left-radius: 0; border-bottom-right-radius: 0; margin-bottom: 0;"><h3 style="margin-top: 0; color: #000000; text-align: left; margin-bottom: 10px;">📝 Detailed Response Summary</h3></div>""", unsafe_allow_html=True)
    with st.container():
        st.markdown("""<style>div[data-testid="stExpander"] {background-color: #FFFFFF; border-left: 4px solid #FF9800; border-radius: 0 0 12px 12px; padding: 0px 15px 15px 15px; margin-top: -15px;}</style>""", unsafe_allow_html=True)
        with st.expander("View All Responses"):
            df_responses = pd.DataFrame(response_data)
            st.dataframe(df_responses, use_container_width=True, hide_index=True, column_config={"Question ID": st.column_config.NumberColumn("Q#"), "Category": st.column_config.TextColumn("Category"), "Question": st.column_config.TextColumn("Question"), "Score": st.column_config.NumberColumn("Score (1-5)"), "Response": st.column_config.TextColumn("Your Answer")})
            
# Row 9: Action Buttons
st.write("")

# Check if viewing history to hide retake button and align downloads
is_viewing_history = st.session_state.get("viewing_history", False)

if is_viewing_history:
    # Align Download Buttons to the right side
    col1, col2, col3, col4 = st.columns([1, 5, 1, 1])
    
    with col3:
        pdf_buffer = generate_pdf_report(
            gender, gender_code, age, answers, question_texts, categories, 
            total_score, percentage, stress_type, category_scores, top_stress_areas, 
            svm_confidence,
            current_time_str
        )
        st.download_button(label="📄 Download PDF", data=pdf_buffer, file_name=f"stress_test_report_{age}_{gender}_{file_date_str}.pdf", mime="application/pdf", use_container_width=True, type="primary")

    with col4:
        txt_report = generate_txt_report(
            gender, gender_code, age, answers, question_texts, categories, 
            total_score, percentage, stress_type, category_scores, top_stress_areas,
            current_time_str
        )
        st.download_button(
            label="📄 Download TXT", 
            data=txt_report, 
            file_name=f"stress_test_report_{age}_{gender}_{file_date_str}.txt", 
            mime="text/plain", 
            use_container_width=True,
            key="download_txt_btn" # <--- ADDED THIS KEY
        )

else:
    # Original Layout with Retake Button
    col1, col2, col3, col4 = st.columns([1, 5, 1, 1])
    
    with col1:
        if st.button("🔄 Retake Test", key="retake_test_btn", use_container_width=True):
            st.session_state.current_q_index = 0
            st.session_state.answers = {}
            st.session_state.user_responses = {}
            st.session_state.formatted_answers = {}
            st.session_state.test_completed = False
            st.session_state.gender = None
            st.session_state.gender_code = None
            st.session_state.age = None
            st.session_state.viewing_history = False
            st.session_state.history_saved = False
            st.switch_page("pages/test_questions.py")

    with col3:
        pdf_buffer = generate_pdf_report(
            gender, gender_code, age, answers, question_texts, categories, 
            total_score, percentage, stress_type, category_scores, top_stress_areas, 
            svm_confidence,
            current_time_str
        )
        st.download_button(label="📄 Download PDF", data=pdf_buffer, file_name=f"stress_test_report_{age}_{gender}_{file_date_str}.pdf", mime="application/pdf", use_container_width=True, type="primary")

    with col4:
        txt_report = generate_txt_report(
            gender, gender_code, age, answers, question_texts, categories, 
            total_score, percentage, stress_type, category_scores, top_stress_areas,
            current_time_str
        )
        st.download_button(
            label="📄 Download TXT", 
            data=txt_report, 
            file_name=f"stress_test_report_{age}_{gender}_{file_date_str}.txt", 
            mime="text/plain", 
            use_container_width=True,
            key="download_txt_btn" # <--- ADDED THIS KEY
        )

# ---------- FOOTER ----------
st.markdown(
    "<p style='color: black; font-weight: bold; font-size: 14px;'>"
    "💡 This report is for informational purposes only. If you're experiencing severe stress, please consult a mental health professional."
    "</p>", 
    unsafe_allow_html=True
)