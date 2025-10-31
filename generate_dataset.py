# generate_dataset.py
import pandas as pd
import numpy as np

# Create 100 fake samples that look like the UCI Parkinson’s dataset
np.random.seed(42)

data = {
    "MDVP:Fo(Hz)": np.random.uniform(90, 200, 100),   # Average vocal fundamental frequency
    "MDVP:Fhi(Hz)": np.random.uniform(100, 250, 100), # Max fundamental frequency
    "MDVP:Flo(Hz)": np.random.uniform(60, 100, 100),  # Min fundamental frequency
    "MDVP:Jitter(%)": np.random.uniform(0.001, 0.02, 100),  # Frequency variation
    "MDVP:Shimmer": np.random.uniform(0.01, 0.1, 100),      # Amplitude variation
    "NHR": np.random.uniform(0.001, 0.1, 100),              # Noise-to-harmonics ratio
    "HNR": np.random.uniform(15, 35, 100),                  # Harmonics-to-noise ratio
    "RPDE": np.random.uniform(0.3, 0.7, 100),
    "DFA": np.random.uniform(0.5, 0.9, 100),
    "spread1": np.random.uniform(-7, -4, 100),
    "spread2": np.random.uniform(0.01, 0.05, 100),
    "D2": np.random.uniform(1.5, 3, 100),
    "PPE": np.random.uniform(0.1, 0.6, 100),
    "status": np.random.randint(0, 2, 100)  # 1 = Parkinson's, 0 = Healthy
}

df = pd.DataFrame(data)

df.to_csv("parkinsons.csv", index=False)

print("✅ Sample dataset 'parkinsons.csv' created successfully!")
print(df.head())
