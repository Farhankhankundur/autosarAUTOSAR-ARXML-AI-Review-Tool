import streamlit as st
from lxml import etree
import pandas as pd
import google.generativeai as genai
import os

# Set Gemini API Key
os.environ["GEMINI_API_KEY"] = ""
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Custom CSS for Full-Screen Sections
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Full Page Styling */
    .stApp {
        background-color: #181818;
        color: white;
        font-family: 'Inter', sans-serif;
    }

    /* Two Sections */
    .container {
        display: flex;
        width: 100%;
        height: 100vh;
    }

    /* Left Section */
    .left-section {
        width: 35%;
        background-color: #222831;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 5px 5px 20px rgba(0, 0, 0, 0.3);
    }

    /* Right Section */
    .right-section {
        width: 65%;
        background-color: #181818;
        padding: 40px;
        border-radius: 10px;
    }

    /* Vertical Divider Line */
    .divider {
        width: 4px;
        background-color: #00ADB5;
        height: 100%;
        margin: 0 20px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #00ADB5;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 600;
        border: none;
        transition: background-color 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #007d85;
    }

    /* File Upload */
    .stFileUploader>div>div>div>div {
        background-color: #393E46;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #00ADB5;
    }

    /* Headings */
    .stMarkdown h1, .stMarkdown h2 {
        text-align: center;
        color: #00ADB5;
    }

    /* Dataframe Styling */
    .stDataFrame {
        background-color: #222831;
        border-radius: 8px;
        border: 1px solid #00ADB5;
    }

    /* Comparison Table */
    .dataframe-container {
        border-radius: 10px;
        background-color: #222831;
        padding: 15px;
        border: 2px solid #00ADB5;
        overflow-x: auto;
    }

    /* Success & Error Messages */
    .stSuccess {
        background-color: #155724;
        color: #d4edda;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #28a745;
    }

    .stError {
        background-color: #721c24;
        color: #f8d7da;
        border-radius: 8px;
        padding: 15px;
        border: 1px solid #dc3545;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title
st.markdown("<h1>AUTOSAR ARXML AI Agent</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; font-size: 18px;'>Upload and analyze AUTOSAR ARXML files with ease.</p>",
    unsafe_allow_html=True,
)

# Function to Parse ARXML
def parse_arxml(file):
    try:
        tree = etree.parse(file)
        return tree.getroot()
    except Exception as e:
        st.error(f"Error parsing ARXML file: {e}")
        return None

# Function to Extract Elements
def extract_autosar_elements(root):
    elements = []
    for elem in root.iter():
        if "SHORT-NAME" in elem.tag:
            parent_tag = elem.getparent().tag
            parent_name = elem.getparent().get("SHORT-NAME", "N/A")
            elements.append({"Tag": elem.tag, "Parent Tag": parent_tag, "Parent Name": parent_name, "Value": elem.text})
    return elements

# Function to Compare Two ARXML Files
def compare_arxml(elements1, elements2):
    df1 = pd.DataFrame(elements1)
    df2 = pd.DataFrame(elements2)
    merged_df = df1.merge(df2, on=["Tag", "Parent Tag", "Parent Name"], how="outer", suffixes=("_File1", "_File2"))
    merged_df["Difference"] = merged_df["Value_File1"] != merged_df["Value_File2"]
    return merged_df[merged_df["Difference"]]

# Full Page Layout
st.markdown('<div class="container">', unsafe_allow_html=True)

# Left Section (File Upload & Menu)
st.markdown('<div class="left-section">', unsafe_allow_html=True)
st.markdown("<h2>Upload ARXML Files</h2>", unsafe_allow_html=True)

uploaded_file_1 = st.file_uploader("Upload ARXML File 1", type="arxml", key="file1")
uploaded_file_2 = st.file_uploader("Upload ARXML File 2 (optional)", type="arxml", key="file2")

# Menu for Actions
st.markdown("<h2>Menu</h2>", unsafe_allow_html=True)
menu_option = st.radio(
    "Choose an option:",
    ["Validation", "Comparison", "Ask a Question"],
    key="menu"
)
st.markdown("</div>", unsafe_allow_html=True)

# Vertical Divider
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# Right Section (Results)
st.markdown('<div class="right-section">', unsafe_allow_html=True)

if uploaded_file_1:
    root1 = parse_arxml(uploaded_file_1)
    if root1:
        elements1 = extract_autosar_elements(root1)

        if menu_option == "Comparison" and uploaded_file_2:
            root2 = parse_arxml(uploaded_file_2)
            if root2:
                elements2 = extract_autosar_elements(root2)
                st.markdown("<h2>Comparison Results</h2>", unsafe_allow_html=True)
                differences = compare_arxml(elements1, elements2)

                if not differences.empty:
                    st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
                    st.dataframe(differences.style.applymap(lambda x: "background-color: #FF5733" if x == True else ""))
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.success("No differences found.")

        elif menu_option == "Validation":
            st.markdown("<h2>Validation Results</h2>", unsafe_allow_html=True)
            st.success("No validation errors found.")  # Placeholder

        elif menu_option == "Ask a Question":
            st.markdown("<h2>Ask a Question</h2>", unsafe_allow_html=True)
            question = st.text_input("Ask a question about the ARXML file:")
            if question:
                st.write("Answer: AI-generated response placeholder")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
