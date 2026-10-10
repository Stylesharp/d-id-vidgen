import streamlit as st
import requests
import time
import base64
import os
import datetime
from dotenv import load_dotenv

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="D-ID AI Avatar Studio Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS (Safe, adaptive for both Light & Dark modes) ───────────────────
st.markdown("""
<style>
    /* Clean up default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Modern gradient header */
    .hero-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7928CA 0%, #4338CA 50%, #2563EB 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: center;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        opacity: 0.75;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Avatar preview image styling */
    .avatar-preview-box {
        border-radius: 14px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        border: 1px solid rgba(128,128,128,0.2);
        transition: transform 0.2s ease;
    }
    .avatar-preview-box:hover {
        transform: scale(1.01);
    }

    /* Primary Generate Button styling */
    [data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #7928CA 0%, #2563EB 100%) !important;
        border: none !important;
        color: white !important;
        border-radius: 30px !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        padding: 0.65rem 2.2rem !important;
        box-shadow: 0 4px 18px rgba(121, 40, 202, 0.4) !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.3px;
    }
    [data-testid="baseButton-primary"]:hover {
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.5) !important;
    }

    /* Soft modern card containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid rgba(128, 128, 128, 0.18) !important;
        padding: 1.3rem !important;
        background: rgba(128, 128, 128, 0.02) !important;
        transition: box-shadow 0.2s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04) !important;
    }

    /* Badge tags */
    .badge-tag {
        display: inline-block;
        padding: 2px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        border-radius: 20px;
        background: rgba(121, 40, 202, 0.12);
        color: #7928CA;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DID_API_URL = "https://api.d-id.com"

# ── Voice catalog (Microsoft Azure Neural Voices via D-ID) ────────────────────
VOICE_CATALOG = {
    "🇺🇸 English (US)": {
        "Jenny (Female - Warm & Natural)": "en-US-JennyNeural",
        "Guy (Male - Confident & Friendly)": "en-US-GuyNeural",
        "Aria (Female - Expressive)": "en-US-AriaNeural",
        "Davis (Male - Professional)": "en-US-DavisNeural",
    },
    "🇬🇧 English (UK)": {
        "Sonia (Female - Polite & Clear)": "en-GB-SoniaNeural",
        "Ryan (Male - Formal)": "en-GB-RyanNeural",
    },
    "🇦🇺 English (Australia)": {
        "Natasha (Female - Casual)": "en-AU-NatashaNeural",
        "William (Male - Relaxed)": "en-AU-WilliamNeural",
    },
    "🇮🇳 English (India)": {
        "Neerja (Female - Warm)": "en-IN-NeerjaNeural",
        "Prabhat (Male - Clear)": "en-IN-PrabhatNeural",
    },
    "🇪🇸 Spanish (Spain)": {
        "Elvira (Female - Natural)": "es-ES-ElviraNeural",
        "Alvaro (Male - Professional)": "es-ES-AlvaroNeural",
    },
    "🇲🇽 Spanish (Mexico)": {
        "Dalia (Female - Expressive)": "es-MX-DaliaNeural",
        "Jorge (Male - Warm)": "es-MX-JorgeNeural",
    },
    "🇫🇷 French (France)": {
        "Denise (Female - Clear)": "fr-FR-DeniseNeural",
        "Henri (Male - Formal)": "fr-FR-HenriNeural",
    },
    "🇩🇪 German (Germany)": {
        "Katja (Female - Precise)": "de-DE-KatjaNeural",
        "Conrad (Male - Confident)": "de-DE-ConradNeural",
    },
    "🇮🇹 Italian (Italy)": {
        "Elsa (Female - Melodic)": "it-IT-ElsaNeural",
        "Diego (Male - Expressive)": "it-IT-DiegoNeural",
    },
    "🇧🇷 Portuguese (Brazil)": {
        "Francisca (Female - Friendly)": "pt-BR-FranciscaNeural",
        "Antonio (Male - Natural)": "pt-BR-AntonioNeural",
    },
    "🇮🇳 Hindi": {
        "Swara (Female - Clear)": "hi-IN-SwaraNeural",
        "Madhur (Male - Confident)": "hi-IN-MadhurNeural",
    },
    "🇯🇵 Japanese": {
        "Nanami (Female - Soft)": "ja-JP-NanamiNeural",
        "Keita (Male - Polite)": "ja-JP-KeitaNeural",
    },
    "🇨🇳 Chinese (Mandarin)": {
        "Xiaoxiao (Female - Warm)": "zh-CN-XiaoxiaoNeural",
        "Yunxi (Male - Lively)": "zh-CN-YunxiNeural",
    },
    "🇸🇦 Arabic (Saudi Arabia)": {
        "Zariyah (Female - Clear)": "ar-SA-ZariyahNeural",
        "Hamed (Male - Formal)": "ar-SA-HamedNeural",
    },
}

VOICE_STYLE_OPTIONS = [
    "general", "cheerful", "empathetic", "excited",
    "friendly", "hopeful", "sad", "shouting",
    "terrified", "unfriendly", "whispering"
]

# ── Preset Script Templates ───────────────────────────────────────────────────
SCRIPT_TEMPLATES = {
    "✨ Default Demo": (
        "Hello! This is a demonstration of the D-ID AI avatar video generation API. "
        "Using just a portrait photo and spoken audio, D-ID creates a lifelike talking presenter. "
        "Thank you for watching!"
    ),
    "🚀 Product Pitch": (
        "Are you looking for a faster, smarter way to engage your audience? "
        "With AI-generated avatars, you can produce personalized video communications "
        "at scale in minutes, without expensive studio equipment."
    ),
    "👋 Welcome & Onboarding": (
        "Welcome to our platform! We are so glad to have you on board. "
        "Take a look around, explore our interactive features, and don't hesitate "
        "to reach out if you need any assistance along the way."
    ),
    "🎓 Educational Explainer": (
        "Did you know that modern deep learning models can synthesize facial lip synchronization "
        "directly from audio phonemes? This technology brings educational characters "
        "and digital instructors to life in over one hundred languages."
    ),
    "💡 Motivational Quote": (
        "Success is not final, failure is not fatal: it is the courage to continue that counts. "
        "Believe in your potential and make today extraordinary!"
    ),
}

# ── Initialize Session State for Video History ────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def get_configured_api_key() -> str:
    """Read API key from Streamlit Secrets or environment variable with fallback."""
    # 1. Check Streamlit Secrets (for Streamlit Community Cloud)
    try:
        if "DID_API_KEY" in st.secrets and st.secrets["DID_API_KEY"]:
            return st.secrets["DID_API_KEY"]
    except Exception:
        pass
    # 2. Check local environment variable (.env)
    return os.getenv("DID_API_KEY", "")


def build_auth_header(api_key: str, is_multipart: bool = False) -> dict:
    """Format HTTP Basic authentication header reliably for D-ID."""
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


def fetch_account_credits(api_key: str) -> dict | None:
    """Check remaining account credits and status from D-ID GET /credits."""
    headers = build_auth_header(api_key)
    try:
        resp = requests.get(f"{DID_API_URL}/credits", headers=headers, timeout=12)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        st.sidebar.error(f"Failed ({resp.status_code}): {resp.text}")
        return None
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")
        return None


def upload_image(api_key: str, file_bytes: bytes, file_name: str = "avatar.jpg") -> str | None:
    """Upload portrait image file to D-ID POST /images."""
    headers = build_auth_header(api_key, is_multipart=True)
    files = {"image": (file_name, file_bytes, "image/jpeg")}
    try:
        resp = requests.post(f"{DID_API_URL}/images", headers=headers, files=files, timeout=35)
        resp.raise_for_status()
        return resp.json().get("url")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Avatar image upload failed ({resp.status_code}): {resp.text}")
        return None
    except Exception as e:
        st.error(f"❌ Image upload error: {e}")
        return None


def upload_audio(api_key: str, audio_bytes: bytes, audio_name: str = "speech.mp3") -> str | None:
    """Upload custom speech audio file to D-ID POST /audios."""
    headers = build_auth_header(api_key, is_multipart=True)
    mime = "audio/mpeg"
    if audio_name.lower().endswith(".wav"):
        mime = "audio/wav"
    elif audio_name.lower().endswith(".m4a"):
        mime = "audio/m4a"
    elif audio_name.lower().endswith(".ogg"):
        mime = "audio/ogg"

    files = {"audio": (audio_name, audio_bytes, mime)}
    try:
        resp = requests.post(f"{DID_API_URL}/audios", headers=headers, files=files, timeout=45)
        resp.raise_for_status()
        return resp.json().get("url")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Audio file upload failed ({resp.status_code}): {resp.text}")
        return None
    except Exception as e:
        st.error(f"❌ Audio upload error: {e}")
        return None


def create_talk(
    api_key: str,
    source_url: str,
    audio_mode: str,
    script_text: str = "",
    voice_id: str = "",
    voice_style: str = "general",
    audio_url: str = "",
    stitch: bool = True,
    subtitles: bool = False,
) -> dict | None:
    """Submit a video generation job to D-ID POST /talks."""
    headers = build_auth_header(api_key)

    if audio_mode == "audio":
        script_payload = {
            "type": "audio",
            "audio_url": audio_url
        }
    else:
        script_payload = {
            "type": "text",
            "input": script_text,
            "provider": {
                "type": "microsoft",
                "voice_id": voice_id,
                "voice_config": {"style": voice_style},
            },
        }

    config_payload = {
        "fluent": True,
        "pad_audio": 0.0,
        "stitch": stitch,
        "result_format": "mp4"
    }

    payload = {
        "source_url": source_url,
        "script": script_payload,
        "config": config_payload,
    }

    try:
        resp = requests.post(f"{DID_API_URL}/talks", json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ D-ID API Error ({resp.status_code}): {resp.text}")
        return None
    except Exception as e:
        st.error(f"❌ Request failed: {e}")
        return None


def poll_until_done(api_key: str, talk_id: str, max_wait: int = 150, interval: int = 3) -> dict | None:
    """Poll job status until 'done' or 'error'."""
    elapsed = 0
    headers = build_auth_header(api_key)
    progress_bar = st.progress(0, text="⏳ Initializing generation...")

    while elapsed < max_wait:
        try:
            resp = requests.get(f"{DID_API_URL}/talks/{talk_id}", headers=headers, timeout=15)
            resp.raise_for_status()
            result = resp.json()
        except Exception:
            result = None

        if result is None:
            time.sleep(interval)
            elapsed += interval
            continue

        status = result.get("status", "unknown")

        if status == "done":
            progress_bar.progress(100, text="✨ Video rendering complete!")
            time.sleep(0.4)
            progress_bar.empty()
            return result
        elif status in ("error", "rejected"):
            progress_bar.empty()
            st.error(f"❌ Video generation failed: {result.get('error', result)}")
            return None

        pct = min(int((elapsed / max_wait) * 95), 95)
        progress_bar.progress(pct, text=f"🎥 Rendering video... ({status.capitalize()} - {elapsed}s)")
        time.sleep(interval)
        elapsed += interval

    st.error("⏱️ Timed out waiting for the video. Please check your D-ID dashboard.")
    return None


# ─────────────────────────────────────────────────────────────────────────────
# UI Layout
# ─────────────────────────────────────────────────────────────────────────────

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://studio.d-id.com/assets/favicon/apple-touch-icon.png", width=55)
    st.markdown("### ⚙️ D-ID Settings")

    configured_key = get_configured_api_key()
    api_key = st.text_input(
        "API Key",
        value=configured_key,
        type="password",
        help="Get your key from studio.d-id.com → Profile → API. Can also be set in .env or Streamlit Secrets.",
    )

    if configured_key:
        st.caption("🔒 Key auto-loaded from environment / secrets.")

    # Live Credit & Account Checker Button
    if st.button("💳 Check Credits & Plan", use_container_width=True):
        if not api_key:
            st.warning("Please provide an API key first.")
        else:
            with st.spinner("Fetching account balance..."):
                credits_info = fetch_account_credits(api_key)
                if credits_info:
                    st.success("✅ Connected to D-ID API")
                    st.json(credits_info)

    st.markdown("---")
    st.markdown("#### 💡 Best Practices")
    st.markdown("""
    - **Face Photo**: High resolution, front-facing, neutral lighting, mouth closed.
    - **Script Length**: Keep messages under 60 seconds for optimal rendering.
    - **Audio Format**: MP3 or WAV with clear vocal clarity and minimal background noise.
    """)

    st.markdown("---")
    st.caption("D-ID AI Studio Pro · Streamlit Edition")


# --- Main Header ---
st.markdown('<p class="hero-title">🎬 D-ID AI Avatar Studio Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Generate photorealistic talking avatars from any portrait photo using AI voice synthesis or custom audio.</p>', unsafe_allow_html=True)

# --- Two-Column Layout ---
col_left, col_right = st.columns([1, 1.25], gap="large")

# ─────────────────────────────────────────────────────────────────────────────
# Left Column: Step 1 - Presenter Photo
# ─────────────────────────────────────────────────────────────────────────────
with col_left:
    with st.container(border=True):
        st.subheader("1️⃣ Upload Avatar Photo")
        st.caption("Choose any portrait photo of a person's face.")

        uploaded_file = st.file_uploader(
            "Upload face image",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, PNG. Clear, front-facing portraits produce the best animations.",
            label_visibility="collapsed"
        )

        if uploaded_file:
            st.image(uploaded_file, caption=f"Selected: {uploaded_file.name}", use_container_width=True)
            st.caption(f"📏 Size: {round(uploaded_file.size / 1024, 1)} KB")
        else:
            st.info("📸 **Drag & drop a photo here to get started.**\n\nEnsure the face is fully visible with good lighting.")

# ─────────────────────────────────────────────────────────────────────────────
# Right Column: Step 2 & 3 - Audio / Spoken Content Setup
# ─────────────────────────────────────────────────────────────────────────────
with col_right:
    # Audio Mode Selection Tabs
    with st.container(border=True):
        st.subheader("2️⃣ Spoken Content & Voice")

        content_mode = st.radio(
            "Select Audio Input Method:",
            ["📝 Text-to-Speech (TTS)", "🎙️ Custom Audio Upload"],
            horizontal=True
        )

        # ── Mode A: Text-to-Speech (TTS) ──────────────────────────────────────
        if content_mode == "📝 Text-to-Speech (TTS)":
            # Quick Script Templates
            col_t1, col_t2 = st.columns([1.2, 1])
            with col_t1:
                selected_template = st.selectbox(
                    "⚡ Load a Script Template:",
                    list(SCRIPT_TEMPLATES.keys()),
                    index=0
                )
            with col_t2:
                st.write("")
                st.write("")
                load_btn = st.button("Apply Template", use_container_width=True)

            # Keep track of active script in session state
            if "script_content" not in st.session_state or load_btn:
                st.session_state.script_content = SCRIPT_TEMPLATES[selected_template]

            script_text = st.text_area(
                "Enter your spoken script:",
                value=st.session_state.script_content,
                height=150,
                max_chars=1200,
                help="Type the words your avatar will say. Up to 1,200 characters.",
            )
            st.session_state.script_content = script_text

            # Live script metrics
            word_count = len(script_text.split()) if script_text.strip() else 0
            char_count = len(script_text)
            est_duration = round((word_count / 140) * 60)  # ~140 words per minute
            st.caption(f"📊 **{char_count}** characters · **{word_count}** words · Estimated speech: **~{est_duration}s**")

            st.markdown("---")

            # Voice & Language Selection
            st.markdown("##### 🌐 Voice & Language Settings")
            v_col1, v_col2 = st.columns(2)
            with v_col1:
                selected_lang = st.selectbox("Language / Accent", list(VOICE_CATALOG.keys()))
                available_voices = VOICE_CATALOG[selected_lang]
                selected_voice_label = st.selectbox("Voice Talent", list(available_voices.keys()))
                voice_id = available_voices[selected_voice_label]

            with v_col2:
                voice_style = st.selectbox(
                    "Emotional Style",
                    VOICE_STYLE_OPTIONS,
                    index=0,
                    help="Speaking emotion provided by Azure Neural TTS."
                )
                st.info(f"🗣️ Active: **{voice_id}**\n🎭 Tone: **{voice_style.capitalize()}**")

            uploaded_audio_file = None

        # ── Mode B: Custom Audio / Voice Recording ────────────────────────────
        else:
            st.markdown("##### 🎙️ Upload Your Own Speech Audio")
            st.caption("Upload a pre-recorded voiceover file or record your voice.")

            # Check if Streamlit's native microphone recorder is supported
            recorded_audio = None
            if hasattr(st, "audio_input"):
                recorded_audio = st.audio_input("Record voice with microphone:")

            uploaded_audio_file = st.file_uploader(
                "Or upload an audio file (.mp3, .wav, .m4a)",
                type=["mp3", "wav", "m4a", "ogg"],
                help="Make sure audio is clear and isolated from background noise."
            )

            # Prefer recorded audio if present, otherwise uploaded file
            active_audio = recorded_audio if recorded_audio is not None else uploaded_audio_file

            if active_audio:
                st.audio(active_audio)
                st.success(f"✅ Audio file ready: **{active_audio.name if hasattr(active_audio, 'name') else 'Recorded Voice'}**")
            else:
                st.info("👆 Upload or record an audio clip to synchronize your avatar's speech.")

            script_text = ""
            voice_id = ""
            voice_style = "general"

    # ─────────────────────────────────────────────────────────────────────────
    # Advanced Generation Settings Expander
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("⚙️ Advanced Video Controls", expanded=False):
        col_adv1, col_adv2 = st.columns(2)
        with col_adv1:
            stitch_option = st.checkbox(
                "Full Image Stitching (`stitch`)",
                value=True,
                help="When enabled, animates the face seamlessly on the full portrait photo. When disabled, crops tightly to the head."
            )
        with col_adv2:
            custom_title = st.text_input(
                "Video Project Label",
                value="My AI Presenter",
                help="Optional title to identify this video in your history gallery."
            )

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Video Generation Action
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])

with btn_col2:
    generate_btn = st.button("🚀 Generate AI Avatar Video", type="primary", use_container_width=True)

if generate_btn:
    # ── Input Validation ──────────────────────────────────────────────────────
    errors = []
    if not api_key.strip():
        errors.append("Please enter your D-ID API Key in the sidebar.")
    if not uploaded_file:
        errors.append("Please upload a portrait photo for the presenter (Step 1).")

    if content_mode == "📝 Text-to-Speech (TTS)":
        if not script_text.strip():
            errors.append("Please enter a spoken script (Step 2).")
    else:
        active_audio_check = recorded_audio if (hasattr(st, "audio_input") and recorded_audio is not None) else uploaded_audio_file
        if not active_audio_check:
            errors.append("Please upload or record an audio file.")

    if errors:
        for err in errors:
            st.error(f"⚠️ {err}")
        st.stop()

    # ── Execution Pipeline ────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🎬 Video Generation in Progress")

    # Step 1: Upload Image to D-ID
    with st.status("🚀 Processing assets with D-ID...", expanded=True) as status_box:
        st.write("📤 Uploading avatar photo to D-ID cloud...")
        source_url = upload_image(api_key, uploaded_file.getvalue(), uploaded_file.name)
        if not source_url:
            status_box.update(label="❌ Failed to upload avatar image.", state="error")
            st.stop()
        st.write("✅ Avatar photo uploaded successfully.")

        # Step 2: Handle Audio if custom mode
        audio_url = ""
        audio_mode_key = "text"
        if content_mode == "🎙️ Custom Audio Upload":
            audio_mode_key = "audio"
            chosen_audio = recorded_audio if (hasattr(st, "audio_input") and recorded_audio is not None) else uploaded_audio_file
            st.write("🎙️ Uploading custom speech audio to D-ID cloud...")
            audio_url = upload_audio(
                api_key,
                chosen_audio.getvalue(),
                getattr(chosen_audio, "name", "recorded_voice.wav")
            )
            if not audio_url:
                status_box.update(label="❌ Failed to upload audio file.", state="error")
                st.stop()
            st.write("✅ Audio track uploaded successfully.")

        # Step 3: Dispatch Create Talk Job
        st.write("⚙️ Submitting animation job to D-ID renderer...")
        job = create_talk(
            api_key=api_key,
            source_url=source_url,
            audio_mode=audio_mode_key,
            script_text=script_text,
            voice_id=voice_id,
            voice_style=voice_style,
            audio_url=audio_url,
            stitch=stitch_option,
        )

        if not job or not job.get("id"):
            status_box.update(label="❌ Failed to dispatch generation job.", state="error")
            st.stop()

        talk_id = job.get("id")
        st.write(f"✅ Render job created! Talk ID: `{talk_id}`")
        status_box.update(label="🎥 Rendering video on D-ID neural servers...", state="running")

    # Step 4: Poll until rendering finishes
    result = poll_until_done(api_key, talk_id)

    if result and result.get("result_url"):
        video_url = result.get("result_url")

        # Save to session history
        history_entry = {
            "id": talk_id,
            "url": video_url,
            "timestamp": datetime.datetime.now().strftime("%I:%M %p"),
            "title": custom_title.strip() or f"Video #{len(st.session_state.history) + 1}",
            "type": "Custom Audio" if content_mode == "🎙️ Custom Audio Upload" else f"TTS ({voice_id})",
            "preview_text": script_text[:85] + ("..." if len(script_text) > 85 else "") if script_text else "Custom Audio Track"
        }
        st.session_state.history.insert(0, history_entry)

        # ─────────────────────────────────────────────────────────────────────
        # Step 5: Review Output & Shareable Links
        # ─────────────────────────────────────────────────────────────────────
        st.divider()
        st.subheader("🎉 Step 5 · Review Output & Public Share Link")

        with st.container(border=True):
            v_col_out1, v_col_out2 = st.columns([1.3, 1], gap="medium")

            with v_col_out1:
                st.video(video_url)

            with v_col_out2:
                st.markdown("#### 🔗 Shareable Public Project Link")
                st.caption("Copy this URL directly to submit your assignment or share your creation:")
                st.code(video_url, language=None)

                # Action Buttons
                st.link_button("🌐 Open Video in Browser", video_url, use_container_width=True)

                # Download button
                try:
                    with st.spinner("Downloading video for local save..."):
                        video_bytes = requests.get(video_url, timeout=40).content
                        st.download_button(
                            "⬇️ Download Video (MP4)",
                            data=video_bytes,
                            file_name=f"d_id_avatar_{talk_id}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                except Exception:
                    pass

                # Embed Code Snippet
                with st.expander("📋 Copy HTML Embed Code"):
                    embed_code = f'<video width="640" height="360" controls><source src="{video_url}" type="video/mp4"></video>'
                    st.code(embed_code, language="html")

        st.success("✨ Your AI avatar video is ready and verified!")
    else:
        st.error("Video processing failed or timed out. Please check your credit balance or try again.")

# ─────────────────────────────────────────────────────────────────────────────
# Session Gallery: Generation History
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.divider()
    st.subheader(f"🎞️ Video Library & Session History ({len(st.session_state.history)})")
    st.caption("Review all AI avatar videos generated during your current session.")

    for idx, item in enumerate(st.session_state.history):
        with st.expander(f"🎬 {item['title']} · {item['timestamp']} ({item['type']})", expanded=(idx == 0)):
            h_col1, h_col2 = st.columns([1, 1.5])
            with h_col1:
                st.video(item["url"])
            with h_col2:
                st.markdown(f"**Description / Script:** {item['preview_text']}")
                st.markdown(f"**Talk ID:** `{item['id']}`")
                st.markdown("**Public URL:**")
                st.code(item["url"], language=None)
                h_b1, h_b2 = st.columns(2)
                with h_b1:
                    st.link_button("🌐 Open URL", item["url"], use_container_width=True)
                with h_b2:
                    try:
                        v_data = requests.get(item["url"], timeout=30).content
                        st.download_button(
                            "⬇️ Download MP4",
                            data=v_data,
                            file_name=f"{item['title'].replace(' ', '_')}.mp4",
                            mime="video/mp4",
                            key=f"dl_{item['id']}_{idx}",
                            use_container_width=True
                        )
                    except Exception:
                        pass
