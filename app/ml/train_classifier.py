import pandas as pd
import pickle
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load dataset
data = pd.read_csv("app/ml/dataset.csv")

texts = data["text"].astype(str).tolist()
labels = data["category"].astype(str).tolist()

# Encode labels
label_encoder = LabelEncoder()
encoded_labels = label_encoder.fit_transform(labels)

# Save label encoder
with open("app/ml/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    texts,
    encoded_labels,
    test_size=0.2,
    random_state=42
)
X_train = tf.constant(X_train, dtype=tf.string)
X_test = tf.constant(X_test, dtype=tf.string)

y_train = tf.constant(y_train, dtype=tf.int32)
y_test = tf.constant(y_test, dtype=tf.int32)

# Text vectorization
vectorizer = tf.keras.layers.TextVectorization(
    max_tokens=5000,
    output_mode="int",
    output_sequence_length=100
)

vectorizer.adapt(X_train)

# Build model
model = tf.keras.Sequential([
    vectorizer,
    tf.keras.layers.Embedding(5000, 32),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(len(label_encoder.classes_), activation="softmax")
])

# Compile
model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

# Train
model.fit(
    X_train,
    y_train,
    epochs=20,
    validation_data=(X_test, y_test)
)

# Save model
model.save("app/ml/classifier.keras")

print("Training completed successfully.")