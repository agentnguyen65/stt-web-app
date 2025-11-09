import streamlit as st
import time

# --- LOGIC API (ĐÃ CẬP NHẬT CHO CHẾ ĐỘ LIÊN TỤC) ---
# ... (Hàm generate_response như đã cập nhật ở trên) ...
def generate_response(input_data):
    # *Hàm này mô phỏng việc xử lý một đoạn âm thanh ngắn*
    time.sleep(0.5) # Giảm thời gian chờ để mô phỏng tính thời gian thực
    
    source_audio_type = input_data.get("Nguồn Âm thanh")
    export_mode = input_data.get("Chế độ Xuất ra")
    lang_source = input_data.get("Ngôn ngữ Gốc")
    lang_target = input_data.get("Ngôn ngữ Dịch")
    
    current_time = time.strftime("%H:%M:%S")
    
    text_source = f"[[Phiên: {current_time}]] {lang_source} đang được ghi lại liên tục." 
    text_target = f"[[Session: {current_time}]] {lang_target} is being translated continuously."
    
    if export_mode == "Google Sheet":
        export_status = f"Đã ghi song ngữ vào Google Sheet. (Đang chờ đoạn ghi tiếp theo...)"
    else: 
        export_status = "Hiển thị trực tiếp (Real-time Display)."

    result = {
        "Văn bản Ngôn ngữ Gốc": text_source,
        "Văn bản Đã Dịch": text_target,
        "Trạng thái Xuất": export_status
    }
    return result
# ----------------------------------------------------

st.set_page_config(page_title="SPG: Chuyển Đổi & Dịch Giọng Nói", layout="wide")

st.title("🎙️ Ứng Dụng Chuyển Đổi & Dịch Giọng Nói (Real-time)")

# Khởi tạo trạng thái phiên (session state)
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# --- Ô Nhập Thông tin (INPUT_SCHEMA) ---
st.header("1. Thiết Lập Đầu Vào")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Cài Đặt Ngôn Ngữ")
    # Các input đã được chuyển sang Session State để duy trì giá trị trong vòng lặp
    lang_source = st.selectbox("Ngôn ngữ Gốc (Đang Nghe)", ("Tiếng Việt", "Tiếng Anh", "Tiếng trung", "Tiếng hàn", "Tiếng nhật"), index=0, key='lang_source', disabled=st.session_state.is_running)
    lang_target = st.selectbox("Ngôn ngữ Dịch (Đích)", ("Tiếng Anh", "Tiếng Việt", "Tiếng trung", "Tiếng hàn", "Tiếng nhật"), index=0, key='lang_target', disabled=st.session_state.is_running)

with col2:
    st.subheader("Nguồn & Chế Độ")
    source_audio_type = st.radio("Nguồn Âm Thanh", ("Mở Micro Trực Tiếp", "Tải Lên Tệp Âm Thanh (.mp3, .wav)"), key='audio_source', disabled=st.session_state.is_running)
    export_mode = st.radio("Chế Độ Xuất Kết Quả", ("Trực Tiếp trên App", "Xuất sang Google Sheet"), key='export_mode', disabled=st.session_state.is_running)


# --- Điều khiển START/STOP ---
st.markdown("---")
col_control_1, col_control_2 = st.columns([1, 4])

with col_control_1:
    if st.button("🔴 START RECORDING", type="primary", disabled=st.session_state.is_running):
        st.session_state.is_running = True
        st.rerun() # ✅ ĐÃ SỬA LỖI

    if st.button("⬛ STOP RECORDING", type="secondary", disabled=not st.session_state.is_running):
        st.session_state.is_running = False
        st.success("⏸️ Đã Dừng Phiên Ghi Âm. Kết quả cuối cùng được hiển thị bên dưới.")
        # Sau khi dừng, không cần rerun ngay, vòng lặp sẽ tự thoát

# --- Khung Hiển Thị Kết Quả (OUTPUT_SCHEMA) ---
st.header("2. Kết Quả Dịch Thời Gian Thực")
output_placeholder = st.empty() # Container để cập nhật liên tục

if st.session_state.is_running:
    # Ứng dụng đang chạy -> Bắt đầu vòng lặp thời gian thực
    with output_placeholder.container():
        st.warning("Đang nghe và dịch liên tục... Nhấn STOP để dừng.")
        col_res1, col_res2 = st.columns(2)
        
        input_data = {
            "Nguồn Âm thanh": st.session_state.audio_source,
            "Chế độ Xuất ra": st.session_state.export_mode,
            "Ngôn ngữ Gốc": st.session_state.lang_source,
            "Ngôn ngữ Dịch": st.session_state.lang_target
        }

        # VÒNG LẶP LIÊN TỤC (Tới khi người dùng bấm STOP)
        while st.session_state.is_running:
            results = generate_response(input_data)

            with col_res1:
                st.subheader(f"1. Văn bản Gốc ({st.session_state.lang_source})")
                st.code(results["Văn bản Ngôn ngữ Gốc"], language='text')

            with col_res2:
                st.subheader(f"2. Văn bản Dịch ({st.session_state.lang_target})")
                st.code(results["Văn bản Đã Dịch"], language='text')
                
            st.info(f"**Trạng thái Xuất:** {results['Trạng thái Xuất']}")
            
            # Cập nhật UI và lặp lại
            time.sleep(0.5) # Độ trễ cho mô phỏng real-time
            st.rerun() # ✅ ĐÃ SỬA LỖI

# Hiển thị thông báo khi ứng dụng không chạy
if not st.session_state.is_running:
    output_placeholder.info("Nhấn START RECORDING để bắt đầu phiên dịch thời gian thực mới.")

