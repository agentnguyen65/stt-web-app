import streamlit as st
import time

# --- LOGIC API (Từ BƯỚC 2) ---
def generate_response(input_data):
    # Mô phỏng quá trình xử lý giọng nói, dịch thuật và xuất dữ liệu
    time.sleep(1) # Tăng trải nghiệm thực tế
    
    source_audio_type = input_data.get("Nguồn Âm thanh")
    export_mode = input_data.get("Chế độ Xuất ra")
    lang_source = input_data.get("Ngôn ngữ Gốc")
    lang_target = input_data.get("Ngôn ngữ Dịch")

    # MÔ PHỎNG KẾT QUẢ ĐẦU RA SAU KHI XỬ LÝ
    text_source = f"Xin chào, tôi là một người máy, đang nói bằng {lang_source}."
    text_target = f"Hello, I am a robot, speaking in {lang_target}."
    
    if export_mode == "Google Sheet":
        export_status = f"Đã ghi song ngữ vào Google Sheet. Gốc: {lang_source}, Dịch: {lang_target}"
    else:
        export_status = "Hiển thị trực tiếp (Direct Display)."

    result = {
        "Văn bản Ngôn ngữ Gốc": text_source,
        "Văn bản Đã Dịch": text_target,
        "Trạng thái Xuất": export_status
    }
    return result
# -------------------------------

st.set_page_config(page_title="SPG: Chuyển Đổi & Dịch Giọng Nói", layout="wide")

st.title("🎙️ Ứng Dụng Chuyển Đổi & Dịch Giọng Nói (Real-time)")

# --- Ô Nhập Thông tin (INPUT_SCHEMA) ---
st.header("1. Thiết Lập Đầu Vào")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Cài Đặt Ngôn Ngữ")
    # Ngôn ngữ Gốc
    lang_source = st.selectbox(
        "Ngôn ngữ Gốc (Đang Nghe)",
        ("Tiếng Việt", "English", "日本語"), 
        index=0,
        key='lang_source'
    )
    # Ngôn ngữ Dịch
    lang_target = st.selectbox(
        "Ngôn ngữ Dịch (Đích)",
        ("English", "Tiếng Việt", "日本語"),
        index=0,
        key='lang_target'
    )

with col2:
    st.subheader("Nguồn & Chế Độ")
    # Nguồn Âm thanh
    source_audio_type = st.radio(
        "Nguồn Âm Thanh",
        ("Mở Micro Trực Tiếp", "Tải Lên Tệp Âm Thanh (.mp3, .wav)"),
        key='audio_source'
    )
    # Chế độ Xuất ra
    export_mode = st.radio(
        "Chế Độ Xuất Kết Quả",
        ("Trực Tiếp trên App", "Xuất sang Google Sheet"),
        key='export_mode'
    )

# --- Nút “Tạo kết quả” ---
st.markdown("---")
if st.button("▶️ BẮT ĐẦU CHUYỂN ĐỔI (START CONVERSION)", type="primary"):
    
    # Chuẩn bị dữ liệu cho API
    input_data = {
        "Nguồn Âm thanh": source_audio_type,
        "Chế độ Xuất ra": export_mode,
        "Ngôn ngữ Gốc": lang_source,
        "Ngôn ngữ Dịch": lang_target
    }
    
    with st.spinner('Đang kết nối và xử lý...'):
        # Gọi API Logic
        results = generate_response(input_data)
    
    # --- Khung Hiển Thị Kết Quả (OUTPUT_SCHEMA) ---
    st.success("✅ Đã Hoàn Thành Xử Lý!")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.subheader(f"1. Văn bản Gốc ({lang_source})")
        st.code(results["Văn bản Ngôn ngữ Gốc"], language='text')

    with col_res2:
        st.subheader(f"2. Văn bản Dịch ({lang_target})")
        st.code(results["Văn bản Đã Dịch"], language='text')
        
    st.info(f"**Trạng thái Xuất:** {results['Trạng thái Xuất']}")



