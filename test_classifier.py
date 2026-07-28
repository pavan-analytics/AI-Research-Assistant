from importlib import reload
import app.ml.classifier as classifier_module

reload(classifier_module)

DocumentClassifier = classifier_module.DocumentClassifier

print("Starting...")

classifier = DocumentClassifier()

print("Model loaded!")

text = """
Python supports functions, loops, classes,
object oriented programming and exception handling.
"""

print("Predicting...")

result = classifier.predict_category(text)

print("Prediction:", result)