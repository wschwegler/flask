from flask import Flask, request, render_template, send_file
import pandas as pd
import os
import difflib

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
        return 'You must upload exactly 2 files: school-districts_lea_directory and districts_ccd_finance.'

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
        lea_directory = pd.read_csv(saved_files[0])
        ccd_finance = pd.read_csv(saved_files[1])
    except Exception as e:
        return f"Error reading CSV files: {str(e)}"

    # Filter columns to reduce memory usage
    lea_columns = ['leaid', 'year', 'lea_name', 'phone', 'urban_centric_locale']
    finance_columns = ['leaid', 'year', 'rev_total', 'exp_total', 'teachers_total_fte', 'enrollment']

    lea_directory = lea_directory.filter(lea_columns).dropna()
    ccd_finance = ccd_finance.filter(finance_columns).dropna()

    # Ensure LEAID and Year are treated as strings
    lea_directory['leaid'] = lea_directory['leaid'].astype(str)
    ccd_finance['leaid'] = ccd_finance['leaid'].astype(str)
    lea_directory['year'] = lea_directory['year'].astype(str)
    ccd_finance['year'] = ccd_finance['year'].astype(str)

    # Best match merge based on 'leaid' and 'year'
    counter = 0
    merged_df2 = pd.DataFrame(columns=lea_columns + finance_columns)
    for _, row in lea_directory.iterrows():
        target_leaid = row['leaid']
        target_year = row['year']
        candidates = ccd_finance[ccd_finance['year'] == target_year]
        
        best_match = None
        best_ratio = 0
        for _, candidate in candidates.iterrows():
            ratio = difflib.SequenceMatcher(None, target_leaid, candidate['leaid']).ratio()
            if ratio > best_ratio and ratio >= 0.92:
                best_ratio = ratio
                best_match = candidate

        if best_match is not None:
            counter += 1
            print(counter)
            new_row = pd.concat([row, best_match]).to_frame().T
            merged_df2 = pd.concat([merged_df2, new_row], ignore_index=True)

    # Save the merged DataFrame
    merged_file_path = os.path.join(app.config['MERGED_FOLDER'], 'merged.csv')
    merged_df2.to_csv(merged_file_path, index=False)

    return render_template('result.html', 
                           message="Files have been successfully merged.",
                           download_link='/download/merged.csv')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['MERGED_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found.", 404

if __name__ == '__main__':
    app.run()

