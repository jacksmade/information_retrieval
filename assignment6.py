import streamlit as st
import numpy as np
from scipy.special import expit as sigmoid
import speech_recognition as sr
import os

def load_documents(base_path):
    """
    Load documents from the specified base path and organize them into categories.
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

def compute_relevance_score(X1, X2):
    # Neural network weights and biases
    W_input1, W_input2 = 0.8, 0.6
    B_input = 0.2
    W_output = 1.5
    B_output = -0.4

    # Hidden layer calculation
    H_input = W_input1 * X1 + W_input2 * X2 + B_input
    H = sigmoid(H_input)

    # Output layer calculation
    relevance_score = W_output * H + B_output
    return relevance_score

def preprocess_query(query):
    # A very simple preprocessing example: splitting query into words
    words = query.lower().split()
    X1 = len([word for word in words if word in ["binary", "queue"]]) / len(words)
    X2 = len([word for word in words if word in ["hashing", "stack", "binary"]]) / len(words)
    return X1, X2

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak your query.")
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio)
            st.success(f"You said: {query}")
            return query
        except sr.WaitTimeoutError:
            st.error("Listening timed out. Please try again.")
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio. Please try again.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
    return None

# Fixed path to the base directory
BASE_PATH = "C:\\IR\\DataStructures"

# Streamlit UI
st.title("Neural Network for Information Retrieval")
st.header("Voice-Activated Query Processing")

if os.path.exists(BASE_PATH):
    documents = load_documents(BASE_PATH)
    st.success("Documents loaded successfully!")
else:
    st.error("Invalid path. Please check the BASE_PATH and try again.")

query = st.text_input("Or type your query below:")
if st.button("Use Speech Input"):
    query = speech_to_text()

if query and 'documents' in locals():
    query_X1, query_X2 = preprocess_query(query)
    results = []

    for category, docs in documents.items():
        for doc in docs:
            doc_X1, doc_X2 = preprocess_query(doc["content"])
            score = compute_relevance_score(query_X1, query_X2)
            results.append({
                "title": doc["title"],
                "category": category,
                "score": score,
                "path": doc["path"]
            })

    # Sort results by score
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # Display top results
    st.write("Top Matching Documents:")
    for result in results[:5]:
        st.write(f"Title: {result['title']}, Category: {result['category']}, Score: {result['score']:.3f}")
