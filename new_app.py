from flask import Flask, request, jsonify, render_template
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

# Define constants
RESULTS_PER_PAGE = 10

@app.route('/')
def index():
    return render_template('index.html')

def fetch_summaries(pubmed_ids):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
    id_string = ','.join(pubmed_ids)
    url = f'{base_url}?db=pubmed&id={id_string}&retmode=json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def parse_summary_data(summary_data):
    article_details = []
    for item in summary_data['result']:
        pubmed_id = list(item.keys())[0]  # Get the PubMed ID
        article_data = item[pubmed_id]

        article_title = article_data['title']
        article_url = f'https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/'

        authors = article_data['authors']
        author_names = [author['name'] for author in authors]

        abstract_elements = article_data.get('AbstractText', [])
        abstract = '\n'.join(abstract_element.text.strip() for abstract_element in abstract_elements) if abstract_elements else 'Abstract Not Found'

        article_details.append({
            'pubmed_id': pubmed_id,
            'title': article_title,
            'url': article_url,
            'authors': author_names,
            'abstract': abstract
        })
    return article_details

@app.route('/search', methods=['POST', 'GET'])
def search_papers():
    search_term = request.form.get('term')
    page = int(request.form.get('page', 1))

    if not search_term:
        return jsonify({'error': 'Search term is required'}), 400

    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    url = f'{base_url}?db=pubmed&term={search_term}&retmode=json&retstart={(page - 1) * RESULTS_PER_PAGE}&retmax={RESULTS_PER_PAGE}'

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        pubmed_ids = data['esearchresult']['idlist']
        total_results = int(data['esearchresult']['count'])
        total_pages = (total_results // RESULTS_PER_PAGE) + 1

        if not pubmed_ids:
            return render_template('results.html', article_details=[], page=page, total_pages=total_pages)

        summary_data = fetch_summaries(pubmed_ids)
        article_details = parse_summary_data(summary_data)

        return render_template('results.html', article_details=article_details, page=page, total_pages=total_pages)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/abstract/<pubmed_id>')
def abstract(pubmed_id):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
    url = f'{base_url}?db=pubmed&id={pubmed_id}&retmode=xml'

    try:
        response = requests.get(url)
        response.raise_for_status()

        xml_data = response.text
        root = ET.fromstring(xml_data)

        abstract_elements = root.findall('.//AbstractText')
        if abstract_elements:
            abstract = '\n'.join(abstract_element.text.strip() for abstract_element in abstract_elements)
            return jsonify({'abstract': abstract})
        else:
            return jsonify({'abstract': 'Abstract Not Found'})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except ET.ParseError as e:
        return jsonify({'error': 'Error parsing XML response'}), 500

@app.route('/keywords/<pubmed_id>')
def keywords(pubmed_id):
    base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
    url = f'{base_url}?db=pubmed&id={pubmed_id}&retmode=json'

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        article_keywords = data['result'][pubmed_id].get('KeyList', [])

        if article_keywords:
            return jsonify({'keywords': [keyword['term'] for keyword in article_keywords]})
        else:
            return jsonify({'keywords': 'Keywords Not Found'})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)