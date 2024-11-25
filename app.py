from flask import Flask, request, render_template, send_file, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
MERGED_FOLDER = 'merged_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MERGED_FOLDER'] = MERGED_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Check if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Ensure necessary folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return 'No files part'

    files = request.files.getlist('files[]')
    
    if len(files) != 2:
        return 'You must upload exactly 2 files.'

    # Save uploaded files to the `uploads` folder
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            saved_files.append(filepath)
        else:
            return f"Invalid file format for {file.filename}."

    try:
        # Load files into DataFrames
        df1 = pd.read_csv(saved_files[0])
        df2 = pd.read_csv(saved_files[1])
    except Exception as e:
        return f"Error reading CSV files: {str(e)}"

    # Redirect to the download page with the first uploaded file (df1)
    return redirect(url_for('download_file', filename=files[0].filename))

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found.", 404

if __name__ == '__main__':
    app.run()
