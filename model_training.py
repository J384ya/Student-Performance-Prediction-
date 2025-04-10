# model_training.py
import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Sample Data
df = pd.DataFrame({
    "study_hours": [1, 2, 3, 4, 5],
    "attendance": [60, 70, 80, 90, 100],
    "prev_score": [50, 60, 70, 80, 90],
    "final_score": [55, 65, 75, 85, 95]
})

X = df[["study_hours", "attendance", "prev_score"]]
y = df["final_score"]

# Train the model
model = LinearRegression()
model.fit(X, y)

# Save the model cleanly
joblib.dump(model, "model.pkl")
print("✅ Model saved successfully!")
