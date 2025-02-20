import streamlit as st
import os
import string
from collections import defaultdict
import networkx as nx


class InvertedIndexer:
    def __init__(self):
        self.index = defaultdict(set)

    def add(self, term, doc_id):
        self.index[term].add(doc_id)

    def search(self, term):
        return self.index.get(term, set())


def is_valid_word(word):
    return word.isalpha()  # Checks if the word consists of alphabetic characters


def build_proximal_graph(documents):
    graph = nx.Graph()
    for doc in documents:
        title = doc['title']
        graph.add_node(title, path=doc['path'])
        words = set(doc['content'].split())
        for word in words:
            graph.add_edge(title, word)
    return graph


def gather_documents_and_create_index(base_path):
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

    return documents, title_index, content_index, build_proximal_graph(documents)


# Streamlit App
BASE_PATH = "C:\\IR\\DataStructures"  # Replace with your documents folder path

st.title("Document Retrieval System")
st.sidebar.header("Select Retrieval Model")

# Load documents and create indexes
st.write("Loading documents...")
documents, title_index, content_index, proximal_graph = gather_documents_and_create_index(BASE_PATH)
st.success("Documents loaded successfully!")

# Model Selection
model = st.sidebar.selectbox(
    "Choose a retrieval model",
    ["Probabilistic (Binary Independence Model)", "Non-Overlapped List Model", "Proximal Nodes Model"]
)

# User Query Input
query = st.text_input("Enter your search query:")

if st.button("Search"):
    if model == "Probabilistic (Binary Independence Model)":
        st.subheader("Probabilistic Retrieval Results")
        query_terms = query.strip().lower().split()
        document_scores = defaultdict(int)

        # Calculate scores for all documents
        all_docs = {doc['path']: 0 for doc in documents}  # Initialize all documents with a score of 0

        for term in query_terms:
            relevant_docs = content_index.search(term)
            for doc in relevant_docs:
                all_docs[doc] += 1  # Increment score for relevant documents

        # Sort documents by their scores
        ranked_docs = sorted(all_docs.items(), key=lambda x: x[1], reverse=True)

        # Show scores for all documents
        st.write("Scores for all documents:")
        for doc, score in ranked_docs:
            st.write(f"{doc} - Score: {score}")

    elif model == "Non-Overlapped List Model":
        st.subheader("Non-Overlapped List Results")
        query_terms = query.strip().lower().split()
        all_documents = set()

        for term in query_terms:
            all_documents |= content_index.search(term)  # Union of document sets

        st.write("Relevant Documents:")
        for doc in all_documents:
            st.write(doc)

    elif model == "Proximal Nodes Model":
        st.subheader("Proximal Nodes Results")
        nodes_of_interest = query.strip().lower().split()
        relevant_docs = set()

        for node in nodes_of_interest:
            if proximal_graph.has_node(node):
                neighbors = proximal_graph.neighbors(node)
                for neighbor in neighbors:
                    if neighbor in proximal_graph.nodes:
                        relevant_docs.add(proximal_graph.nodes[neighbor].get("path", neighbor))

        st.write("Documents connected to proximal nodes:")
        for doc in relevant_docs:
            st.write(doc)

# Evaluate Model (Optional)
if st.sidebar.checkbox("Show evaluation metrics"):
    st.subheader("Evaluation Metrics")
    st.write("Metrics such as Precision, Recall, and F1-score can be computed based on ground truth relevance data.")
