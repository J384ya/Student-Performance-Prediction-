# 🎓 Student Performance Prediction System

A full-stack web application that **predicts student performance** using machine learning and provides smart insights to help them improve.

Built with **Flask + MS SQL Server + Scikit-learn + Chart.js** — perfect for academic evaluation and real-world applications.

---

## 🚀 Features

✅ Student login/signup  
✅ Predict performance using ML model  
✅ Manual data entry or CSV upload  
✅ Smart suggestions based on prediction  
✅ Export data to PDF  
✅ Analytics dashboard with charts  
✅ Recent uploads table  
✅ Responsive Bootstrap design

---

## 🛠️ Tech Stack

| Layer        | Technology                      |
|--------------|---------------------------------|
| Frontend     | HTML, CSS, Bootstrap, Chart.js  |
| Backend      | Python, Flask                   |
| ML Model     | Scikit-learn (Linear Regression)|
| Database     | MS SQL Server (via pyodbc)      |
| Reports      | PDF (via xhtml2pdf / Pisa)      |

---

## 🗂️ Folder Structure

student_app/ ├── static/ │ └── img/ # Icons, logos ├── templates/ # HTML templates (Jinja2) │ ├── base.html # Layout │ ├── login.html │ ├── signup.html │ ├── dashboard.html │ ├── upload.html │ ├── export.html │ └── analytics.html ├── model.pkl # Trained ML model ├── model_training.py # Script to train model ├── app.py # Main Flask backend ├── db_connection.py # MS SQL connection helper └── README.md # You’re here!

To install everything from it
pip install -r requirements.txt

Train the Model
python model_training.py

Start the App
python app.py


📈 ML Model Details
Algorithm: Linear Regression

Input Features:

Study Hours per Day

Attendance Percentage

Previous Exam Score

Output: Final Predicted Score



👩‍💻 Author
Jatin
Final Year Student, Sagar Institute of Science & Technology 
Mentor: Prof. Jai Mungi 
Project Type: Major Project (2024–2025)

📄 License

This project is open-source and intended for academic purposes only.

