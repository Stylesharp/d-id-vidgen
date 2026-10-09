import streamlit as st
import requests
import time
import base64
import os
from dotenv import load_dotenv

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="D-ID AI Avatar Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS for Premium UI ───────────────────────────────────────────────────
# ── Custom CSS for Premium UI ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Header styling */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: center;
        letter-spacing: -1px;
    }
    .sub-title {
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* Avatar preview image */
    .avatar-preview {
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        border: 2px solid #555;
        transition: transform 0.3s ease;
    }
    .avatar-preview:hover {
        transform: scale(1.02);
    }

    /* The 'Generate' button */
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        padding: 0.75rem 2rem !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    [data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 20px rgba(255, 107, 107, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DID_API_URL = "https://api.d-id.com"

# ── Preset avatars ────────────────────────────────────────────────────────────
AVATAR_OPTIONS = {
    "Amy (Professional)": "https://create-images-results.d-id.com/DefaultPresenters/Amy_f/image.jpeg",
    "Aria (Business)":    "https://create-images-results.d-id.com/DefaultPresenters/Aria_f/image.jpeg",
    "Wade (Casual)":      "https://create-images-results.d-id.com/DefaultPresenters/Wade_m/image.jpeg",
    "Matias (Formal)":    "https://create-images-results.d-id.com/DefaultPresenters/Matias_m/image.jpeg",
    "Upload Image...":    "__upload__",
    "Custom URL...":      "__custom__",
}

# ── Voice options ─────────────────────────────────────────────────────────────
VOICE_OPTIONS = {
    "Jenny (US Female)":    "en-US-JennyNeural",
    "Guy (US Male)":        "en-US-GuyNeural",
    "Emma (UK Female)":     "en-GB-SoniaNeural",
    "Ryan (UK Male)":       "en-GB-RyanNeural",
    "Natasha (AU Female)":  "en-AU-NatashaNeural",
    "Priya (IN Female)":    "en-IN-NeerjaNeural",
}

VOICE_STYLE_OPTIONS = ["general", "cheerful", "empathetic", "excited",
                       "friendly", "hopeful", "sad", "shouting",
                       "terrified", "unfriendly", "whispering"]

DEFAULT_SCRIPT = (
    "Hello! This is a demonstration of the D-ID AI avatar video generation API. "
    "Using just a photo and a script, D-ID creates a realistic talking avatar video. "
    "Isn't that amazing? Thank you for watching!"
)

# ─────────────────────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────────────────────

def build_auth_header(api_key: str, is_multipart: bool = False) -> dict:
    """D-ID uses Basic auth. Handle both raw 'id:secret' and already-encoded keys."""
    api_key = api_key.strip()
    if api_key.lower().startswith("basic "):
        api_key = api_key[6:].strip()
        
    if ":" in api_key:
        token = base64.b64encode(api_key.encode()).decode()
    else:
        token = api_key
        
    headers = {"Authorization": f"Basic {token}"}
    if not is_multipart:
        headers["Content-Type"] = "application/json"
    return headers

def upload_image(api_key: str, file_bytes: bytes, file_name: str = "avatar.jpg") -> str | None:
    """POST /images — upload a local file to get a D-ID source_url."""
    headers = build_auth_header(api_key, is_multipart=True)
    # Using 'image' as the field name as per D-ID docs
    files = {"image": (file_name, file_bytes, "image/jpeg")}
    try:
        resp = requests.post(f"{DID_API_URL}/images", headers=headers, files=files, timeout=30)
        resp.raise_for_status()
        return resp.json().get("url")
    except Exception as e:
        st.error(f"❌ Image upload failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
             st.error(e.response.text)
        return None

def create_talk(api_key: str, source_url: str, script_text: str,
                voice_id: str, voice_style: str) -> dict | None:
    """POST /talks — submit a new video generation job."""
    headers = build_auth_header(api_key)
    payload = {
        "source_url": source_url,
        "script": {
            "type": "text",
            "input": script_text,
            "provider": {
                "type": "microsoft",
                "voice_id": voice_id,
                "voice_config": {"style": voice_style},
            },
        },
        "config": {"fluent": True, "pad_audio": 0.0},
    }
    try:
        resp = requests.post(f"{DID_API_URL}/talks", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API Error {resp.status_code}: {resp.text}")
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

def get_talk_status(api_key: str, talk_id: str) -> dict | None:
    """GET /talks/{id} — poll the job until it's done."""
    headers = build_auth_header(api_key)
    try:
        resp = requests.get(f"{DID_API_URL}/talks/{talk_id}", headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None

def poll_until_done(api_key: str, talk_id: str, max_wait: int = 120, interval: int = 3) -> dict | None:
    elapsed = 0
    progress_bar = st.progress(0, text="⏳ Initializing generation...")
    
    while elapsed < max_wait:
        result = get_talk_status(api_key, talk_id)
        if result is None: return None

        status = result.get("status", "unknown")
        
        if status == "done":
            progress_bar.progress(100, text="✨ Video rendering complete!")
            time.sleep(0.5)
            progress_bar.empty()
            return result
        elif status in ("error", "rejected"):
            progress_bar.empty()
            st.error(f"❌ Generation failed: {result.get('error', result)}")
            return None

        pct = min(int((elapsed / max_wait) * 95), 95)
        progress_bar.progress(pct, text=f"🎥 Rendering video... ({status.capitalize()})")
        time.sleep(interval)
        elapsed += interval

    st.error("⏱️ Timed out waiting for the video. Please check the D-ID dashboard.")
    return None

# ─────────────────────────────────────────────────────────────────────────────
# UI Layout
# ─────────────────────────────────────────────────────────────────────────────

# --- Sidebar ---
with st.sidebar:
    st.image("https://studio.d-id.com/assets/favicon/apple-touch-icon.png", width=60)
    st.markdown("### ⚙️ Settings")
    
    default_key = os.getenv("DID_API_KEY", "")
    api_key = st.text_input(
        "D-ID API Key",
        value=default_key,
        type="password",
        help="Paste your API key from studio.d-id.com",
    )
    
    st.markdown("---")
    st.markdown("#### 💡 Tips")
    st.info("- Keep scripts under 60 seconds\n- Use high-quality portrait photos\n- Test voices before generating")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("Powered by [D-ID API](https://docs.d-id.com/)")


# --- Main Content ---
st.markdown('<p class="main-title">✨ D-ID AI Avatar Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Create lifelike AI presenter videos in seconds.</p>', unsafe_allow_html=True)

# Layout: Two main columns
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    with st.container(border=True):
        st.subheader("1️⃣ Select Presenter")
        avatar_choice = st.selectbox("Choose a face", list(AVATAR_OPTIONS.keys()), label_visibility="collapsed")
        
        source_url = None
        uploaded_file = None
        
        if AVATAR_OPTIONS[avatar_choice] == "__custom__":
            source_url = st.text_input("🔗 Custom Image URL", placeholder="https://example.com/face.jpg", help="Must be publicly accessible (e.g. Imgur, AWS S3). Wikipedia links block automated bots.")
            if source_url:
                st.image(source_url, use_container_width=True)
        elif AVATAR_OPTIONS[avatar_choice] == "__upload__":
            uploaded_file = st.file_uploader("Upload a face image", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                st.image(uploaded_file, use_container_width=True)
        else:
            source_url = AVATAR_OPTIONS[avatar_choice]
            # Nice display for the preset avatar
            st.markdown(f'<img src="{source_url}" class="avatar-preview" style="width:100%; object-fit:cover; max-height: 350px;">', unsafe_allow_html=True)

with col_right:
    with st.container(border=True):
        st.subheader("2️⃣ Write Script")
        script_text = st.text_area(
            "What should the avatar say?",
            value=DEFAULT_SCRIPT,
            height=180,
            label_visibility="collapsed"
        )
        st.caption(f"Length: {len(script_text)} characters (Max: 1000)")

    with st.container(border=True):
        st.subheader("3️⃣ Voice Configuration")
        c1, c2 = st.columns(2)
        with c1:
            voice_label = st.selectbox("🎙️ Voice", list(VOICE_OPTIONS.keys()))
            voice_id    = VOICE_OPTIONS[voice_label]
        with c2:
            voice_style = st.selectbox("🎭 Emotion / Style", VOICE_STYLE_OPTIONS, index=0)

# --- Generate Action ---
st.markdown("<br>", unsafe_allow_html=True)
c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])

with c_btn2:
    generate_btn = st.button("🚀 Generate AI Video", type="primary", use_container_width=True)

# --- Output Section ---
if generate_btn:
    if not api_key:
        st.error("⚠️ Please provide your D-ID API Key in the sidebar.")
        st.stop()
        
    if AVATAR_OPTIONS[avatar_choice] == "__upload__":
        if not uploaded_file:
            st.error("⚠️ Please upload an image file.")
            st.stop()
    elif not source_url:
        st.error("⚠️ Please select an avatar or provide a custom URL.")
        st.stop()
        
    if not script_text.strip():
        st.error("⚠️ Script cannot be empty.")
        st.stop()

    st.markdown("---")
    st.subheader("🎬 Your Video")
    
    with st.spinner("🚀 Submitting request to D-ID API..."):
        # Handle file upload first if needed
        if AVATAR_OPTIONS[avatar_choice] == "__upload__":
            source_url = upload_image(api_key, uploaded_file.getvalue(), uploaded_file.name)
            if not source_url:
                st.stop()
                
        job = create_talk(api_key, source_url, script_text, voice_id, voice_style)

    if job and job.get("id"):
        talk_id = job.get("id")
        
        result = poll_until_done(api_key, talk_id)
        
        if result and result.get("result_url"):
            video_url = result.get("result_url")
            
            # Display result inside a nice card
            with st.container(border=True):
                st.video(video_url)
                
                st.markdown("### 🔗 Share Link")
                st.code(video_url, language=None)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.link_button("🌐 Open in new tab", video_url, use_container_width=True)
                with col_b:
                    try:
                        video_bytes = requests.get(video_url).content
                        st.download_button(
                            "⬇️ Download MP4",
                            data=video_bytes,
                            file_name="d-id-avatar.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )
                    except:
                        pass
            
            st.success("🎉 Video generated successfully!")
        else:
            st.warning("Job finished, but no URL was returned. Please check your D-ID dashboard.")
