import requests

def get_domain_from_clearbit(company, industry=None):
    try:
        response = requests.get(f'https://autocomplete.clearbit.com/v1/companies/suggest?query={company}')
        data = response.json()

        for item in data:
            if item['name'].lower() == company.lower():
                if industry and industry.lower() not in item.get('domain', ''):
                    continue
                return item['domain']
    except Exception as e:
        print(f"Clearbit error: {e}")
    return None
