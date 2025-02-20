import os
import json
import string
import streamlit as st

# Set up the document path
BASE_PATH = "C:\\IR\\DataStructures"

# Define a set of words to exclude from indexing (stop words)
excluded_words = {"the", "is", "in", "at", "of", "and", "a", "to", "for", "on", "it", "an", "with", "as", "by", "that", "this"}

# Function to check if a word is likely a noun (basic heuristic)
def is_noun(word):
    # Exclude stop words
    if not word or word in excluded_words:
        return False
    # Consider word as noun if it is alphabetic and starts with a capital letter (a basic heuristic)
    return word[0].isupper() or word.isalpha()

# Custom indexer class for inverted index
class InvertedIndexer:
    def __init__(self):
        self.index = {}  # Inverted index will store terms as keys and document paths as values
    
    def add(self, term, doc_path):
        if term not in self.index:
            self.index[term] = []
        if doc_path not in self.index[term]:
            self.index[term].append(doc_path)
    
    def search(self, query):
        query = query.lower()  # Normalize the query to lowercase
        return self.index.get(query, [])  # Return the document paths if the term exists
    
    def to_dict(self):
        return self.index

# Function to gather documents, tokenize, and create inverted index
def gather_documents_and_create_index(base_path=BASE_PATH):
    documents = []
    title_index = InvertedIndexer()  # Inverted index for titles
    content_index = InvertedIndexer()  # Inverted index for content (nouns)
    
    # Traverse document folders
    for foldername in os.listdir(base_path):
        folder_path = os.path.join(base_path, foldername)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                # Add document to the list of documents
                documents.append({
                    "title": filename,
                    "path": file_path,
                    "content": content
                })
                
                # Tokenize the title and create inverted index for titles
                title = filename.strip(string.punctuation).lower()
                title_index.add(title, file_path)  # Add title to title index
                
                # Tokenize the content and create inverted index for nouns
                words = content.split()
                for word in words:
                    word = word.strip(string.punctuation).lower()  # Remove punctuation and normalize to lowercase
                    if is_noun(word):  # Check if the word is likely a noun and not a stop word
                        content_index.add(word, file_path)  # Add to content index

    # Step 3: Save the inverted indexes to JSON
    with open("title_index.json", "w") as title_file:
        json.dump(title_index.to_dict(), title_file)

    with open("content_index.json", "w") as content_file:
        json.dump(content_index.to_dict(), content_file)

    return documents, title_index, content_index

# Function to search documents based on the inverted index
def search_documents(query, search_by, title_index, content_index):
    query = query.lower()  # Normalize query to lowercase
    
    if search_by == "Title":
        results = title_index.search(query)  # Search in title index
    elif search_by == "Content":
        results = content_index.search(query)  # Search in content index
    
    return results

# Gather documents and create inverted indexes
documents, title_index, content_index = gather_documents_and_create_index()

# Streamlit page setup
st.title("Document Search Engine")
st.write("Search for documents by **Title** or **Content**")

# Streamlit input fields
query = st.text_input("Enter your search query:")
search_by = st.selectbox("Search By", ("Title", "Content"))

# Add a Search button
search_button = st.button("Search")

if search_button and query:
    results = search_documents(query, search_by, title_index, content_index)
    
    if results:
        st.write(f"**{len(results)} results found for '{query}' by {search_by}:**")
        for path in results:
            st.write(f"**Document Path**: {path}")
            st.write("---")  # separator between results
    else:
        st.write("No results found. Try a different query.")
