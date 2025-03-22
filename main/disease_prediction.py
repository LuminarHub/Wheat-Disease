import tensorflow as tf
import numpy as np
from PIL import Image
import os
from keras.preprocessing import image

model_path = tf.keras.models.load_model(".\crop\main\Wheat.keras", compile=False, safe_mode=False)

# Define class labels
class_labels = ['Wheat Brown Rust', 'Wheat Healthy', 'Wheat Yellow Rust']


# Function to preprocess the image for prediction
def preprocess_image(image_path):
    img = Image.open(image_path)
    img = img.resize((224, 224))  # Resize to the model's expected input size
    img_array = np.array(img) / 255.0  # Normalize the image
    return np.expand_dims(img_array, axis=0)

# def load_and_prep_image(image_file, img_shape=224):
#     img = Image.open(image_file)
#     img = img.resize((img_shape, img_shape))
#     img_array = np.array(img)
#     img_array = img_array / 255.0  # Normalizing
#     return np.expand_dims(img_array, axis=0)

# Prediction function
def predicted_class(class_labels, model_path, img_array):
    prediction = model_path.predict(img_array)
    predicted_class = class_labels[np.argmax(prediction)]
    return predicted_class

# # Fetch treatment recommendations (you can replace this with your actual function for fetching data)
# def get_groq_response(query):
#     # For now, return a dummy treatment response.
#     # In your case, you'd implement logic to get the actual treatment from an API or a database.
#     treatments = {
#         'Brown_rust': 'Use fungicide, remove infected plants, crop rotation.',
#         'Healthy': 'No treatment needed.',
#         'Yellow_rust': 'Apply fungicide, remove infected plants, monitor crops regularly.'
#     }
#     return treatments.get(query, 'No recommendations available')y