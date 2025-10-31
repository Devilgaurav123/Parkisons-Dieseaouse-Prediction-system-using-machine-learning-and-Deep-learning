# ===============================
# Parkinson's Image CNN Model (Fixed)
# Works with dataset/healthy and dataset/parkinson
# ===============================

import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
import shutil

# Directories
base_dir = 'dataset'
train_dir = 'dataset_split/train'
test_dir = 'dataset_split/test'

# Create split directories if not exist
if not os.path.exists('dataset_split'):
    os.makedirs(train_dir)
    os.makedirs(test_dir)

    for label in ['healthy', 'parkinson']:
        os.makedirs(os.path.join(train_dir, label))
        os.makedirs(os.path.join(test_dir, label))

        # Split files 80/20 automatically
        full_path = os.path.join(base_dir, label)
        images = os.listdir(full_path)
        train_imgs, test_imgs = train_test_split(images, test_size=0.2, random_state=42)

        for img in train_imgs:
            shutil.copy(os.path.join(full_path, img), os.path.join(train_dir, label, img))
        for img in test_imgs:
            shutil.copy(os.path.join(full_path, img), os.path.join(test_dir, label, img))

    print("✅ Dataset split into train/test successfully!")

# Parameters
img_size = (224, 224)
batch_size = 32

# Data Augmentation
train_datagen = ImageDataGenerator(
    rescale=1.0/255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)
test_datagen = ImageDataGenerator(rescale=1.0/255)

train_gen = train_datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary'
)

test_gen = test_datagen.flow_from_directory(
    test_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode='binary'
)

# Build Model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(224,224,3)),
    BatchNormalization(),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2,2),

    Conv2D(128, (3,3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Early stopping
callback = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train
model.fit(train_gen, validation_data=test_gen, epochs=10, callbacks=[callback])

# Save model
model.save('image_model.h5')
print("✅ Saved image_model.h5 successfully.")
