# Importing the libraries needed
import torch
import urllib.request
from PIL import Image
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification

# Determining the file URL
url = 'some url'

# Opening the image using PIL
img = Image.open(urllib.request.urlretrieve(url)[0])

# Loading the model and preprocessor from HuggingFace
preprocessor = EfficientNetImageProcessor.from_pretrained("dennisjooo/Birds-Classifier-EfficientNetB2")
model = EfficientNetForImageClassification.from_pretrained("dennisjooo/Birds-Classifier-EfficientNetB2")

# Preprocessing the input
inputs = preprocessor(img, return_tensors="pt")

# Running the inference
with torch.no_grad():
    logits = model(**inputs).logits

# Getting the predicted label
predicted_label = logits.argmax(-1).item()
print(model.config.id2label[predicted_label])

