import os
import streamlit as st
import numpy as np

# Function to load documents and create the content hierarchy
def load_documents(base_path):
    """
    Load documents from the specified base path.
    """
    documents = {}
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            documents[folder_name] = []
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                documents[folder_name].append({
                    "title": file_name,
                    "content": content,
                    "path": file_path
                })
    return documents

# Function to process Boolean Extended model
def process_boolean_extended_query(query, documents):
    """
    Process a Boolean Extended query.
    """
    terms = query.split()
    results = []
    for category, docs in documents.items():
        for doc in docs:
            # Implement basic AND, OR, NOT operations based on query terms
            if all(term.lower() in doc["content"].lower() for term in terms if term.startswith('+')):
                results.append(doc)
            elif any(term.lower() in doc["content"].lower() for term in terms if term.startswith('-')):
                continue
            elif any(term.lower() in doc["content"].lower() for term in terms):
                results.append(doc)
    return results

# Function to process Fuzzy model
def process_fuzzy_query(query, documents):
    """
    Process a Fuzzy query.
    """
    terms = query.split()
    results = []
    for category, docs in documents.items():
        for doc in docs:
            relevance = sum(1 for term in terms if term.lower() in doc["content"].lower()) / len(terms)
            if relevance > 0:
                doc["relevance"] = relevance
                results.append(doc)
    return sorted(results, key=lambda x: x["relevance"], reverse=True)

# Function to process Generalized Vector model
def process_generalized_vector_query(query, documents):
    """
    Process a Generalized Vector query.
    """
    def vectorize(text):
        return {term: 1 for term in text.split()}
    
    query_vector = vectorize(query)
    results = []
    for category, docs in documents.items():
        for doc in docs:
            doc_vector = vectorize(doc["content"])
            similarity = sum(query_vector.get(term, 0) * doc_vector.get(term, 0) for term in query_vector)
            if similarity > 0:
                doc["similarity"] = similarity
                results.append(doc)
    return sorted(results, key=lambda x: x["similarity"], reverse=True)

# Function to process Latent Semantic Indexing (LSI) model
def process_lsi_query(query, documents):
    """
    Process an LSI query.
    """
    all_texts = [" ".join(doc["content"].split()) for docs in documents.values() for doc in docs]
    # Create a term-document matrix
    term_doc_matrix = []
    terms = list(set(" ".join(all_texts).split()))
    for text in all_texts:
        term_counts = {term: text.split().count(term) for term in terms}
        term_doc_matrix.append([term_counts.get(term, 0) for term in terms])
    
    # Convert the term-document matrix to a numpy array
    term_doc_matrix = np.array(term_doc_matrix)
    
    # Transform the query into the same space
    query_vector = np.array([1 if term in query.split() else 0 for term in terms])
    
    # Calculate cosine similarity manually
    def cosine_similarity(X, Y):
        dot_product = np.dot(X, Y.T)
        norm_X = np.linalg.norm(X)
        norm_Y = np.linalg.norm(Y)
        return dot_product / (norm_X * norm_Y)
    
    similarity_scores = []
    for i, category in enumerate(documents):
        for j, doc in enumerate(documents[category]):
            doc_vector = term_doc_matrix[i * len(documents[category]) + j]
            similarity = cosine_similarity(query_vector, doc_vector)
            doc["lsi_score"] = similarity
            similarity_scores.append(doc)
    
    return sorted(similarity_scores, key=lambda x: x["lsi_score"], reverse=True)

# Streamlit UI Configuration
st.set_page_config(layout="wide", page_title="Document Viewer")

# Define the base folder path
BASE_PATH = "C:\\IR\\DataStructures"  # Replace this with your documents folder path
documents = load_documents(BASE_PATH)

# Initialize session state for selected document
if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

# Main content area
st.title("Document Viewer")
query = st.text_input("Enter Query:")

if query:
    model_choice = st.radio("Choose IR Model:", ["Boolean Extended", "Fuzzy", "Generalized Vector", "LSI"])

    if model_choice == "Boolean Extended":
        results = process_boolean_extended_query(query, documents)
        for result in results:
            st.write(f"Title: {result['title']}")

    elif model_choice == "Fuzzy":
        results = process_fuzzy_query(query, documents)
        for result in results:
            st.write(f"Title: {result['title']} (Relevance: {result['relevance']})")

    elif model_choice == "Generalized Vector":
        results = process_generalized_vector_query(query, documents)
        for result in results:
            st.write(f"Title: {result['title']} (Similarity: {result['similarity']})")

    elif model_choice == "LSI":
        results = process_lsi_query(query, documents)
        for result in results:
            st.write(f"Title: {result['title']} (LSI Score: {result['lsi_score']})")

else:
    st.info("Please enter a query to search.")
