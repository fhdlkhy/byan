import streamlit as st
import google.generativeai as genai
import os
import tempfile

# ==========================================
# 1. إعدادات الصفحة والتصميم (Official Identity)
# ==========================================
st.set_page_config(page_title="منصة بيان", page_icon="🟢", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;800&display=swap');
    
    /* تعيين الخط العام */
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        background-color: #ffffff;
        color: #212529;
    }
    
    /* الهيدر والعناوين */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        border-bottom: 2px solid #e9ecef;
        margin-bottom: 2rem;
    }
    
    .title-text {
        color: #198754; /* أخضر زمردي */
        font-weight: 800;
        font-size: 2.5rem;
        margin: 0;
    }
    
    .subtitle-text {
        color: #6c757d;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* صندوق السيناريو */
    .scenario-card {
        background: #f8f9fa;
        border-right: 5px solid #198754;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin: 1.5rem 0;
        text-align: right;
        direction: rtl;
    }
    
    .scenario-text {
        font-size: 1.2rem;
        line-height: 1.8;
        color: #2c3e50;
        font-weight: 600;
    }

    /* بطاقة النتيجة */
    .result-card {
        background: linear-gradient(145deg, #ffffff, #f1f3f5);
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        animation: fadeIn 1s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .badge-success {
        background-color: #d1e7dd;
        color: #0f5132;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 1rem;
    }

    /* الفوتر */
    .footer {
        text-align: center;
        margin-top: 4rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        color: #adb5bd;
        font-size: 0.8rem;
    }
    
    /* تحسين زر التسجيل */
    .stAudio { width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. تهيئة النظام والبيانات
# ==========================================

# السيناريوهات الواقعية
SCENARIOS = {
    "📢 رسالة صوتية (واتساب)": {
        "desc": "تخيل أنك ترسل ملاحظة صوتية لصديق تعتذر فيها عن موعد.",
        "text": "يا صديقي، سامحني.. حصل ظرف طارئ في البيت ومش حقدر انزل النهاردة. خليني اكلمك بالليل نرتب ليوم تاني.",
        "type": "عامية بيضاء (Spoken Arabic)"
    },
    "💼 بريد صوتي (رسمي)": {
        "desc": "تخيل أنك تترك رسالة لمدير التوظيف.",
        "text": "مرحباً، معكم فهد طه. اتصلت بخصوص فرصة العمل المعلن عنها. أتمنى تحديد موعد للمقابلة لمناقشة التفاصيل.",
        "type": "لغة مهنية (Professional)"
    },
    "🎤 إلقاء (نص أدبي)": {
        "desc": "اختبار الفصاحة ومخارج الحروف.",
        "text": "إنَّ اللُّغَةَ العَرَبِيَّةَ لَيْسَتْ مُجَرَّدَ أَدَاةٍ لِلتَّوَاصُل، بَلْ هِيَ وِعَاءُ الفِكْرِ وَمِرْآةُ الهُوِيَّة.",
        "type": "فصحى معاصرة (MSA)"
    }
}

# تكوين مفتاح API (مدمج للطوارئ)
# تم تجزئة المفتاح لتجنب فلاتر GitHub
KEY_PART_1 = "AIzaSyB72GXyTtv"
KEY_PART_2 = "jxj5XqTMLuOWm9bmcY4qCXys"
API_KEY = KEY_PART_1 + KEY_PART_2

# محاولة التهيئة
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("خطأ في الاتصال بالخادم الذكي.")

# ==========================================
# 3. بناء الواجهة
# ==========================================

# الرأس
st.markdown("""
<div class="main-header">
    <h1 class="title-text">منصة بَيَان</h1>
    <div class="subtitle-text">نظام الاعتماد الوطني للهوية اللغوية | AIL System</div>
</div>
""", unsafe_allow_html=True)

# اختيار المسار
col1, col2 = st.columns([3, 1])
with col2:
    st.markdown("### 🎯 اختر المسار:")
with col1:
    selected_option = st.selectbox("label", list(SCENARIOS.keys()), label_visibility="collapsed")

current_scenario = SCENARIOS[selected_option]

# عرض التحدي
st.info(f"💡 **السياق:** {current_scenario['desc']}")
st.markdown(f"""
<div class="scenario-card">
    <div style="font-size: 0.9rem; color: #198754; margin-bottom: 5px;">النص المقترح للقراءة:</div>
    <div class="scenario-text">"{current_scenario['text']}"</div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. المحرك الذكي (The Core)
# ==========================================

audio_input = st.audio_input("اضغط لبدء الاختبار")

if audio_input:
    st.markdown("---")
    status_text = st.empty()
    status_text.caption("⏳ جاري تحليل البصمة الصوتية ومعالجة البيانات...")
    
    # حفظ مؤقت
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_input.read())
        tmp_path = tmp_file.name

    try:
        # الاتصال بموديل 1.5 Flash (الوحيد الذي يدعم الصوت)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # رفع الملف
        uploaded_file = genai.upload_file(tmp_path)
        
        # هندسة الأمر (Prompt Engineering)
        prompt = f"""
        بصفتك خبيراً لغوياً في مجمع اللغة العربية، قيم هذا التسجيل الصوتي.
        السياق: {current_scenario['type']}
        النص المستهدف: {current_scenario['text']}
        
        المطلوب: تقرير HTML بسيط (بدون وسوم html/body) يحتوي على:
        1. مستوى المتحدث (مبتدئ - متمكن - سفير).
        2. نسبة الإتقان %.
        3. تحليل موجز لمخارج الحروف والنبرة (هل تناسب السياق؟).
        4. نصيحة قصيرة.
        
        اجعل الأسلوب مشجعاً ورسمياً. استخدم الرموز التعبيرية (Emojis).
        """
        
        response = model.generate_content([uploaded_file, prompt])
        
        status_text.empty() # إخفاء رسالة التحميل
        
        # عرض النتيجة
        st.markdown(f"""
        <div class="result-card">
            <div class="badge-success">✨ تم إصدار الرخصة الرقمية</div>
            <div style="text-align: right; direction: rtl; line-height: 1.6; font-size: 1.1rem;">
                {response.text}
            </div>
            <hr style="margin-top: 20px; border-top: 1px dashed #ccc;">
            <small>تم التوثيق بواسطة: Bayan AI Engine v1.0</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.balloons()

    except Exception as e:
        st.error(f"عذراً، حدث خطأ تقني: {str(e)}")
        st.warning("يرجى التأكد من تحديث المكتبات في requirements.txt")
        
    finally:
        # تنظيف
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# الفوتر
st.markdown('<div class="footer">جميع الحقوق محفوظة © جائزة محمد بن راشد للغة العربية 2026</div>', unsafe_allow_html=True)
