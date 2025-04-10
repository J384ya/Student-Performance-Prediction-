from flask import Flask, render_template, request, redirect, session, url_for
from db_connection import get_connection
import hashlib
from flask import render_template, make_response
from xhtml2pdf import pisa
import io


app = Flask(__name__)
app.secret_key = 'jATIN'  # Replace with secure key

@app.route('/')
def home():
    return redirect(url_for('login'))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        gmail = request.form['gmail']
        password = request.form['password']

        conn, cursor = get_connection()
        cursor.execute("SELECT * FROM Users WHERE Gmail=? AND PasswordHash=?", (gmail, hash_password(password)))
        user = cursor.fetchone()

        if user:
            session['username'] = user[2]  # assuming Name is 2nd column
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid Gmail or Password")

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        gmail = request.form['gmail']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            return render_template('signup.html', error="Passwords do not match")

        conn, cursor = get_connection()
        cursor.execute("SELECT * FROM Users WHERE Gmail=?", (gmail,))
        if cursor.fetchone():
            return render_template('signup.html', error="Gmail already registered")

        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO Users (Name, Gmail, PasswordHash) VALUES (?, ?, ?)", (name, gmail, hashed_pw))
        conn.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn, cursor = get_connection()
    cursor.execute("SELECT UserID FROM Users WHERE Gmail=?", (session['username'],))

    user_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT StudyHoursPerDay, AttendancePercent, PreviousScore, PredictedFinalScore, CreatedAt
        FROM Predictions
        WHERE UserID=?
        ORDER BY CreatedAt
    """, (user_id,))
    rows = cursor.fetchall()

    study_hours = [r[0] for r in rows]
    attendance = [r[1] for r in rows]
    prev_scores = [r[2] for r in rows]
    predicted_scores = [r[3] for r in rows]

    def avg(lst):
        return round(sum(lst) / len(lst), 2) if lst else None

    return render_template('dashboard.html',
        username=session['username'],
        predictions=[dict(zip(['StudyHoursPerDay','AttendancePercent','PreviousScore','PredictedFinalScore','CreatedAt'], row)) for row in rows],
        avg_study_hours=avg(study_hours),
        avg_attendance=avg(attendance),
        avg_prev_score=avg(prev_scores),
        avg_score=avg(predicted_scores),
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn, cursor = get_connection()

    # Get user ID
    cursor.execute("SELECT UserID FROM Users WHERE Gmail=?", (session['username'],))
    user = cursor.fetchone()
    if not user:
        return "User not found", 404
    user_id = user[0]

    # Import model
    import joblib
    import pandas as pd
    import os
    model = joblib.load(os.path.join('model.pkl'))

    success_message = None
    error_message = None

    try:
        # 📁 If CSV file uploaded
        if request.files.get('csv_file'):
            file = request.files['csv_file']
            df = pd.read_csv(file)

            required_cols = {'study_hours', 'attendance', 'prev_score'}
            if not required_cols.issubset(df.columns):
                return render_template('upload.html', error="CSV must contain columns: study_hours, attendance, prev_score")

            for _, row in df.iterrows():
                input_vals = [[row['study_hours'], row['attendance'], row['prev_score']]]
                prediction = round(model.predict(input_vals)[0], 2)
                cursor.execute("""
                    INSERT INTO Predictions (UserID, StudyHoursPerDay, AttendancePercent, PreviousScore, PredictedFinalScore)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    int(user_id),
                    float(row['study_hours']),
                    float(row['attendance']),
                    float(row['prev_score']),
                    float(prediction)
                ))


            conn.commit()
            success_message = f"✅ {len(df)} records uploaded and predicted successfully!"

        # ✍️ Manual form submission
        elif request.form.get('study_hours'):
            study_hours = float(request.form['study_hours'])
            attendance = float(request.form['attendance'])
            previous_score = float(request.form['previous_score'])

            predicted_score = round(model.predict([[study_hours, attendance, previous_score]])[0], 2)
            cursor.execute("""
                INSERT INTO Predictions (UserID, StudyHoursPerDay, AttendancePercent, PreviousScore, PredictedFinalScore)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, study_hours, attendance, previous_score, predicted_score))
            conn.commit()
            success_message = "✅ Data uploaded successfully!"

            # 🧠 Add Smart Suggestion Generator
            if predicted_score < 50:
                suggestion = "Focus on improving attendance and increase your study hours by 2 hrs/day."
            elif predicted_score < 65:
                suggestion = "You're on track! Try maintaining attendance above 85% and add 1 hour of study daily."
            elif predicted_score < 80:
                suggestion = "Great! Keep up consistent study habits and attendance."
            else:
                suggestion = "Excellent! Maintain your current efforts to stay ahead."

            # Save suggestion in session
            session['suggestion'] = suggestion
            session['predicted_score'] = predicted_score

    except Exception as e:
        error_message = str(e)

    # Show last 5 uploads
    cursor.execute("""
        SELECT TOP 5 StudyHoursPerDay, AttendancePercent, PreviousScore, PredictedFinalScore, CreatedAt
        FROM Predictions
        WHERE UserID=?
        ORDER BY CreatedAt DESC
    """, (user_id,))
    last_uploads = cursor.fetchall()

    return render_template(
        'upload.html',
        success=success_message,
        error=error_message,
        last_uploads=last_uploads
    )



@app.route('/export')
def export_pdf():
    conn, cursor = get_connection()
    cursor.execute("""
        SELECT StudyHoursPerDay, AttendancePercent, PreviousScore, PredictedFinalScore, CreatedAt 
        FROM Predictions 
        WHERE UserID = (SELECT UserID FROM Users WHERE Gmail = ?) 
        ORDER BY CreatedAt DESC
    """, (session['username'],))
    predictions = cursor.fetchall()

    html = render_template('export.html', predictions=predictions)

    # Convert HTML to PDF
    result = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=result)

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=student_report.pdf'

    return response


@app.route('/logout')
def logout():
    session.clear()  # clears all session data
    return redirect(url_for('login'))

@app.route('/analytics')
def analytics():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn, cursor = get_connection()
    cursor.execute("SELECT UserID FROM Users WHERE Gmail=?", (session['username'],))
    user = cursor.fetchone()
    if not user:
        return "User not found", 404

    user_id = user[0]
    cursor.execute("""
        SELECT CreatedAt, PredictedFinalScore
        FROM Predictions
        WHERE UserID=?
        ORDER BY CreatedAt
    """, (user_id,))
    data = cursor.fetchall()

    dates = [row.CreatedAt.strftime('%d-%b') for row in data]
    scores = [row.PredictedFinalScore for row in data]

    passed = sum(1 for s in scores if s >= 60)
    failed = len(scores) - passed

    avg_confidence = round(min(100, max(40, sum(scores) / len(scores))) if scores else 0, 2)

    return render_template("analytics.html", dates=dates, scores=scores,
                           passed=passed, failed=failed, confidence=avg_confidence)


if __name__ == '__main__':
    app.run(debug=True)

