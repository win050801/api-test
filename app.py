import streamlit as st
import google.generativeai as genai
import re

# Cấu hình trang
st.set_page_config(page_title="AI Movie Recap Pro", page_icon="🔥", layout="wide")

# --- LẤY API KEY TỪ SECRETS ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    st.error("❌ Không tìm thấy API Key trong Secrets. Hãy thêm 'GEMINI_API_KEY' vào phần Settings -> Secrets trên Streamlit Cloud.")
    st.stop()

def clean_srt(srt_content):
    """Lọc bỏ rác trong file SRT để AI tập trung vào lời thoại"""
    text = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', srt_content)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    return " ".join(text.split())

def generate_content(content, model_name):
    """Gọi Gemini với model được chọn và cấu trúc phản hồi chi tiết"""
    try:
        genai.configure(api_key=api_key)
        # Sử dụng model được truyền vào từ giao diện
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        Bạn là một biên tập viên chuyên tóm tắt phim tu tiên, kiếm hiệp và fantasy cho YouTube.
        Dưới đây là kịch bản (phụ đề) của phim:
        ---
        {content}
        ---
        Dựa trên kịch bản trên, hãy trình bày nội dung theo đúng cấu trúc sau thêm vào những từ ngữ seb tìm kiểm để tăng khả năng tiếp cận người xem:

        1. **TIÊU ĐỀ VIDEO (3 Lựa chọn)**:
           - Đưa lên đầu tiên. Tiêu đề cần kịch tính, chuẩn SEO, chứa từ khóa mạnh dễ tìm kiếm.

        2. **NHÂN VẬT CHÍNH**:
           - Tên nhân vật, biệt danh, vũ khí hoặc linh thú đi kèm (nếu có).

        3. **CHI TIẾT HỆ THỐNG CẢNH GIỚI & SỨC MẠNH**:
           - Phân tích kỹ các cấp bậc sức mạnh xuất hiện hoặc được nhắc đến.
           - Trình bày dạng danh sách có thứ tự từ thấp đến cao (ví dụ: Luyện Khí -> Trúc Cơ -> ...).
           - Ghi chú thêm đặc điểm của mỗi cấp độ nếu kịch bản có nhắc tới.

        4. **MÔ TẢ YOUTUBE (DESCRIPTION)**:
           - Viết một đoạn tóm tắt nội dung kịch tính (200-300 từ) để lôi kéo người xem bấm vào video.

        5. **HASHTAG XU HƯỚNG**:
           - Danh sách các hashtag liên quan.

        Yêu cầu: Văn phong chuyên nghiệp, dùng thuật ngữ phim ảnh chính xác. Nếu không thấy tên nhân vật hoặc cảnh giới rõ ràng, hãy dựa vào ngữ cảnh để suy luận thông minh.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Lỗi: {str(e)}"

# --- GIAO DIỆN NGƯỜI DÙNG ---
st.title("⚡ AI Movie Content Creator")
st.markdown("Hệ thống tự động phân tích cảnh giới và viết mô tả YouTube.")

# --- SIDEBAR: CHỌN MODEL ---
with st.sidebar:
    st.header("Cấu hình Model")
    selected_model = st.selectbox(
        "Chọn phiên bản Gemini:",
        [
            "gemini-2.5-flash-lite",
            "gemini-3-flash-preview" 
            
        ],
        help="Bản 3.1 Flash Lite thường nhanh và tiết kiệm hơn, bản 3 Flash mạnh mẽ hơn trong việc suy luận."
    )
    st.divider()
    st.info("Lưu ý: API Key đã được cấu hình bảo mật trong hệ thống.")

uploaded_file = st.file_uploader("Tải lên file phụ đề (.srt)", type=["srt"])

if uploaded_file:
    # Hiển thị nút bấm
    if st.button("🚀 Bắt đầu phân tích kịch bản"):
        with st.spinner(f"Đang sử dụng {selected_model} để quét kịch bản..."):
            # Xử lý text
            raw_text = uploaded_file.getvalue().decode("utf-8")
            cleaned_text = clean_srt(raw_text)
            
            # Gọi AI với model đã chọn
            result = generate_content(cleaned_text, selected_model)
            
            # Hiển thị kết quả
            st.divider()
            st.markdown(result)
            
            # Nút tải kết quả
            st.download_button(
                label="📥 Tải về bản nháp mô tả",
                data=result,
                file_name="mo_ta_phim.md",
                mime="text/markdown"
            )