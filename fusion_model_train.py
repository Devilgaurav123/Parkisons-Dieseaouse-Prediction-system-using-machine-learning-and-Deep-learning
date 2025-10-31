"""
fusion_model_train.py
----------------------
Train a multimodal deep learning system for Parkinson's Detection.
Combines audio-based features and CNN-based MRI features.
"""

import os
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.layers import (
    Dense, Dropout, Input, concatenate
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------------------------------
# 1️⃣ LOAD DATA (replace these with your real extracted features)
# -------------------------------------------------------------------------
# Example: each sample = one patient
# voice_features.npy → shape (N, 40)
# mri_features.npy → shape (N, 1024)
# labels.npy → shape (N, )

audio_feat_path = os.path.join(BASE_DIR, "voice_features.npy")
image_feat_path = os.path.join(BASE_DIR, "mri_features.npy")
label_path = os.path.join(BASE_DIR, "labels.npy")

if not (os.path.exists(audio_feat_path) and os.path.exists(image_feat_path) and os.path.exists(label_path)):
    raise FileNotFoundError("Please generate voice_features.npy, mri_features.npy, and labels.npy before training.")

X_audio = np.load(audio_feat_path)
X_image = np.load(image_feat_path)
y = np.load(label_path)

print("Loaded datasets:")
print(f"Audio features: {X_audio.shape}")
print(f"Image features: {X_image.shape}")
print(f"Labels: {y.shape}")

# -------------------------------------------------------------------------
# 2️⃣ TRAIN AUDIO MODEL (RandomForest)
# -------------------------------------------------------------------------
print("\nTraining audio model...")

scaler = StandardScaler()
X_audio_scaled = scaler.fit_transform(X_audio)

audio_model = RandomForestClassifier(n_estimators=200, random_state=42)
audio_model.fit(X_audio_scaled, y)

joblib.dump(audio_model, os.path.join(BASE_DIR, "parkinsons_model.pkl"))
joblib.dump(scaler, os.path.join(BASE_DIR, "scaler.pkl"))

print("✅ Saved: parkinsons_model.pkl & scaler.pkl")

# -------------------------------------------------------------------------
# 3️⃣ TRAIN IMAGE MODEL (CNN)
# -------------------------------------------------------------------------
print("\nTraining MRI CNN model...")

# Suppose you have images stored in dataset/healthy and dataset/parkinson
dataset_dir = os.path.join(BASE_DIR, "dataset")
train_datagen = ImageDataGenerator(rescale=1.0 / 255.0, validation_split=0.2)

train_gen = train_datagen.flow_from_directory(
    dataset_dir,
    target_size=(224, 224),
    batch_size=8,
    class_mode="binary",
    subset="training"
)
val_gen = train_datagen.flow_from_directory(
    dataset_dir,
    target_size=(224, 224),
    batch_size=8,
    class_mode="binary",
    subset="validation"
)

base_model = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
x = GlobalAveragePooling2D()(base_model.output)
x = Dense(128, activation="relu")(x)
x = Dropout(0.3)(x)
out = Dense(1, activation="sigmoid")(x)
image_model = Model(inputs=base_model.input, outputs=out)

for layer in base_model.layers[:100]:
    layer.trainable = False

image_model.compile(optimizer=Adam(1e-4), loss="binary_crossentropy", metrics=["accuracy"])

callbacks = [
    EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
    ModelCheckpoint(os.path.join(BASE_DIR, "image_model.h5"), save_best_only=True)
]

image_model.fit(train_gen, validation_data=val_gen, epochs=10, callbacks=callbacks)
print("✅ Saved: image_model.h5")

# -------------------------------------------------------------------------
# 4️⃣ TRAIN FUSION MODEL (Deep Neural Net)
# -------------------------------------------------------------------------
print("\nTraining fusion model...")

# Create embeddings (simulated)
# You can later replace with actual outputs from both models
audio_emb_size = X_audio.shape[1]
image_emb_size = X_image.shape[1]

X_audio_train, X_audio_val, X_image_train, X_image_val, y_train, y_val = train_test_split(
    X_audio_scaled, X_image, y, test_size=0.2, random_state=42
)

input_audio = Input(shape=(audio_emb_size,))
input_image = Input(shape=(image_emb_size,))

a = Dense(64, activation="relu")(input_audio)
i = Dense(64, activation="relu")(input_image)

merged = concatenate([a, i])
x = Dense(128, activation="relu")(merged)
x = Dropout(0.3)(x)
x = Dense(64, activation="relu")(x)
out = Dense(1, activation="sigmoid")(x)

fusion_model = Model(inputs=[input_audio, input_image], outputs=out)
fusion_model.compile(optimizer=Adam(1e-4), loss="binary_crossentropy", metrics=["accuracy"])

callbacks = [
    EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
    ModelCheckpoint(os.path.join(BASE_DIR, "fusion_model.h5"), save_best_only=True)
]

fusion_model.fit(
    [X_audio_train, X_image_train],
    y_train,
    validation_data=([X_audio_val, X_image_val], y_val),
    epochs=15,
    batch_size=16,
    callbacks=callbacks,
)

print("✅ Saved: fusion_model.h5")
print("\n✅ All models trained and saved successfully!")
