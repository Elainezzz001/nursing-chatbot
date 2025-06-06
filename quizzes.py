quiz_data = [
    {
        "question": "What is the normal respiratory rate for a 1-year-old?",
        "options": ["10-20", "20-30", "25-45", "60-80"],
        "answer": "25-45"
    },
    {
        "question": "What is the recommended fluid requirement for a 12kg child?",
        "options": ["1200 mL", "1000 mL", "1100 mL", "1400 mL"],
        "answer": "1100 mL"
    },
    {
        "question": "What does a widened pulse pressure indicate in children?",
        "options": ["Cardiogenic shock", "Distributive shock", "Hypovolemic shock", "Normal condition"],
        "answer": "Distributive shock"
    }
]

def streamlit_quiz_ui():
    import streamlit as st
    st.subheader("📝 Nursing Quiz")
    score = 0
    for idx, item in enumerate(quiz_data):
        st.markdown(f"**Q{idx+1}: {item['question']}**")
        selected = st.radio("", item['options'], key=idx)
        if st.button(f"Check Answer {idx+1}", key=f"check{idx}"):
            if selected == item['answer']:
                st.success("✅ Correct!")
                score += 1
            else:
                st.error(f"❌ Incorrect. Correct answer is: {item['answer']}")
    st.markdown(f"### 🏁 Final Score: {score}/{len(quiz_data)}")