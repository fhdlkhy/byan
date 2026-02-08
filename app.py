import streamlit as st
import google.generativeai as genai
import json
import re
import tempfile
import os

# 1. إعداد الصفحة
st.set_page_config(page_title="بَيَان", page_icon="🍃", layout="centered")

# 2. التصميم (CSS) - لاحظ علامات التنصيص الثلاثية في البداية والنهاية
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;500;800&display=swap');
header, footer, .stDeployButton {display: none !important;}
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif;
    background-color: #ffffff;
    color: #212529;
}
.logo-container {
    text-align: center;
    padding-top: 3rem;
}
.logo-text {
    font-size: 4rem;
    font-weight: 800;
    color: #198754;
    margin: 0;
}
.tagline {
    color: #c5a059;
    font-size: 1.1rem;
    margin-top: -10px;
}
.stTextArea textarea {
    border: 2px solid #f1f3f5;
    border-radius: 15px;
    padding: 15px;
    font-size: 1.2rem;
    text-align: right;
    direction: rtl;
}
.stButton button {
    background-color: #198754;
    color: white;
    border-radius: 50px;
    width: 100%;
    border: none;
    padding: 10px;
}
.result-card {
    background-color: #f8f9fa;
    border-right: 4px solid #c5a059;
    padding: 2rem;
    border-radius: 12px;
    margin-top: 2rem;
    text-align: right;
    direction: rtl;
}
.correction-text {
    font-size: 1.4rem;
    color: #198754;
    font-weight: bold;
}
.original-text {
    color: #adb5bd;
    text-decoration: line-through;
}
</style>
""", unsafe_allow_html=True)

# 3. المحرك
api_key = "AIzaSyB72GXyTtvjxj5XqTMLuOWm9bmcY4qCXys"
if api_key: genai.configure(api_key=api_key)

def process(input_val, is_audio=False):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = """
        أنت مدقق لغوي (بَيَان).
        1. حول المدخلات إلى نص فصحى سليم وبليغ.
        2. أخرج النتيجة بصيغة JSON فقط:
        {"original": "النص الأصلي", "corrected": "النص المصحح", "tip": "نصيحة قصيرة"}
        """
        
        if is_audio:
            response = model.generate_content([prompt, input_val])
        else:
            response = model.generate_content(f"{prompt}\nالنص: {input_val}")
            
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"original": "...", "corrected": response.text, "tip": "تدقيق عام"}
        
    except Exception as e:
        return {"original": "خطأ", "corrected": "حدث خطأ", "tip": str(e)}

# 4. الواجهة
st.markdown("""
<div class="logo-container">
    <div class="logo-text">بَيَان</div>
    <div class="tagline">فصاحة اللسان .. بذكاء البيان</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# الحالة
if 'result' not in st.session_state:
    st.session_state.result = None

# الإدخال
method = st.radio("الوسيلة:", ["كتابة", "صوت"], horizontal=True, label_visibility="collapsed")

if method == "كتابة":
    txt = st.text_area("", placeholder="اكتب هنا...")
    if st.button("تدقيق") and txt:
        with st.spinner("جاري التدقيق..."):
            st.session_state.result = process(txt, False)
else:
    st.info("سجل صوتك...")
    audio = st.audio_input("تسجيل")
    if audio:
        with st.spinner("جاري التحليل..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio.read())
                tmp_path = tmp.name
            
            myfile = genai.upload_file(tmp_path)
            st.session_state.result = process(myfile, True)
            os.remove(tmp_path)

# النتيجة
if st.session_state.result:
    res = st.session_state.result
    st.markdown(f"""
    <div class="result-card">
        <div class="original-text">{res.get('original', '...')}</div>
        <div class="correction-text">{res.get('corrected', '...')}</div>
        <div style="margin-top:10px; color:#c5a059;">💡 {res.get('tip', '...')}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center; margin-top:50px; color:#ccc; font-size:12px;'>Tutoz AI Studio 2026</div>", unsafe_allow_html=True)
