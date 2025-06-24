import subprocess
subprocess.run("pip install -r requirements.txt")


from flask import Flask, request, render_template, send_file
import os
import pandas as pd
from clearbit_utils import get_domain_from_clearbit
from fallback_search import fallback_domain_guess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app = Flask(__name__)
RESULT_EXCEL_FILE = os.path.join(RESULT_FOLDER, 'results.xlsx')

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    table_data = None
    if request.method == 'POST':
        if 'company_name' in request.form:
            company = request.form['company_name']
            industry = request.form.get('industry')
            domain = get_domain_from_clearbit(company) or fallback_domain_guess(company, industry=industry)
            result = { 'company': company, 'domain': domain or 'Not Found' }

        elif 'excel_file' in request.files:
            file = request.files['excel_file']
            industry = request.form.get('industry')  # Get industry input for bulk mode

            if file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
                results = []

                for name in df.iloc[:, 0]:
                    domain = get_domain_from_clearbit(name) or fallback_domain_guess(name, industry = industry)
                    results.append({'Company': name, 'Domain': domain or 'Not Found'})

                result_df = pd.DataFrame(results)
                result_df.to_excel(RESULT_EXCEL_FILE, index=False)
                table_data = result_df.to_dict(orient='records')


    return render_template('index.html', result=result, table_data=table_data)

@app.route('/download')
def download_excel():
    return send_file(RESULT_EXCEL_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
