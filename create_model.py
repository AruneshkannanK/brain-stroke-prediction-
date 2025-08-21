import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Create a simple mock model for demonstration
# In a real scenario, this would be trained on actual stroke data
np.random.seed(42)

# Generate some mock training data
n_samples = 1000
n_features = 15

# Feature names as used in the app
feature_names = ['age', 'avg_glucose_level', 'bmi', 'gender_Male',
                 'hypertension_1', 'heart_disease_1', 'ever_married_Yes',
                 'work_type_Never_worked', 'work_type_Private',
                 'work_type_Self_employed', 'work_type_children',
                 'Residence_type_Urban', 'smoking_status_formerly_smoked',
                 'smoking_status_never_smoked', 'smoking_status_smokes']

# Generate mock data
X = np.random.rand(n_samples, n_features)
# Age should be realistic (20-90)
X[:, 0] = np.random.randint(20, 91, n_samples)
# Glucose level (70-300)
X[:, 1] = np.random.uniform(70, 300, n_samples)
# BMI (15-50)
X[:, 2] = np.random.uniform(15, 50, n_samples)
# Binary features (0 or 1)
for i in range(3, n_features):
    X[:, i] = np.random.randint(0, 2, n_samples)

# Generate target variable (stroke risk)
# Higher age, glucose, BMI increase stroke risk
y = ((X[:, 0] > 60) | (X[:, 1] > 200) | (X[:, 2] > 30) | 
     (X[:, 4] == 1) | (X[:, 5] == 1)).astype(int)

# Add some randomness
y = np.where(np.random.rand(n_samples) < 0.1, 1 - y, y)

# Train a simple model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the model
with open('model.pickle', 'wb') as f:
    pickle.dump(model, f)

print("Mock model created and saved as model.pickle")