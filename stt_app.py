from streamlit_audiorecorder import st_audiorecorder
import streamlit as st

# ----------------- Cấu hình Giao diện -----------------
st.set_page_config(page_title="SPG: Ứng dụng Chuyển Giọng Nói (STT)", layout="wide")
st.title("🎤 Ứng dụng Chuyển Giọng Nói Thành Văn Bản (STT)")
st.markdown("Sử dụng Quy trình STT đã thiết lập để chuyển đổi giọng nói.")

# ----------------- Vùng Điều khiển Input (Sidebar) -----------------
with st.sidebar:
    st.header("⚙️ Thiết Lập Tham Số STT")
    
    # INPUT 1: Chế độ Xuất
    export_mode = st.radio(
        "1. Chế độ Xuất Kết Quả",
        ('Trực tiếp', 'Google Sheet'),
        index=0,
        help="Chọn nơi bạn muốn văn bản được xuất ra."
    )
    
    # INPUT 2: Ngôn ngữ Mục tiêu
    target_language = st.selectbox(
        "2. Ngôn ngữ Mục tiêu",
        ('Tiếng Việt', 'Tiếng Anh', 'Tiếng Pháp', 'Khác...'),
        index=0
    )

    # INPUT 3: Điều kiện Xuất bản
    publish_condition = st.text_input(
        "3. Điều kiện Xuất bản (VD: Sau mỗi 3 dòng)",
        value="Hết câu logic hoặc sau 10 giây im lặng"
    )
    
    # INPUT 4: Điều kiện Dừng
    stop_condition = st.text_input(
        "4. Điều kiện Dừng (VD: Người dùng nói 'Dừng')",
        value="Người dùng nhấn nút Dừng hoặc nói từ khóa 'Kết thúc'"
    )

# ----------------- Vùng Nhập Audio Chính (CHỈ MIC) -----------------
st.header("🗣️ Nguồn Âm Thanh Đầu Vào (Ghi Âm Trực Tiếp)")
st.info("Nhấn **'Record'** bên dưới để kích hoạt Mic và ghi lại giọng nói của bạn.")

# Sử dụng component chuyên biệt để ghi âm
wav_audio_data = st_audiorecorder()

# Thao tác: Kiểm tra xem người dùng đã ghi âm xong chưa
audio_source_input = None
if wav_audio_data is not None:
    # Nếu có dữ liệu, hiển thị trình phát lại và xác nhận đã ghi âm
    st.audio(wav_audio_data, format='audio/wav')
    st.success("✅ Ghi âm hoàn tất! Dữ liệu Audio đã sẵn sàng.")
    # Cần dữ liệu bytes để xử lý STT thực tế
    audio_source_input = wav_audio_data
    
# ----------------- Nút Thực thi -----------------
if st.button('✨ Tạo Kết Quả Chuyển Đổi', type="primary"):
    if audio_source_input is not None:
        # Chuẩn bị dữ liệu đầu vào cho API
        input_data = {
            'audio_source': "Mic Data", # Chỉ dùng để minh họa trong placeholder
            'export_mode': export_mode,
            'target_language': target_language,
            'publish_condition': publish_condition,
            'stop_condition': stop_condition,
        }
        
        # Gọi hàm xử lý (mô phỏng)
        with st.spinner('Đang xử lý và chuyển đổi giọng nói...'):
            # result = generate_stt_result(input_data, wav_audio_data) # Dùng trong môi trường thực
            # Mô phỏng kết quả:
            result = {
                "transcribed_text": "Đây là văn bản được chuyển đổi **trực tiếp từ mic của bạn**, dựa trên: Ngôn ngữ [" + target_language + "], Xuất bản [" + publish_condition + "]. Chế độ File Uploader đã bị loại bỏ.",
                "export_mode_used": export_mode
            }

        # ----------------- Vùng Hiển thị Kết quả -----------------
        st.divider()
        st.subheader("✅ Văn Bản Đã Chuyển Đổi Hoàn Chỉnh (OUTPUT)")
        st.text_area(
            "Văn bản", 
            result["transcribed_text"], 
            height=300
        )
        st.success(f"Chế độ xuất: **{result['export_mode_used']}**")
    else:
        # Dòng này đã được sửa lỗi cú pháp
        st.warning("Vui lòng ghi âm giọng nói trước khi nhấn nút Tạo Kết Quả.")


