# utils/txt_generator.py
def generate_txt_report(gender, gender_code, age, answers, question_texts, categories,
                        total_score, percentage, stress_level, stress_type,
                        category_scores, top_stress_areas):
    """Generate TXT report"""
    
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
    
    return report