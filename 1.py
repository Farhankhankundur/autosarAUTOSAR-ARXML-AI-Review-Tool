import streamlit as st
import xmltodict
import json
import time
import psutil
from transformers import AutoModelForCausalLM, AutoTokenizer

# Custom CSS for dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: white;
    }
    .stSidebar {
        background-color: #1F2732;
        color: white;
    }
    .stButton>button {
        background-color: #1F2732;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stTextArea>textarea {
        background-color: #1F2732;
        color: white;
        border-radius: 5px;
    }
    .stMarkdown {
        color: white;
    }
    .stProgress>div>div>div {
        background-color: #1F2732;
    }
    .stFileUploader>div>div>div>button {
        background-color: #1F2732;
        color: white;
    }
    .stFileUploader>div>div>div>button:hover {
        background-color: #2E3B4E;
    }
    .stTabs>div>div>button {
        background-color: #1F2732;
        color: white;
    }
    .stTabs>div>div>button:hover {
        background-color: #2E3B4E;
    }
    </style>
    """, unsafe_allow_html=True)

# ---- AI Model Selection ----
MODEL_OPTIONS = {
    "GPT-2": "gpt2"
}

st.sidebar.title("⚙️ AI Model Selection")
selected_model = st.sidebar.selectbox("Choose AI Model:", list(MODEL_OPTIONS.keys()))

# Load Model (cached for faster loading)
@st.cache_resource
def load_model(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model(MODEL_OPTIONS[selected_model])

def generate_response(prompt):
    """Generate AI-powered review using the selected model"""
    inputs = tokenizer(prompt, return_tensors="pt")
    output = model.generate(**inputs, max_new_tokens=250)
    return tokenizer.decode(output[0], skip_special_tokens=True)

# ---- ARXML File Handling ----
@st.cache_data
def parse_arxml(file):
    """Parse ARXML into JSON format"""
    try:
        # Read the file content and reset the file pointer
        file_content = file.getvalue().decode("utf-8")
        if not file_content.strip():
            return {"error": "The uploaded file is empty."}
        data = xmltodict.parse(file_content)
        return data
    except Exception as e:
        return {"error": f"Error parsing ARXML file: {str(e)}"}

def check_consistency(file):
    """Check ARXML for missing values & AUTOSAR rule violations"""
    extracted_data = parse_arxml(file)
    if "error" in extracted_data:
        return [{"issue": f"❌ {extracted_data['error']}", "category": "Critical"}]

    # Ensure extracted_data is a dictionary
    if not isinstance(extracted_data, dict):
        return [{"issue": "❌ Invalid ARXML format. Expected a dictionary.", "category": "Critical"}]

    required_fields = ["ECU", "Software-Component", "Diagnostic", "Communication"]
    inconsistencies = []

    for field in required_fields:
        if field not in extracted_data:
            inconsistencies.append({
                "issue": f"❌ Missing required configuration: {field}",
                "category": "Critical"
            })

    return inconsistencies if inconsistencies else [{"issue": "✅ No inconsistencies found.", "category": "Info"}]

def compare_arxml(file1, file2):
    """Compare two ARXML files and highlight differences"""
    data1 = parse_arxml(file1)
    data2 = parse_arxml(file2)

    if "error" in data1 or "error" in data2:
        return [{"issue": "❌ Invalid ARXML file(s). Please upload valid files.", "category": "Critical"}]

    # Ensure both data1 and data2 are dictionaries
    if not isinstance(data1, dict) or not isinstance(data2, dict):
        return [{"issue": "❌ Invalid ARXML format. Expected dictionaries.", "category": "Critical"}]

    differences = []

    # Compare keys and values
    for key in data1:
        if key not in data2:
            differences.append(f"❌ Key '{key}' is missing in the second file.")
        elif data1[key] != data2[key]:
            differences.append(f"⚠️ Difference in '{key}': File 1 = {data1[key]}, File 2 = {data2[key]}")

    for key in data2:
        if key not in data1:
            differences.append(f"❌ Key '{key}' is missing in the first file.")

    return differences if differences else ["✅ No differences found between the files."]

# ---- AI-Powered ARXML Review ----
def ai_review_arxml(file):
    """AI-powered AUTOSAR compliance review"""
    inconsistencies = check_consistency(file)

    prompt = f"""
    You are an AUTOSAR expert. Analyze this ARXML file for compliance issues.
    Identify missing attributes, required configurations, and best practices.
    Provide explanations and fixes for the following issues:
    
    {json.dumps(inconsistencies, indent=4)}
    """

    ai_response = generate_response(prompt)
    return ai_response

# ---- Streamlit UI ----
st.title("🚗 AUTOSAR ARXML AI Review Tool")
st.write("AI-powered analysis of ARXML files for compliance and inconsistencies.")

# Multi-file uploader
uploaded_files = st.file_uploader("Upload ARXML Files", type=["arxml"], accept_multiple_files=True)

if uploaded_files:
    start_time = time.time()  # Track processing time
    memory_before = psutil.virtual_memory().used  # Memory before processing

    with st.spinner('Analyzing ARXML files...'):
        if len(uploaded_files) == 1:
            tab1, tab2 = st.tabs(["⚠️ AI-Powered Review", "🔍 Consistency Check"])
            
            with tab1:
                st.subheader("💡 AI-Powered AUTOSAR Compliance Report")
                ai_review = ai_review_arxml(uploaded_files[0])
                st.markdown("### AI Review Insights:")
                st.markdown(f"<div style='background-color: #1F2732; padding: 10px; border-radius: 5px;'>{ai_review}</div>", unsafe_allow_html=True)

            with tab2:
                st.subheader("🔎 Manual Consistency Check")
                consistency_result = check_consistency(uploaded_files[0])
                for issue in consistency_result:
                    st.markdown(f"**{issue['category']}**: {issue['issue']}")

        elif len(uploaded_files) == 2:
            tab1, tab2, tab3 = st.tabs(["⚠️ AI-Powered Review", "🔍 Consistency Check", "🔎 File Comparison"])
            
            with tab1:
                st.subheader("💡 AI-Powered AUTOSAR Compliance Report")
                ai_review = ai_review_arxml(uploaded_files[0])
                st.markdown("### AI Review Insights:")
                st.markdown(f"<div style='background-color: #1F2732; padding: 10px; border-radius: 5px;'>{ai_review}</div>", unsafe_allow_html=True)

            with tab2:
                st.subheader("🔎 Manual Consistency Check")
                consistency_result = check_consistency(uploaded_files[0])
                for issue in consistency_result:
                    st.markdown(f"**{issue['category']}**: {issue['issue']}")

            with tab3:
                st.subheader("🔎 ARXML File Comparison")
                comparison_result = compare_arxml(uploaded_files[0], uploaded_files[1])
                for result in comparison_result:
                    if isinstance(result, dict):
                        st.markdown(f"**{result['category']}**: {result['issue']}")
                    else:
                        st.markdown(f"**{result}**")
        else:
            st.error("Please upload 1 or 2 ARXML files.")

    # ---- Performance Metrics ----
    end_time = time.time()
    memory_after = psutil.virtual_memory().used
    processing_time = round(end_time - start_time, 2)
    memory_usage = (memory_after - memory_before) / (1024 ** 2)

    st.write(f"⏳ Processing Time: **{processing_time} seconds**")
    st.write(f"💾 Memory Usage: **{memory_usage:.2f} MB**")

st.write("🔗 Built using **Streamlit** and **GPT-2**.")