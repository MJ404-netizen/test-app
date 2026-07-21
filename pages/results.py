import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

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
        
        .recommendation-box {
            background: #E3F2FD;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #1976D2;
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
user_responses = st.session_state.get("user_responses", {})

# ---------- ANALYZE RESPONSES ----------
def calculate_stress_score(answers):
    """Calculate stress score from answers"""
    # Only count stress questions (id >= 3)
    stress_answers = {k: v for k, v in answers.items() if k >= 3}
    
    if not stress_answers:
        return 0, 0
    
    # Extract numeric values from answers (e.g., "1 - Never" -> 1)
    scores = []
    for answer in stress_answers.values():
        try:
            # Extract the number from the beginning of the string
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

def get_stress_category_scores(answers, questions):
    """Calculate stress scores by category"""
    categories = {
        "Physical Symptoms": [2, 6, 9],  # Heartbeat, headaches, illness
        "Emotional Well-being": [7, 8, 12, 14, 18],  # Irritated, concentration, loneliness, relationships
        "Academic Stress": [13, 15, 16, 19, 20, 21, 22],  # Competition, professors, environment, confidence, workload
        "Lifestyle Factors": [4, 5, 10, 11, 23]  # Sleep, anxiety, relaxation, classes, weight
    }
    
    category_scores = {}
    for category, question_ids in categories.items():
        scores = []
        for q_id in question_ids:
            if q_id in answers:
                try:
                    score = int(answers[q_id].split(" - ")[0])
                    scores.append(score)
                except:
                    continue
        if scores:
            category_scores[category] = sum(scores) / len(scores)  # Average score
    
    return category_scores

def get_top_stress_areas(answers):
    """Identify top stress areas"""
    stress_items = []
    for q_id, answer in answers.items():
        if q_id >= 3:  # Only stress questions
            try:
                score = int(answer.split(" - ")[0])
                if score >= 4:  # High stress (4 or 5)
                    stress_items.append({
                        "question": questions[q_id-1]["question"] if q_id-1 < len(questions) else f"Q{q_id}",
                        "score": score,
                        "level": "High" if score == 5 else "Moderate-High"
                    })
            except:
                continue
    
    # Sort by score (highest first)
    stress_items.sort(key=lambda x: x["score"], reverse=True)
    return stress_items[:5]  # Top 5 stress areas

# ---------- LOAD QUESTIONS FOR CONTEXT ----------
def load_questions():
    """Load questions for context"""
    # Define the questions (same as in stress_test.py)
    stress_questions = [
        "Have you recently experienced stress in your life?",
        "Have you noticed a rapid heartbeat or palpitations?",
        "Have you been dealing with anxiety or tension recently? (How Serious is it?)",
        "Do you face any sleep problems or difficulties falling asleep?",
        "How often have you been dealing with anxiety or tension recently?",
        "Have you been getting headaches more than usual?",
        "Do you get irritated easily?",
        "Do you have trouble concentrating on your academic tasks?",
        "Have you been feeling sadness or low mood?",
        "Have you been experiencing any illness or health issues?",
        "Do you often feel lonely or isolated?",
        "Do you feel overwhelmed with your academic workload?",
        "Are you in competition with your peers, and does it affect you?",
        "Do you find that your relationship often causes you stress?",
        "Are you facing any difficulties with your professors or instructors?",
        "Is your working environment unpleasant or stressful?",
        "Do you struggle to find time for relaxation and leisure activities?",
        "Is your hostel or home environment causing you difficulties?",
        "Do you lack confidence in your academic performance?",
        "Do you lack confidence in your choice of academic subjects?",
        "Academic and extracurricular activities conflicting for you?",
        "Do you attend classes regularly?",
        "Have you gained/lost weight?"
    ]
    
    questions = []
    # Add Gender as Question 1
    questions.append("What is your gender?")
    # Add Age as Question 2
    questions.append("What is your age?")
    # Add stress questions
    questions.extend(stress_questions)
    
    return questions

questions = load_questions()

# ---------- CALCULATE RESULTS ----------
total_score, percentage = calculate_stress_score(answers)
stress_level, stress_class, stress_emoji = get_stress_level(percentage)
category_scores = get_stress_category_scores(answers, questions)
top_stress_areas = get_top_stress_areas(answers)

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

# Row 2: Overall Stress Score
st.subheader("📈 Overall Stress Assessment")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Display stress level
    st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 72px; margin: 10px 0;">{stress_emoji}</div>
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

# Row 3: Stress Level Gauge Chart
st.subheader("📊 Stress Level Gauge")

# Create gauge chart
fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = percentage,
    title = {'text': "Stress Level (%)"},
    domain = {'x': [0, 1], 'y': [0, 1]},
    gauge = {
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

# Row 4: Category Scores
st.subheader("📊 Stress Breakdown by Category")

if category_scores:
    # Create a DataFrame for category scores
    categories = list(category_scores.keys())
    scores = list(category_scores.values())
    
    # Create color map
    colors = ['#4CAF50' if s < 3 else '#FF9800' if s < 4 else '#F44336' for s in scores]
    
    fig2 = go.Figure(data=[
        go.Bar(
            x=categories,
            y=scores,
            marker_color=colors,
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

st.markdown("---")

# Row 5: Top Stress Areas
st.subheader("🎯 Top Stress Areas")

if top_stress_areas:
    st.write("Here are your top stress areas that may need attention:")
    
    for i, item in enumerate(top_stress_areas, 1):
        color = "#F44336" if item["level"] == "High" else "#FF9800"
        icon = "🔴" if item["level"] == "High" else "🟠"
        st.markdown(f"""
            <div class="result-card result-card-danger" style="border-left-color: {color};">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 24px;">{icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 600; font-size: 16px;">{item['question']}</div>
                        <div style="font-size: 14px; color: #666;">
                            Score: {item['score']}/5 - {item['level']} Level
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.info("✅ No high-stress areas identified. Keep up the good work!")

st.markdown("---")

# Row 6: Recommendations
st.subheader("💡 Recommendations")

if stress_level == "Low Stress":
    st.markdown("""
        <div class="recommendation-box">
            <h4>🌟 You're Doing Great!</h4>
            <ul>
                <li>Continue maintaining your current healthy lifestyle</li>
                <li>Keep practicing stress management techniques</li>
                <li>Regular exercise and proper sleep are helping you</li>
                <li>Stay connected with friends and family</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
elif stress_level == "Moderate Stress":
    st.markdown("""
        <div class="recommendation-box">
            <h4>⚖️ Time to Take Action</h4>
            <ul>
                <li>Consider incorporating relaxation techniques like meditation or deep breathing</li>
                <li>Maintain a balanced routine with adequate sleep and exercise</li>
                <li>Talk to friends, family, or a counselor about your concerns</li>
                <li>Set realistic goals and prioritize your tasks</li>
                <li>Take regular breaks from work/study</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="recommendation-box" style="border-left-color: #F44336;">
            <h4>🚨 Professional Support Recommended</h4>
            <ul>
                <li><strong>Seek professional help</strong> - Consider talking to a counselor or therapist</li>
                <li>Practice stress reduction techniques daily (meditation, yoga, deep breathing)</li>
                <li>Reach out to your support network - friends, family, or support groups</li>
                <li>Consider taking a break from stressful activities</li>
                <li>Maintain a healthy lifestyle - proper nutrition, exercise, and sleep</li>
                <li>Contact your institution's counseling services for support</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# Specific recommendations based on top stress areas
if top_stress_areas:
    st.markdown("### 🎯 Specific Recommendations for Your Top Stress Areas:")
    
    for item in top_stress_areas[:3]:  # Top 3 areas
        if "sleep" in item["question"].lower():
            st.info("💤 **Sleep Tips**: Maintain a consistent sleep schedule, avoid screens before bed, create a relaxing bedtime routine")
        elif "anxiety" in item["question"].lower() or "tension" in item["question"].lower():
            st.info("🧘 **Anxiety Management**: Practice deep breathing exercises, try mindfulness meditation, talk to someone you trust")
        elif "academic" in item["question"].lower() or "workload" in item["question"].lower():
            st.info("📚 **Academic Stress**: Break tasks into smaller chunks, use a planner, take regular study breaks")
        elif "relationship" in item["question"].lower():
            st.info("❤️ **Relationships**: Communicate openly, set healthy boundaries, spend quality time with supportive people")
        elif "confidence" in item["question"].lower() or "performance" in item["question"].lower():
            st.info("💪 **Building Confidence**: Celebrate small wins, focus on progress not perfection, seek feedback constructively")

st.markdown("---")

# Row 7: Detailed Response Summary
st.subheader("📝 Detailed Response Summary")

# Create a DataFrame for all answers
response_data = []
for q_id, answer in sorted(answers.items()):
    if q_id >= 3:  # Only stress questions
        question_text = questions[q_id-1] if q_id-1 < len(questions) else f"Q{q_id}"
        response_data.append({
            "Question ID": q_id,
            "Question": question_text[:60] + ("..." if len(question_text) > 60 else ""),
            "Response": answer
        })

if response_data:
    df_responses = pd.DataFrame(response_data)
    
    # Use expander for detailed view
    with st.expander("View All Responses"):
        st.dataframe(
            df_responses,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Question ID": st.column_config.NumberColumn("Q#"),
                "Question": st.column_config.TextColumn("Question"),
                "Response": st.column_config.TextColumn("Your Answer")
            }
        )

st.markdown("---")

# Row 8: Action Buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔄 Retake Test", use_container_width=True):
        # Reset test state
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
    if st.button("📊 Download Report", use_container_width=True):
        # Create a downloadable report
        report = f"""
        STRESS TEST REPORT
        ===================
        
        Personal Information:
        - Gender: {gender} (Code: {gender_code})
        - Age: {age}
        - Questions Answered: {len(answers)}
        
        Overall Stress Level:
        - Level: {stress_level}
        - Score: {percentage:.1f}%
        - Total Score: {total_score}
        
        Stress Breakdown:
        """
        
        for category, score in category_scores.items():
            report += f"\n  - {category}: {score:.1f}/5"
        
        report += "\n\nDetailed Answers:\n"
        for q_id, answer in sorted(answers.items()):
            q_text = questions[q_id-1] if q_id-1 < len(questions) else f"Q{q_id}"
            report += f"\nQ{q_id}: {q_text}\n  Answer: {answer}\n"
        
        st.download_button(
            label="📥 Download Report",
            data=report,
            file_name=f"stress_test_report_{age}_{gender}.txt",
            mime="text/plain",
            use_container_width=True
        )

with col3:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("main.py")

with col4:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_id = ""
        st.rerun()

# ---------- FOOTER ----------
st.markdown("---")
st.caption("💡 This report is for informational purposes only. If you're experiencing severe stress, please consult a mental health professional.")