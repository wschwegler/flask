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

# Home route that renders the upload form
@app.route('/')
def upload_form():
    return render_template('upload.html')

# Route to handle file uploads and process the data
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return 'No files part'

    files = request.files.getlist('files[]')  # Retrieve the list of uploaded files
    
    if len(files) != 4:
        return 'You must upload exactly 4 files.'

    # Save uploaded files to the `uploads` folder
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            saved_files.append(filepath)
        else:
            return f"Invalid file format for {file.filename}."

    # Load the files into DataFrames
    try:
        df1 = pd.read_csv(saved_files[0])
        df2 = pd.read_csv(saved_files[1])
        #df3 = pd.read_csv(saved_files[2])
        #df4 = pd.read_csv(saved_files[3])
    except Exception as e:
        return f"Error reading CSV files: {str(e)}"

    # Process the first two DataFrames
    '''
    columns_to_keep2 = ['fiscal year', 'name of school district', 'secured_net taxable value', 'unsecured_net taxable value']
    df1.columns = df1.columns.str.lower()
    df2.columns = df2.columns.str.lower()
    print("test")
    df2 = df2.rename(columns={
        'school district name': 'name of school district',
        'secured - net taxable value_school districts property taxes': 'secured_net taxable value',
        'unsecured - net taxable value_school districts property taxes': 'unsecured_net taxable value'
    })

    df1 = df1.filter(columns_to_keep2)
    df2 = df2.filter(columns_to_keep2)

    df1['fiscal year'] = df1['fiscal year'].astype(str)
    df2['fiscal year'] = df2['fiscal year'].astype(str)

    merged_df1 = pd.concat([df1, df2], ignore_index=True).drop_duplicates(subset=['fiscal year', 'name of school district'])
    
    print("part 2")
    # Process the third and fourth DataFrames
    columns_to_keep = ['leaid', 'year', 'lea_name', 'phone', 'urban_centric_locale', 'number_of_schools', 'enrollment',
                       'teachers_total_fte', 'race', 'rev_total', 'rev_fed_total', 'rev_state_total', 'rev_local_total',
                       'exp_total', 'exp_current_instruction_total', 'outlay_capital_total', 'payments_charter_schools',
                       'salaries_instruction', 'benefits_employee_total', 'debt_interest', 
                       'debt_longterm_outstand_end_fy', 'debt_shortterm_outstand_end_fy', 'est_population_5_17_poverty_pct']
    
    df3 = df3[df3['year'] >= 2008]
    df3 = df3[df3['state_mailing'].str.contains('CA', na=False)]
    df3.columns = df3.columns.str.lower()
    df3 = df3.filter(columns_to_keep)
    df3['leaid'] = df3['leaid'].astype(str)
    print("year df3")

    df4 = df4[df4['year'] >= 2008]
    df4.columns = df4.columns.str.lower()
    df4 = df4.filter(columns_to_keep)
    df4['leaid'] = df4['leaid'].astype(str)
    print("year df4")

    counter = 0 
    # Merge df3 and df4 based on best matches
    merged_df2 = pd.DataFrame(columns=df3.columns.tolist() + df4.columns.tolist())
    for _, row in df3.iterrows():
        target = row['leaid']
        target_year = row['year']
        candidates = df4[df4['year'] == target_year]
        best_match = None
        best_ratio = 0
        for _, candidate in candidates.iterrows():
            ratio = difflib.SequenceMatcher(None, target, candidate['leaid']).ratio()
            if ratio > best_ratio and ratio >= 0.92:
                counter += 1
                print(counter)
                best_ratio = ratio
                best_match = candidate
        if best_match is not None:
            new_row = pd.concat([row, best_match]).to_frame().T
            merged_df2 = pd.concat([merged_df2, new_row], ignore_index=True)

    # Save the final merged DataFrame
    merged_file_path = os.path.join(app.config['MERGED_FOLDER'], 'merged.csv')
    merged_df2.to_csv(merged_file_path, index=False)
    #------------------------------------------------------------------
    '''
    print("merge")
    df7 = df1
    df8 = df2
    '''
    df7['secured_net taxable value'] = None
    df7['unsecured_net taxable value'] = None
    columns = df7.columns.tolist() + df8.columns.tolist()
    merged_df_final = pd.DataFrame(columns=columns)
    ignore_words = ["unified"]
    counter2 = 0
    for i in range(0, len(df7)):
        target = df7.iloc[i]['lea_name'].lower()
        target = target.lower()
        target_y = df7.iloc[i]['year']
        for word in ignore_words:
            target = target.replace(word, "").strip()
        new_df = df8[df8['fiscal year'] == int(target_y)]

        best_match = None
        best_ratio = 0

        for k in range(0, len(new_df)):
            df8_name = new_df.iloc[k]['name of school district'].lower()
            for word in ignore_words:
                df8_name = df8_name.replace(word, "").strip()
            diff = difflib.SequenceMatcher(None, target, df8_name)
            ratio = diff.ratio()
            if (ratio >= 0.92):
                counter2 += 1
                print(counter2)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = new_df.iloc[k].copy()
        if best_match is not None:
            new_row = pd.concat([df7.iloc[[i]].reset_index(drop=True),
                                best_match.to_frame().T.reset_index(drop=True)], axis=1)
            merged_df_final = pd.concat([merged_df_final, new_row], ignore_index=True)


    #Final merged file
    '''
    merged_df_final = df7
    merged_file_path = os.path.join(app.config['MERGED_FOLDER'], 'merged.csv')
    merged_df_final.to_csv(merged_file_path, index=False)
    

    

    # Render the success message with download link
    return render_template('result.html', 
                           message="Files have been successfully merged.",
                           download_link='/download/merged.csv')

# Route to serve the merged file
@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['MERGED_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
