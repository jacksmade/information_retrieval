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

    for doc in documents:
        tf = {}
        content_words = doc["content"].split()
        for term in query_terms:
            tf[term] = content_words.count(term) / len(content_words) if content_words else 0
            tf_idf_scores[doc["path"]] = sum(tf[term] * idf[term] for term in query_terms)

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

# Query function for keyword matching and TF-IDF scoring
def query_documents(query, search_by, ranking_method, title_index, content_index, documents):
    query_terms = [term.lower() for term in query.split() if is_valid_word(term)]
    if not query_terms:
        return []

    if ranking_method == "Keyword Matching":
        index = content_index if search_by == "Content" else title_index
        matched_docs = index.search(query_terms)
        ranked_results = sort_by_keyword_matches(matched_docs, query_terms)
    elif ranking_method == "TF-IDF Scoring":
        ranked_results = calculate_tf_idf(query_terms, documents, content_index)
    else:
        ranked_results = []

    return ranked_results

# Helper function to rank documents by keyword matches
def sort_by_keyword_matches(documents, query_terms):
    def count_keyword_matches(doc_path):
        return sum(1 for term in query_terms if term in doc_path.lower())
    
    return sorted(documents, key=count_keyword_matches, reverse=True)

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
st.title("Document Search Engine with Ranking")
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
