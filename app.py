
import streamlit as st
import openai
from gtts import gTTS
import os
import tempfile
import pandas as pd
import fitz  # PyMuPDF
import docx
from openai import OpenAI
# Load your OpenAI key
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set page configuration
st.set_page_config(page_title="AI Translator & Speaker", layout="centered")

st.title("🌍 AI Text Translator & Speaker")
st.markdown("Translate your text into any language and listen to it!")

# Language options
language_map = {
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Hindi": "hi",
    "Marathi": "mr",
    "Chinese": "zh",
    "Arabic": "ar",
    "Russian": "ru"
}

def translate_text(text, target_lang):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator."},
                {"role": "user", "content": f"Translate this into {target_lang}: {text}"}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    
    except openai.RateLimitError:
        st.warning("🚫 OpenAI API quota exceeded. This is a mock translation.")
        return f" {text} (in)→ [{target_lang}]"


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "text/plain":
        return str(uploaded_file.read(), "utf-8")
    elif uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        doc = docx.Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.type in ["text/csv", "application/vnd.ms-excel"]:
        df = pd.read_csv(uploaded_file)
        return df.to_string(index=False)
    return ""

def text_to_speech(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_file.name)
    return temp_file.name

# Upload or enter text
upload = st.file_uploader("📁 Upload a file (TXT, PDF, DOCX, CSV)", type=["txt", "pdf", "docx", "csv"])
input_text = ""
if upload:
    input_text = extract_text_from_file(upload)
    st.success("✅ File loaded successfully!")
else:
    input_text = st.text_area("📝 Or type your text below:", "")

# Language selection
selected_lang = st.selectbox("🌐 Select target language", list(language_map.keys()))

# Translate
if st.button("Translate"):
    if input_text:
        with st.spinner("Translating..."):
            translated = translate_text(input_text, selected_lang)
            st.subheader("Translated Text:")
            st.write(translated)

            # Convert to speech
            audio_file = text_to_speech(translated, language_map[selected_lang])
            st.audio(audio_file, format='audio/mp3')
            st.download_button("⬇️ Download Audio", data=open(audio_file, "rb"), file_name="translated_audio.mp3")
    else:
        st.warning("⚠️ Please upload a file or enter text.")

