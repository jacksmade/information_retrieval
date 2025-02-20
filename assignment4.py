import os
import streamlit as st

# Function to load documents and create the content hierarchy
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

# Function to process content and convert specific words to clickable elements
def convert_to_hyperlinked_content(content, category):
    """
    Process the content to make specific words clickable to navigate within the same page.
    """
    words = content.split()
    clickable_words = []
    for word in words:
        # Define words to make clickable and associate them with navigation actions
        if word.lower() == "stack":
            clickable_words.append(f'<a href="#" onclick="set_state(\'category\', \'{category}\', \'doc\', \'stack_intro.txt\')">{word}</a>')
        elif word.lower() == "queue":
            clickable_words.append(f'<a href="#" onclick="set_state(\'category\', \'{category}\', \'doc\', \'queue_intro.txt\')">{word}</a>')
        elif word.lower() == "heap":
            clickable_words.append(f'<a href="#" onclick="set_state(\'category\', \'{category}\', \'doc\', \'heap_intro.txt\')">{word}</a>')
        else:
            clickable_words.append(word)
    return " ".join(clickable_words)

# Streamlit UI Configuration
st.set_page_config(layout="wide", page_title="Structure Guided Document Viewer")
st.sidebar.header("Documents")

# Define the base folder path
BASE_PATH = "C:\\IR\\DataStructures"  # Replace this with your documents folder path
documents = load_documents(BASE_PATH)

# Initialize session state for selected category and document
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

# Sidebar with hierarchical structure
st.sidebar.title("Structure Guided Browsing")

# Populate the sidebar with categories and documents
for category, files in documents.items():
    with st.sidebar.expander(category, expanded=False):
        for doc in files:
            if st.button(doc["title"], key=f"{category}-{doc['title']}"):
                st.session_state.selected_category = category
                st.session_state.selected_document = doc

# Main content area
st.title("Document Viewer")
if st.session_state.selected_category and st.session_state.selected_document:
    selected_category = st.session_state.selected_category
    selected_document = st.session_state.selected_document

    st.subheader(selected_document["title"])
    # Convert content into clickable words
    hyperlinked_content = convert_to_hyperlinked_content(selected_document["content"], selected_category)
    st.markdown(hyperlinked_content, unsafe_allow_html=True)

    # Display related documents as buttons
    st.markdown("### Related Documents")
    for doc in documents[selected_category]:
        if doc["title"] != selected_document["title"]:
            if st.button(doc["title"], key=f"related-{doc['title']}"):
                st.session_state.selected_document = doc
else:
    st.info("Please select a document from the sidebar to view its content.")
