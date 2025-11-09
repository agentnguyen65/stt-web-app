import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import time
import os
import json

# Thư viện Google Cloud (Cần được cài đặt qua requirements.txt)
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v3 as translate

# --- Khởi tạo và Xác thực Google Cloud ---

def initialize_google_clients(credentials):
    """Khởi tạo Speech và Translate Client từ khóa JSON"""
    try:
        # Ghi nội dung JSON vào một file tạm thời (Cách chuẩn trong môi trường không tin cậy)
        with open("gcp_credentials.json", "w") as f:
            f.write(credentials)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp_credentials.json"
        
        # Khởi tạo các client
        speech_client = speech.SpeechClient()
        translate_client = translate.TranslationServiceClient()
        
        return speech_client, translate_client
    except Exception as e:
        st.error(f"Lỗi xác thực Google Cloud. Kiểm tra lại khóa JSON: {e}")
        return None, None

# --- LOGIC XỬ LÝ (TỪ BƯỚC 2 - ĐÃ VIẾT LẠI CHO API THỰC) ---

def process_audio_stream(audio_bytes, speech_client, translate_client, project_id, lang_source, lang_target):
    """
    Hàm này mô phỏng việc gửi gói âm thanh đến Google STT và dịch kết quả.
    *LƯU Ý: Đây là logic thời gian thực rất phức tạp, đoạn này chỉ là cấu trúc*
    """
    
    # CẤU HÌNH STT STREAMING (Dành cho việc gọi API thực tế)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16, # Cần khớp với định dạng WebRTC
        sample_rate_hertz=16000, # Tần số mẫu (cần khớp với WebRTC)
        language_code=lang_source,
    )
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True # Trả về kết quả tạm thời (Real-time)
    )

    # --- Gọi STT API ---
    # *Trong ứng dụng thực, audio_bytes sẽ được truyền liên tục*
    # *Vì WebRTC không truyền liên tục dễ dàng trong Streamlit, chúng ta mô phỏng*
    
    # Mô phỏng nhận văn bản gốc từ STT
    text_source = f"[[STT: {time.strftime('%H:%M:%S')}]] Đây là văn bản gốc từ Google STT API."
    
    # --- Gọi Translation API ---
    try:
        parent = f"projects/{project_id}/locations/global"
        response = translate_client.translate_text(
            parent=parent,
            contents=[text_source],
            target_language_code=lang_target,
            source_language_code=lang_source
        )
        text_target = response.translations[0].translated_text
        export_status = "Đã dịch và xuất thành công."
    except Exception as e:
        text_target = f"Lỗi dịch thuật: {e}"
        export_status = "Lỗi trong quá trình dịch."
        
    return text_source, text_target, export_status


# --------------------------------------------------------------------------
# --- CẤU TRÚC GIAO DIỆN STREAMLIT ---
# --------------------------------------------------------------------------

st.set_page_config(page_title="SPG: Dịch Giọng Nói Real-time (Google Cloud)", layout="wide")
st.title("🎙️ Ứng Dụng Dịch Giọng Nói Real-time (Google Cloud API)")

# Khởi tạo trạng thái Micro
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

# --- 1. Xác thực và Thiết lập Đầu vào ---
st.header("1. Xác Thực & Thiết Lập")

# Ô nhập Khóa API
json_key = st.text_area(
    "🔑 Nhập JSON Service Account Key của Google Cloud tại đây:", 
    height=200, 
    key='json_key',
    help="Khóa này chứa thông tin xác thực cho Speech-to-Text và Translation API."
)

if json_key:
    # Lấy Project ID từ khóa JSON (cần thiết cho Translation API)
    try:
        key_data = json.loads(json_key)
        st.session_state.project_id = key_data.get("project_id", "project-id-not-found")
    except json.JSONDecodeError:
        st.error("JSON Key không hợp lệ. Vui lòng kiểm tra lại định dạng JSON.")
        st.session_state.project_id = None
else:
    st.session_state.project_id = None

# Nếu có khóa, khởi tạo Client
speech_client, translate_client = None, None
if st.session_state.project_id:
    speech_client, translate_client = initialize_google_clients(json_key)

if not speech_client or not translate_client:
    st.warning("Vui lòng nhập JSON Key hợp lệ để kích hoạt dịch vụ Google Cloud.")

# Cột thiết lập ngôn ngữ
col1, col2 = st.columns(2)
with col1:
    lang_source = st.selectbox("Ngôn ngữ Gốc (Mã Ngôn ngữ)", ("Tiếng Việt", "Tiếng anh", "Tiếng trung", "Tiếng hàn", "Tiếng nhật"), key='lang_source')
    lang_target = st.selectbox("Ngôn ngữ Dịch (Mã Ngôn ngữ)", ("Tiếng Việt", "Tiếng anh", "Tiếng trung", "Tiếng hàn", "Tiếng nhật"), key='lang_target')

with col2:
    export_mode = st.radio("Chế Độ Xuất Kết Quả", ("Trực Tiếp trên App", "Xuất sang Google Sheet"), key='export_mode', help="Chế độ Xuất Google Sheet chỉ là mô phỏng trong logic hiện tại.")

st.markdown("---")
st.header("2. Kích Hoạt & Kết Quả Dịch Thuật")

# --- Component WebRTC (Chỉ Audio) ---
ctx = webrtc_streamer(
    key="realtime-audio",
    mode=WebRtcMode.SENDONLY,
    media_stream_constraints={"video": False, "audio": True},
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# --- Khung Hiển Thị Kết Quả ---
output_placeholder = st.empty()

if ctx.state.playing and speech_client and translate_client:
    st.session_state.is_running = True
    
    with output_placeholder.container():
        st.success("✅ Micro Đã Hoạt Động & API Đã Kết Nối! Đang Dịch Thời Gian Thực...")
        col_res1, col_res2 = st.columns(2)
        
        # VÒNG LẶP LIÊN TỤC (Sử dụng API thực tế)
        while ctx.state.playing:
            # LƯU Ý QUAN TRỌNG: 
            # Dữ liệu âm thanh thực tế cần được lấy từ ctx.audio_receiver.get_frames()
            # và sau đó được truyền đến Google STT Streaming API.
            
            # TẠM THỜI: Chúng ta gọi hàm process_audio_stream (chỉ là khung sườn)
            # để mô phỏng kết quả API trả về liên tục.
            
            text_source, text_target, export_status = process_audio_stream(
                audio_bytes=None, # Tạm thời bỏ qua audio_bytes
                speech_client=speech_client, 
                translate_client=translate_client,
                project_id=st.session_state.project_id,
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
            
            time.sleep(1) # Giảm tải cho mô phỏng
            st.rerun() 
            
else:
    # Ứng dụng chưa phát (chờ kích hoạt)
    st.session_state.is_running = False
    if not json_key:
        output_placeholder.warning("⚠️ Bước 1: Vui lòng nhập khóa Service Account JSON để xác thực API.")
    elif ctx.state.playing == False:
        output_placeholder.warning("⚠️ Bước 2: Nhấn nút **START** trên component WebRTC phía trên để bắt đầu dịch.")
