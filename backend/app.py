from flask import Flask, request, jsonify
import torch
from ultralytics import YOLO
from flask_cors import CORS
import cv2
import numpy as np

app = Flask(__name__)
CORS(app)

# Load the YOLO model - ensure 'best.pt' is in the correct directory
model = YOLO('best.pt')

# Function to calculate class counts
def get_class_counts(results):
    counts = {'WBC': 0, 'RBC': 0, 'Platelets': 0}
    for result in results:
        if result.boxes is not None:  # Ensure there are detected boxes
            for box in result.boxes:
                class_id = int(box.cls.item())  # Convert Tensor to int
                class_name = ['WBC', 'RBC', 'Platelets'][class_id]
                counts[class_name] += 1
    return counts

# Function to get the cell size distribution
def get_cell_size_distribution(results):
    sizes = {'WBC': [], 'RBC': [], 'Platelets': []}
    for result in results:
        if result.boxes is not None:  # Ensure there are detected boxes
            for box in result.boxes:
                class_id = int(box.cls.item())  # Convert Tensor to int
                class_name = ['WBC', 'RBC', 'Platelets'][class_id]

                # Assuming boxes are in xyxy format: [x1, y1, x2, y2]
                box_data = box.xyxy[0].cpu().numpy()  # Convert Tensor to NumPy array
                width = box_data[2] - box_data[0]
                height = box_data[3] - box_data[1]
                area = width * height
                sizes[class_name].append(float(area))  # Convert to float for JSON serialization

    return sizes

# Function to detect diseases based on counts
def detect_diseases(wbc_count, rbc_count, platelet_count):
    conditions = []
    if wbc_count > 11:  # Adjusted for small sample size
        conditions.append("Potential Leukemia: High WBC count")
    elif wbc_count < 4:
        conditions.append("Low WBC: Potential immune system issues")

    if rbc_count < 4700:
        conditions.append("Potential Anemia: Low RBC count")

    if platelet_count < 150:
        conditions.append("Potential Thrombocytopenia: Low platelet count")

    return conditions if conditions else ["No abnormalities detected"]

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    # Load the image from the request
    image_np = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    # Run inference on the image with confidence threshold
    results = model(img, conf=0.25)

    # Get class counts and size distributions
    class_counts = get_class_counts(results)
    cell_sizes = get_cell_size_distribution(results)

    # Detect diseases based on the counts
    detected_conditions = detect_diseases(class_counts['WBC'], class_counts['RBC'], class_counts['Platelets'])

    return jsonify({
        'WBC': class_counts['WBC'],
        'RBC': class_counts['RBC'],
        'Platelets': class_counts['Platelets'],
        'sizeDistributions': cell_sizes,
        'detectedConditions': detected_conditions
    })

if __name__ == '__main__':
    app.run(debug=True)
