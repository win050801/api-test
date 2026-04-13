import streamlit as st
import google.generativeai as genai
import re

# Cấu hình trang
st.set_page_config(page_title="Gemini 3.1 Auto-Recap", page_icon="⚡")

# --- LẤY API KEY TỪ SECRETS ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("❌ Không tìm thấy API Key trong Secrets. Vui lòng cấu hình trên Streamlit Cloud!")
    st.stop()

def clean_srt(srt_content):
    """Xử lý file SRT: Bỏ số thứ tự và mốc thời gian"""
    text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', srt_content)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    return " ".join(text.split())

def generate_content(content):
    """Sử dụng Gemini 3.1 Flash Lite Preview"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")
        
        prompt = f"""
        Bạn là một chuyên gia Review Phim. Dựa vào nội dung file SRT sau:
        ---
        {content}
        ---
        Hãy trích xuất và viết nội dung sau bằng tiếng Việt:
        1. Tên nhân vật chính:
        2. Hệ thống cảnh giới/sức mạnh (nếu có):
        3. Tiêu đề YouTube (3 mẫu):
        4. Mô tả phim kịch tính (để đăng YouTube):
        5. Hashtag:
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- GIAO DIỆN ---
st.title("🎬 AI Movie Recap (Auto-Key)")
uploaded_file = st.file_uploader("Tải file SRT lên", type=["srt"])

if uploaded_file:
    if st.button("🚀 Chạy phân tích ngay"):
        with st.spinner("Đang xử lý..."):
            content = uploaded_file.getvalue().decode("utf-8")
            cleaned_text = clean_srt(content)
            result = generate_content(cleaned_text)
            st.markdown("### ✨ Kết quả:")
            st.write(result)