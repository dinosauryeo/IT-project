from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import pandas as pd

app = Flask(__name__)

# Set upload folder path
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to serve the HTML file
@app.route('/')
def index():
    return render_template('home.html')

# Route to handle the file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Save the file to the server
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Read the file into a dataframe and convert to JSON
        if file.filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        else:
            return jsonify({'error': 'Invalid file format'}), 400

        data = df.to_dict(orient='records')
        return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
