# ===============================
# Parkinson's Voice Model Training Script
# ===============================
# Output: parkinsons_model.pkl, scaler.pkl
# ===============================

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1️⃣ Load dataset (UCI Parkinson’s)
data = pd.read_csv('parkinsons.csv')

# Drop irrelevant columns
if 'name' in data.columns:
    X = data.drop(columns=['name', 'status'])
else:
    X = data.drop(columns=['status'])
y = data['status']

# 2️⃣ Split into train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3️⃣ Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 4️⃣ Train SVM model
model = SVC(kernel='rbf', probability=True, random_state=42)
model.fit(X_train_scaled, y_train)

# 5️⃣ Evaluate
y_pred = model.predict(X_test_scaled)
print("✅ Accuracy:", round(accuracy_score(y_test, y_pred) * 100, 2), "%")
print("Classification Report:\n", classification_report(y_test, y_pred))

# 6️⃣ Save model + scaler
joblib.dump(model, 'parkinsons_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("✅ Files saved: parkinsons_model.pkl, scaler.pkl")
