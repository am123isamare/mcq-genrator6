import streamlit as st
import PyPDF2
import re
from random import sample, shuffle

# Function to extract text from PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from TXT file
def extract_text_from_txt(file):
    return file.read().decode("utf-8")

# Function to clean and filter text
def clean_text(text):
    # Remove excessive whitespace and special characters
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,]', '', text)
    sentences = re.split(r'(?<=\.)\s', text)  # Split sentences by period followed by a space
    return [sentence.strip() for sentence in sentences if len(sentence.split()) > 5]  # Filter short sentences

# Function to generate MCQs
def generate_mcqs(sentences, limit):
    mcqs = []
    for sentence in sample(sentences, min(limit, len(sentences))):
        words = sentence.split()
        if len(words) > 4:
            correct_answer = sample(words, 1)[0]  # Randomly pick a word as the correct answer
            # Generate options: Correct answer + 3 random words from the sentence
            options = list(set([correct_answer] + sample(words, min(4, len(words)))))
            shuffle(options)  # Shuffle options
            question = sentence.replace(correct_answer, "_____")
            mcqs.append({
                "question": question.strip(),
                "options": options,
                "answer": correct_answer
            })
    return mcqs

# Streamlit App
st.title("Multiple Choice Question (MCQ) Generator")

# File upload
uploaded_file = st.file_uploader("Upload a File (.txt or .pdf)", type=["txt", "pdf"])
mcq_limit = st.number_input("Enter the number of MCQs to generate (max 50)", min_value=1, max_value=50, step=1)

if uploaded_file and st.button("Generate MCQs"):
    file_type = uploaded_file.name.split('.')[-1]
    text = ""

    try:
        # Extract text based on file type
        if file_type == "pdf":
            text = extract_text_from_pdf(uploaded_file)
        elif file_type == "txt":
            text = extract_text_from_txt(uploaded_file)
        else:
            st.error("Unsupported file type.")
        
        if text:
            # Clean and filter text
            sentences = clean_text(text)

            # Generate MCQs
            mcqs = generate_mcqs(sentences, mcq_limit)

            if mcqs:
                st.write("### Generated MCQs")
                for i, mcq in enumerate(mcqs):
                    st.write(f"**Q{i+1}: {mcq['question']}**")
                    for opt in mcq['options']:
                        st.write(f"- {opt}")
                    st.write(f"*Answer: {mcq['answer']}*")

                # Downloadable MCQ file
                mcq_text = "\n\n".join([
                    f"Q{i+1}: {mcq['question']}\nOptions: " + ', '.join(mcq['options']) + f"\nAnswer: {mcq['answer']}"
                    for i, mcq in enumerate(mcqs)
                ])
                st.download_button("Download MCQs", data=mcq_text.encode(), file_name="mcqs.txt", mime="text/plain")
            else:
                st.warning("Not enough valid sentences to generate MCQs.")
    
    except Exception as e:
        st.error(f"Error: {e}")
