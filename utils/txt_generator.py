from datetime import datetime

def generate_txt_report(gender, gender_code, age, answers, question_texts, categories,
                        total_score, percentage, stress_type,
                        category_scores, top_stress_areas):
    """Generate TXT report"""
    
    report = f"""
STRESS TEST REPORT
===================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Personal Information:
- Gender: {gender} (Code: {gender_code})
- Age: {age}
- Questions Answered: {len(answers)}

Stress Type Classification:
- Type: {stress_type}

Stress Breakdown by Category:
"""
    
    for category, score in category_scores.items():
        report += f"\n  {category}: {score:.1f}/5"
    
    # Top 5 Stress Areas
    if top_stress_areas:
        report += "\n\nTop 5 Stress Areas:"
        report += "\nHere are your top stress areas that may need attention:"
        for i, item in enumerate(top_stress_areas[:5], 1):
            report += f"\n  {i}. {item['question']}"
            report += f"\n     {item['category']} • Score: {item['score']}/5 - {item['level']} Level"
    
    # Full Personalized Recommendations (Matches the UI)
    report += "\n\nPersonalized Recommendations:\n"
    if stress_type == "Eustress":
        report += "  • Self care: Prioritize self-care activities to maintain well-being and prevent eustress from turning into distress\n"
        report += "  • Channel your energy: Use this motivating stress to tackle challenging projects and goals\n"
        report += "  • Maintain balance: Continue your healthy routines that are working well\n"
        report += "  • Set new challenges: Consider taking on new learning opportunities or responsibilities\n"
        report += "  • Practice mindfulness: Stay present and enjoy your accomplishments\n"
        report += "  • Share your strategies: Help others who may be struggling with stress\n"
    elif stress_type == "Distress":
        report += "  • Seek support: Talk to a counselor, therapist, or trusted friend\n"
        report += "  • Practice relaxation: Try deep breathing, meditation, or yoga daily\n"
        report += "  • Prioritize self-care: Ensure adequate sleep, nutrition, and exercise\n"
        report += "  • Set boundaries: Learn to say no and protect your time\n"
        report += "  • Break tasks down: Divide overwhelming tasks into smaller, manageable steps\n"
        report += "  • Consider professional help: If distress persists, seek professional mental health support\n"
        report += "  • Self Assessment: Regularly assess your stress levels and triggers\n"
    else:
        report += "  • Stay engaged: Consider new challenges to maintain growth and development\n"
        report += "  • Build resilience: Continue developing coping skills for future challenges\n"
        report += "  • Maintain connections: Keep nurturing your relationships and social network\n"
        report += "  • Practice gratitude: Appreciate your current balanced state\n"
        report += "  • Plan ahead: Set goals that will keep you motivated and fulfilled\n"
        
    # Specific Recommendations for Top Areas
    if top_stress_areas:
        specific_tips_txt = ""
        shown_tips = set()
        for item in top_stress_areas[:3]:
            q_lower = item["question"].lower()
            if "sleep" in q_lower and "sleep" not in shown_tips: 
                specific_tips_txt += "  • Sleep Tips: Maintain a consistent sleep schedule.\n"
                shown_tips.add("sleep")
            elif ("anxiety" in q_lower or "tension" in q_lower) and "anxiety" not in shown_tips: 
                specific_tips_txt += "  • Anxiety Management: Practice deep breathing exercises.\n"
                shown_tips.add("anxiety")
            elif ("competition" in q_lower or "peers" in q_lower) and "competition" not in shown_tips: 
                specific_tips_txt += "  • Peer Competition: Focus on your personal growth.\n"
                shown_tips.add("competition")
            elif ("academic" in q_lower or "workload" in q_lower or "classes" in q_lower) and "academic" not in shown_tips: 
                specific_tips_txt += "  • Academic Stress: Break tasks into smaller chunks.\n"
                shown_tips.add("academic")
            elif "relationship" in q_lower and "relationship" not in shown_tips: 
                specific_tips_txt += "  • Relationships: Communicate openly.\n"
                shown_tips.add("relationship")
            elif ("confidence" in q_lower or "performance" in q_lower) and "confidence" not in shown_tips: 
                specific_tips_txt += "  • Building Confidence: Celebrate small wins.\n"
                shown_tips.add("confidence")
            elif ("health" in q_lower or "illness" in q_lower) and "health" not in shown_tips: 
                specific_tips_txt += "  • Health Concerns: Schedule a check-up.\n"
                shown_tips.add("health")
            elif ("lonely" in q_lower or "isolated" in q_lower) and "lonely" not in shown_tips: 
                specific_tips_txt += "  • Social Connection: Join a club or group activity.\n"
                shown_tips.add("lonely")
            elif ("environment" in q_lower or "hostel" in q_lower or "working" in q_lower) and "environment" not in shown_tips: 
                specific_tips_txt += "  • Environment: Create a comfortable workspace.\n"
                shown_tips.add("environment")
            elif ("heartbeat" in q_lower or "palpitations" in q_lower) and "heartbeat" not in shown_tips: 
                specific_tips_txt += "  • Physical Symptoms: Practice deep breathing.\n"
                shown_tips.add("heartbeat")
            elif "irritated" in q_lower and "irritated" not in shown_tips: 
                specific_tips_txt += "  • Irritability: Practice mindfulness.\n"
                shown_tips.add("irritated")
            elif ("extracurricular" in q_lower or "activities" in q_lower) and "activities" not in shown_tips: 
                specific_tips_txt += "  • Work-Life Balance: Prioritize activities.\n"
                shown_tips.add("activities")
            elif "weight" in q_lower and "weight" not in shown_tips: 
                specific_tips_txt += "  • Weight Management: Consult a nutritionist.\n"
                shown_tips.add("weight")
            
        if specific_tips_txt:
            report += "\nSpecific Recommendations for Your Top Stress Areas:\n"
            report += specific_tips_txt
    
    report += "\n\nDetailed Answers:\n"
    for q_id, answer in sorted(answers.items()):
        if q_id >= 3:
            q_text = question_texts.get(q_id, f"Q{q_id}")
            report += f"\nQ{q_id}: {q_text}\n  Answer: {answer}\n"
    
    return report