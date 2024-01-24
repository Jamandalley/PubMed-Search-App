# PubMed Article Finder and Summary App
This Flask-based application allows users to search for articles on PubMed and view their summaries. The app consists of the following routes:
1. Index page (`/`): Displays the search form for users to input their search terms.
2. Search results (`/search`): Shows a list of articles matching the user's search term. Users can navigate through multiple pages of results. Each result includes the article's title, authors, and a link to the abstract.
3. Abstract view (`/abstract/<pubmed_id>`): Displays the abstract of an article based on its PubMed ID.
4. Keywords view (`/keywords/<pubmed_id>`): Shows the keywords associated with an article based on its PubMed ID.

# Setup and Running the App
1. Make sure you have Python 3.x and Flask installed.
2. Save the code provided above in a file named app.py.
3. Create a `templates` folder in the same directory as `app.py`.
4. Inside the templates folder, create two HTML files: `index.html` and `results.html`.
Download the `index.html` and `results.html` templates from this GitHub Gist and save them in the templates folder.
Run the app using the command `python app.py`. The app will be accessible at `http://0.0.0.0:5000/`.

# API Documentation
## Search Results (`/search`)
## Request Parameters
- `term` (required): The search term to look for in PubMed.
- `page` (optional, default: 1): The page number of the search results.

## Response
A JSON object containing a list of article summaries and metadata for pagination.

## Example
`GET /search?term=tuberculosis&page=2`

## Abstract View (`/abstract/<pubmed_id>`)
## Path Parameters
- `pubmed_id`: The PubMed ID of the article to fetch the abstract for.

## Response
A JSON object containing the abstract text or a message indicating that the abstract was not found.