import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import time

# --- LOGIC API (TỪ BƯỚC 2) ---
def generate_response(lang_source, lang_target, export_mode):
    # Hàm mô phỏng real-time
    import time
    time.sleep(0.5) 
    
    current_time = time.strftime("%H:%M:%S")
    
    text_source = f"[[Phiên: {current_time}]] {lang_source} đang được ghi lại liên tục từ Micro." 
    text_target = f"[[Session: {current_time}]] {lang_target} đã dịch đoạn vừa rồi."
    
    if export_mode == "Google Sheet":
        export_status = f"Đã ghi vào Google Sheet. (Micro đang hoạt động...)"
    else: 
        export_status = "Hiển thị trực tiếp (Real-time Display)."

    return text_source, text_target, export_status
# ----------------------------------------------------

st.set_page_config(page_title="SPG: Chuyển Đổi & Dịch Giọng Nói (Micro Real-time)", layout="wide")
st.title("🎙️ Ứng Dụng Chuyển Đổi & Dịch Giọng Nói (Chế Độ Micro Real-time)")

# Khởi tạo trạng thái Micro
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# --- 1. Thiết Lập Đầu Vào ---
st.header("1. Thiết Lập Đầu Vào")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cài Đặt Ngôn Ngữ")
    lang_source = st.selectbox("Ngôn ngữ Gốc (Đang Nghe)", ("Tiếng Việt", "Tiếng anh", "Tiếng trung", "Tiếng hàn", "Tiếng nhật"), key='lang_source')
    lang_target = st.selectbox("Ngôn ngữ Dịch (Đích)", ("Tiếng Việt", "Tiếng anh", "Tiếng trung", "Tiếng hàn", "Tiếng nhật"), key='lang_target')

with col2:
    st.subheader("Chế Độ Xuất")
    export_mode = st.radio("Chế Độ Xuất Kết Quả", ("Trực Tiếp trên App", "Xuất sang Google Sheet"), key='export_mode')

st.markdown("---")
st.header("2. Kích Hoạt Microphone & Dịch Thuật")

# --- Component WebRTC (Chỉ Audio) ---
# Tùy chọn chính: media_stream_constraints={"video": False, "audio": True}
ctx = webrtc_streamer(
    key="realtime-audio",
    mode=WebRtcMode.SENDONLY, # Chỉ gửi dữ liệu từ trình duyệt (Micro) lên server
    video_processor_factory=None, 
    audio_processor_factory=None,
    media_stream_constraints={"video": False, "audio": True}, # Yêu cầu chỉ Audio
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }
)

# Sử dụng trạng thái WebRTC để bắt đầu vòng lặp Real-time
if ctx.state.playing:
    # Set trạng thái chạy khi Micro được bật thành công
    st.session_state.is_running = True

# --- Khung Hiển Thị Kết Quả (OUTPUT_SCHEMA) ---
output_placeholder = st.empty()

if st.session_state.is_running:
    # Ứng dụng đang chạy -> Bắt đầu vòng lặp thời gian thực
    with output_placeholder.container():
        st.success("✅ Micro Đã Hoạt Động! Đang Dịch Thời Gian Thực...")
        col_res1, col_res2 = st.columns(2)
        
        # VÒNG LẶP LIÊN TỤC (Tới khi người dùng tự tắt Micro trên component)
        while ctx.state.playing:
            # Gọi hàm logic API
            text_source, text_target, export_status = generate_response(
                lang_source=st.session_state.lang_source,
                lang_target=st.session_state.lang_target,
                export_mode=st.session_state.export_mode
            )

            with col_res1:
                st.markdown(f"**Gốc ({st.session_state.lang_source}):**")
                st.code(text_source, language='text')

            with col_res2:
                st.markdown(f"**Dịch ({st.session_state.lang_target}):**")
                st.code(text_target, language='text')
                
            st.info(f"**Trạng thái Xuất:** {export_status}")
            
            time.sleep(1) # Giảm tải cho mô phỏng
            # Buộc cập nhật UI để mô phỏng tính liên tục
            st.rerun() 

else:
    # Ứng dụng chưa phát (chờ kích hoạt)
    output_placeholder.warning("⚠️ Nhấn nút **START** trên component WebRTC phía trên để cấp quyền Microphone và bắt đầu dịch thời gian thực.")
    st.session_state.is_running = False
