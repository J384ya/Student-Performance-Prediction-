import streamlit as st
import numpy as np
import joblib

# Load your trained model
model = joblib.load("model.pkl")  # ← Load after training

st.title("📊 Student Performance Dashboard")

if st.session_state.get("logged_in"):
    st.subheader(f"Welcome, {st.session_state.username} 👋")

    # Input sliders
    hours = st.slider("🕒 Study Hours per Day", 0.0, 10.0, 2.0)
    attendance = st.slider("🎓 Attendance (%)", 0, 100, 80)
    prev_score = st.slider("📄 Previous Exam Score", 0, 100, 75)

    if st.button("🔍 Predict Performance"):
        input_data = np.array([[hours, attendance, prev_score]])
        prediction = model.predict(input_data)[0]

        st.success(f"📈 Predicted Final Score: **{prediction:.2f}**")
else:
    st.warning("Please login from the Home page first.")
