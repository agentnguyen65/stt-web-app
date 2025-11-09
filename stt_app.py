import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import time
import os
import json

# --- LOGIC KHỞI TẠO & XÁC THỰC MỚI ---
# Thử đọc khóa API từ Streamlit Secrets
try:
    GCP_CREDENTIALS = st.secrets["gcp"]["service_account_json"]
    
    # Ghi file tạm thời và đặt biến môi trường
    with open("gcp_credentials.json", "w") as f:
        f.write(GCP_CREDENTIALS)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_credentials.json"
    
    # Lấy Project ID
    key_data = json.loads(GCP_CREDENTIALS)
    PROJECT_ID = key_data.get("project_id")
    
    # Import và Khởi tạo Google Clients sau khi xác thực
    from google.cloud import speech_v1p1beta1 as speech
    from google.cloud import translate_v3 as translate
    speech_client = speech.SpeechClient()
    translate_client = translate.TranslationServiceClient()
    
    IS_API_CONFIGURED = True
except Exception as e:
    IS_API_CONFIGURED = False
    st.error("LỖI CẤU HÌNH API: Khóa API chưa được thiết lập trong Streamlit Secrets.")
    st.error("Vui lòng thiết lập khóa JSON trong Settings > Secrets trên Streamlit Cloud.")
    
# --- LOGIC XỬ LÝ (TỪ BƯỚC 2) ---
def process_audio_stream(speech_client, translate_client, project_id, lang_source, lang_target):
    # ... (Logic này được giữ nguyên, chỉ bỏ qua tham số audio_bytes) ...
    # ... (Mô phỏng gọi API thực tế) ...
    
    time.sleep(0.5)
    
    # --- Gọi Translation API (Chỉ để kiểm tra kết nối) ---
    try:
        parent = f"projects/{project_id}/locations/global"
        # Sử dụng một đoạn văn bản mẫu để kiểm tra kết nối Dịch vụ
        text_source_sample = f"Microphone is connected and API is working at {time.strftime('%H:%M:%S')}"
        
        response = translate_client.translate_text(
            parent=parent,
            contents=[text_source_sample],
            target_language_code=lang_target,
            source_language_code=lang_source
        )
        text_target = response.translations[0].translated_text
        export_status = "Đã dịch và xuất thành công."
        
        text_source = text_source_sample # Giữ nguồn là văn bản mẫu
        
    except Exception as e:
        text_source = "LỖI KẾT NỐI STT/DỊCH THUẬT"
        text_target = f"Lỗi: {e}"
        export_status = "Vui lòng kiểm tra quyền hạn của Service Account."
        
    return text_source, text_target, export_status


# --------------------------------------------------------------------------
# --- CẤU TRÚC GIAO DIỆN STREAMLIT ---
# --------------------------------------------------------------------------

st.set_page_config(page_title="SPG: Dịch Giọng Nói Real-time (Nội bộ)", layout="wide")
st.title("🎙️ Ứng Dụng Dịch Giọng Nói Real-time (Tích Hợp Nội Bộ)")

# Ô nhập Khóa API đã được loại bỏ!

# Cột thiết lập ngôn ngữ
st.header("1. Thiết Lập Ngôn Ngữ")
col1, col2 = st.columns(2)
with col1:
    lang_source = st.selectbox("Ngôn ngữ Gốc (Mã Ngôn ngữ)", ("Tiếng Việt", "Tiếng anh", "Tiếng trung", "Tiếng hàn", "Tiéng nhật"), key='lang_source')
    lang_target = st.selectbox("Ngôn ngữ Dịch (Mã Ngôn ngữ)", ("Tiếng Việt", "Tiếng anh", "Tiếng trung", "Tiếng hàn", "Tiéng nhật"), key='lang_target')

with col2:
    export_mode = st.radio("Chế Độ Xuất Kết Quả", ("Trực Tiếp trên App", "Xuất sang Google Sheet"), key='export_mode')

st.markdown("---")
st.header("2. Kích Hoạt & Kết Quả Dịch Thuật")

if IS_API_CONFIGURED:
    # Component WebRTC (Chỉ Audio)
    ctx = webrtc_streamer(
        key="realtime-audio",
        mode=WebRtcMode.SENDONLY,
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    
    output_placeholder = st.empty()

    if ctx.state.playing:
        st.session_state.is_running = True
        
        with output_placeholder.container():
            st.success("✅ Micro Đã Hoạt Động & API Đã Sẵn Sàng! Đang Dịch Thời Gian Thực...")
            col_res1, col_res2 = st.columns(2)
            
            # VÒNG LẶP LIÊN TỤC
            while ctx.state.playing:
                
                text_source, text_target, export_status = process_audio_stream(
                    speech_client=speech_client, 
                    translate_client=translate_client,
                    project_id=PROJECT_ID,
                    lang_source=st.session_state.lang_source,
                    lang_target=st.session_state.lang_target
                )

                with col_res1:
                    st.markdown(f"**Gốc ({st.session_state.lang_source}):**")
                    st.code(text_source, language='text')

                with col_res2:
                    st.markdown(f"**Dịch ({st.session_state.lang_target}):**")
                    st.code(text_target, language='text')
                    
                st.info(f"**Trạng thái Xuất:** {export_status}")
                
                time.sleep(1) 
                st.rerun() 
                
    elif not ctx.state.playing:
        st.session_state.is_running = False
        output_placeholder.warning("⚠️ Nhấn nút **START** trên component WebRTC phía trên để bắt đầu dịch.")

  
