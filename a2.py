import os
import string
import math
import streamlit as st

# Set up the document path
BASE_PATH = "C:\\IR\\DataStructures"

# Define stop words
STOP_WORDS = {"the", "is", "in", "at", "of", "and", "a", "to", "for", "on", "it", "an", "with", "as", "by", "that", "this"}

# Function to check if a word is valid (e.g., not a stop word)
def is_valid_word(word):
    return word and word not in STOP_WORDS and word.isalpha()

# Inverted index class for keyword search
class InvertedIndexer:
    def __init__(self):
        self.index = {}

    def add(self, term, doc_path):
        if term not in self.index:
            self.index[term] = []
        if doc_path not in self.index[term]:
            self.index[term].append(doc_path)

    def search(self, query_terms):
        results = []
        for term in query_terms:
            if term in self.index:
                results.extend(self.index[term])
        return list(set(results))

# TF-IDF calculation
def calculate_tf_idf(query_terms, documents, content_index):
    tf_idf_scores = {}
    num_docs = len(documents)

    # Calculate IDF
    idf = {}
    for term in query_terms:
        doc_count = sum(1 for doc in documents if term in content_index.index and doc["path"] in content_index.index[term])
        idf[term] = math.log((1 + num_docs) / (1 + doc_count)) + 1  # Add 1 to avoid division by zero
        print(f"IDF[{term}] = {idf[term]:.4f}")  # Log IDF to console

    for doc in documents:
        tf = {}
        content_words = doc["content"].split()
        for term in query_terms:
            tf[term] = content_words.count(term) / len(content_words) if content_words else 0
            print(f"TF[{term}] for Document[{doc['path']}] = {tf[term]:.4f}")  # Log TF to console

        tf_idf_scores[doc["path"]] = sum(tf.get(term, 0) * idf[term] for term in query_terms)
        print(f"TF-IDF Score for Document[{doc['path']}] = {tf_idf_scores[doc['path']]:.4f}")  # Log TF-IDF to console

    return sorted(tf_idf_scores.items(), key=get_score, reverse=True)  # Return ranked documents

# Helper function for sorting by score
def get_score(item):
    return item[1]

# Gather documents and create inverted indexes
def gather_documents_and_create_index(base_path=BASE_PATH):
    documents = []
    title_index = InvertedIndexer()
    content_index = InvertedIndexer()

    for foldername in os.listdir(base_path):
        folder_path = os.path.join(base_path, foldername)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                documents.append({
                    "title": filename,
                    "path": file_path,
                    "content": content
                })

                title_index.add(filename.strip(string.punctuation).lower(), file_path)

                for word in content.split():
                    word = word.strip(string.punctuation).lower()
                    if is_valid_word(word):
                        content_index.add(word, file_path)

    return documents, title_index, content_index

# Handle boolean queries
def parse_boolean_query(query):
    query = query.lower()
    and_terms = []
    or_terms = []
    not_terms = []

    terms = query.split()
    current_operator = "OR"  # Default operator

    for term in terms:
        if term == "and":
            current_operator = "AND"
        elif term == "or":
            current_operator = "OR"
        elif term == "not":
            current_operator = "NOT"
        else:
            if current_operator == "AND":
                and_terms.append(term)
            elif current_operator == "OR":
                or_terms.append(term)
            elif current_operator == "NOT":
                not_terms.append(term)

    return and_terms, or_terms, not_terms

def apply_boolean_logic(and_terms, or_terms, not_terms, documents, content_index):
    and_docs = set(content_index.search(and_terms)) if and_terms else set(doc["path"] for doc in documents)
    or_docs = set(content_index.search(or_terms)) if or_terms else set()
    not_docs = set(content_index.search(not_terms)) if not_terms else set()

    # Combine results using boolean logic
    result_docs = (and_docs & or_docs) if or_docs else and_docs
    result_docs = result_docs - not_docs

    return list(result_docs)

# Query function for keyword matching and TF-IDF scoring
def query_documents(query, search_by, ranking_method, title_index, content_index, documents):
    and_terms, or_terms, not_terms = parse_boolean_query(query)

    if ranking_method == "Keyword Matching":
        results = apply_boolean_logic(and_terms, or_terms, not_terms, documents, content_index)
    elif ranking_method == "TF-IDF Scoring":
        query_terms = and_terms + or_terms  # NOT terms are excluded from scoring
        results = calculate_tf_idf(query_terms, documents, content_index)
    else:
        results = []

    return results

# Display ranked documents
def display_results(results, ranking_method):
    st.write(f"**{len(results)} results found:**")
    for result in results:
        if ranking_method == "TF-IDF Scoring":
            st.write(f"**Document Path**: {result[0]}")
            st.write(f"**Relevance Score**: {result[1]:.4f}")
        else:
            st.write(f"**Document Path**: {result}")
        st.write("---")

# Streamlit interface
st.title("Document Search Engine with Boolean Queries")
st.write("Search for documents by **Title** or **Content** using **Keyword Matching** or **TF-IDF Scoring**")

query = st.text_input("Enter your search query:")
search_by = st.selectbox("Search By", ("Title", "Content"))
ranking_method = st.selectbox("Ranking Method", ("Keyword Matching", "TF-IDF Scoring"))
search_button = st.button("Search")

# Index documents
documents, title_index, content_index = gather_documents_and_create_index()

if search_button and query:
    results = query_documents(query, search_by, ranking_method, title_index, content_index, documents)
    if results:
        display_results(results, ranking_method)
    else:
        st.write("No results found. Try a different query.")
