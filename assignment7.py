import os
import random
import streamlit as st

# Function to load documents from a base path
def load_documents(base_path):
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

# Function to compute relevance probabilities (Inference Model)
def compute_relevance_probabilities(documents, query):
    relevance_probs = {}
    for category, docs in documents.items():
        relevant_count = sum(1 for doc in docs if query in doc["content"])
        total_count = len(docs)
        relevance_probs[category] = relevant_count / total_count if total_count > 0 else 0
    return relevance_probs

# Function to retrieve documents based on relevance probabilities (Inference Model)
def retrieve_documents(query, documents, relevance_probs):
    ranked_docs = sorted(
        documents.items(),
        key=lambda item: relevance_probs.get(item[0], 0),
        reverse=True
    )
    return ranked_docs

# Function to define a belief network structure
def define_belief_network(documents):
    belief_network = {}
    for category, docs in documents.items():
        for doc in docs:
            node = f"{category}_{doc['title']}"
            belief_network[node] = ["query"]  # Link the document node to the query node
    belief_network["query"] = []  # Query is the root node
    return belief_network

# Function to create document-specific evidence
def get_document_evidence(documents, query):
    evidence = {}
    for category, docs in documents.items():
        for doc in docs:
            node = f"{category}_{doc['title']}"
            evidence[node] = query in doc["content"]  # True if query exists in document content
    evidence["query"] = True
    return evidence

# Function to calculate joint probabilities
def joint_probability(belief_network, evidence):
    joint_probs = {}
    for node, parents in belief_network.items():
        if node in evidence:
            joint_probs[node] = 1 if evidence[node] else 0
        else:
            # Compute probability based on parent nodes
            parent_probs = [joint_probs[parent] for parent in parents]
            joint_probs[node] = sum(parent_probs) / len(parent_probs) if parent_probs else random.random()
    return joint_probs

# Function to rank documents based on probabilities
def rank_documents_by_belief(belief_network, evidence):
    joint_probs = joint_probability(belief_network, evidence)
    document_probs = {node: prob for node, prob in joint_probs.items() if node != "query"}
    ranked_docs = sorted(document_probs.items(), key=lambda item: item[1], reverse=True)
    return ranked_docs

# Streamlit app
st.title("Information Retrieval Models")

# Load documents
base_path = "C:\\IR\\DataStructures"  # Change to your actual base path
documents = load_documents(base_path)

# Dropdown menu for model selection
model_choice = st.selectbox("Choose a model:", ["Inference Model", "Belief Network"])

# User input for query
query = st.text_input("Enter your query:")

if query:
    if model_choice == "Inference Model":
        st.subheader("Inference Model")
        relevance_probs = compute_relevance_probabilities(documents, query)
        ranked_documents = retrieve_documents(query, documents, relevance_probs)
        st.subheader("Top Ranked Documents:")
        for rank, (category, doc_list) in enumerate(ranked_documents, start=1):
            for doc in doc_list:
                st.write(f"Rank {rank}: {doc['title']} (Category: {category})")

    elif model_choice == "Belief Network":
        st.subheader("Belief Network")
        belief_network = define_belief_network(documents)
        evidence = get_document_evidence(documents, query)
        ranked_documents = rank_documents_by_belief(belief_network, evidence)
        st.subheader("Top Ranked Documents:")
        for rank, (doc_node, prob) in enumerate(ranked_documents, start=1):
            category, title = doc_node.split("_", 1)
            st.write(f"Rank {rank}: {title} (Category: {category}) - Probability: {prob:.2f}")
