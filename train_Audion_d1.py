# ===============================
# Parkinson's Voice Deep Learning Model (CNN on MFCC)
# Output: parkinsons_audio_dl.h5
# ===============================

import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.utils import to_categorical

# 1️⃣ Dataset directory structure:
# dataset_voice/
# ├── parkinsons/
# │   ├── file1.wav
# │   └── ...
# └── healthy/
#     ├── file1.wav
#     └── ...
DATASET_DIR = 'dataset_voice'

def extract_mfcc(file_path, n_mfcc=40, max_len=173):
    try:
        y, sr = librosa.load(file_path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        if mfcc.shape[1] < max_len:
            pad_width = max_len - mfcc.shape[1]
            mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
        else:
            mfcc = mfcc[:, :max_len]
        return mfcc
    except:
        return None

X, y = [], []
for label, folder in enumerate(['healthy', 'parkinsons']):
    path = os.path.join(DATASET_DIR, folder)
    for file in os.listdir(path):
        if file.endswith('.wav'):
            fpath = os.path.join(path, file)
            mfcc = extract_mfcc(fpath)
            if mfcc is not None:
                X.append(mfcc)
                y.append(label)

X = np.array(X)
y = np.array(y)
X = X[..., np.newaxis]  # Add channel dimension

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 2️⃣ Build CNN model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=X_train.shape[1:]),
    MaxPooling2D((2,2)),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D((2,2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(1, activation='sigmoid')
])

# 3️⃣ Compile
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 4️⃣ Train
model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

# 5️⃣ Save model
model.save('parkinsons_audio_dl.h5')
print("✅ Saved deep learning model: parkinsons_audio_dl.h5")
