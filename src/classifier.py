from transformers import pipeline
from PIL import Image
import glob

classifier = pipeline(
    "image-classification",
    model="chriamue/bird-species-classifier"
)
directory_path = 'data/*.jpg'
for image in glob.glob(directory_path):
    with Image.open(image) as img:
        print(classifier(img))
