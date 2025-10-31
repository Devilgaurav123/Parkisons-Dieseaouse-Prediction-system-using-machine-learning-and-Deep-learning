import os
import numpy as np
from PIL import Image

# Create directories for two classes
os.makedirs("dataset/healthy", exist_ok=True)
os.makedirs("dataset/parkinson", exist_ok=True)

# Generate 100 synthetic grayscale images (50 per class)
for i in range(50):
    healthy_image = np.random.randint(150, 255, (64, 64), dtype=np.uint8)
    parkinson_image = np.random.randint(0, 120, (64, 64), dtype=np.uint8)
    
    Image.fromarray(healthy_image).save(f"dataset/healthy/healthy_{i}.png")
    Image.fromarray(parkinson_image).save(f"dataset/parkinson/parkinson_{i}.png")

print("✅ Synthetic image dataset created successfully!")
print("📁 dataset/healthy and dataset/parkinson contain the images.")
