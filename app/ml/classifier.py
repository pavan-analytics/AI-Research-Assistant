import pickle
import tensorflow as tf


class DocumentClassifier:

    def __init__(self):

        self.model = tf.keras.models.load_model(
            "app/ml/classifier.keras"
        )

        with open("app/ml/label_encoder.pkl", "rb") as f:
            self.label_encoder = pickle.load(f)

    def predict_category(self, text):

        text = text[:1000]

        input_text = tf.constant([text], dtype=tf.string)

        prediction = self.model.predict(
            input_text,
            verbose=0
        )

        predicted_class = prediction.argmax(axis=1)[0]

        category = self.label_encoder.inverse_transform(
            [predicted_class]
        )[0]

        return category