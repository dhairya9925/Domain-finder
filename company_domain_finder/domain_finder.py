from flask import Flask, request, jsonify, render_template
import requests
from difflib import get_close_matches

app = Flask(__name__)

CLEARBIT_URL = "https://autocomplete.clearbit.com/v1/companies/suggest?query="

COMMON_TLDS = [
    ".com", ".org", ".net", ".info", ".biz", ".co", ".io", ".me",
    ".app", ".tech", ".dev", ".xyz", ".online", ".site", ".store", ".agency",
    ".in", ".us"
]

def get_domain_clearbit(company_name):
    try:
        res = requests.get(f"{CLEARBIT_URL}{company_name}")
        data = res.json()
        if data:
            names = [d['name'] for d in data]
            closest = get_close_matches(company_name, names, n=1)
            if closest:
                for d in data:
                    if d['name'] == closest[0]:
                        return d['domain']
        return None
    except:
        return None

def try_common_domains(company_name):
    name_clean = company_name.lower().replace(" ", "")
    for ext in COMMON_TLDS:
        domain = f"{name_clean}{ext}"
        try:
            res = requests.get(f"https://{domain}", timeout=2)
            if res.ok:
                return domain
        except:
            continue
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_domain", methods=["POST"])
def get_domain():
    company = request.form.get("company")
    if not company:
        return jsonify({"error": "Company name is required."}), 400

    domain = get_domain_clearbit(company)
    if not domain:
        domain = try_common_domains(company)

    return jsonify({"company": company, "domain": domain or "Not found"})

if __name__ == '__main__':
    app.run(debug=True)
