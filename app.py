from flask import Flask, request, render_template, redirect, url_for
import cv2
import pytesseract
from werkzeug.utils import secure_filename
import os

# Path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'static'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('display_result', filename=filename))
    return render_template('upload.html')

@app.route('/result/<filename>')
def display_result(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Load the image
    img = cv2.imread(file_path)

    if img is None:
        return f"Error: Image not loaded. Please check the file path: {file_path}"

    # Resize the image
    img = cv2.resize(img, (600, 800))

    # Convert the image to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Extract text from the image
    extracted_text = pytesseract.image_to_string(img)

    # Get image dimensions
    h_img = img.shape[0]
    w_img = img.shape[1]

    # Get bounding boxes of the detected text
    boxes = pytesseract.image_to_boxes(img)
    for b in boxes.splitlines():
        b = b.split(' ')
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(img, (x, h_img - y), (w, h_img - h), (0, 0, 255), 1)
        cv2.putText(img, b[0], (x, h_img - y + 20), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

    # Save the processed image with bounding boxes
    result_image_filename = 'result_' + filename
    result_image_path = os.path.join(app.config['PROCESSED_FOLDER'], result_image_filename)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(result_image_path, img)

    return render_template('result.html', extracted_text=extracted_text, result_image=result_image_filename)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8000)
   