# 🎬 D-ID AI Avatar Studio Pro

An advanced, production-ready Streamlit application that integrates with the **D-ID API** to generate photorealistic AI talking avatar videos from any portrait photo using either neural text-to-speech (TTS) or custom voice recordings.

---

## ✨ Features & Capabilities

- **📸 Custom Avatar Upload**: Drag & drop any face photo (JPG/PNG). Automatically uploads to D-ID via `POST /images`.
- **📝 Script-to-Speech (TTS)**:
  - ⚡ **One-Click Script Templates**: Product Pitch, Course Explainer, Welcome Greeting, Motivational Quote.
  - 📊 **Real-time Script Analytics**: Character count, word count, and estimated speech duration.
  - 🌐 **Global Neural Voices**: Curated Azure Neural Voices across 14 languages & accents (US, UK, Australia, India, Spain, Mexico, France, Germany, Italy, Brazil, Japan, China, etc.).
  - 🎭 **Emotional Speaking Styles**: Cheerful, empathetic, excited, friendly, hopeful, whispering, and more.
- **🎙️ Custom Audio & Voiceover Upload**:
  - Upload pre-recorded audio files (`.mp3`, `.wav`, `.m4a`, `.ogg`) or record directly through your microphone using Streamlit's `st.audio_input`.
  - Automatically sends audio to D-ID via `POST /audios` and animates lip-sync matching the custom audio track.
- **💳 Live Account & Credit Checker**: Check your real-time D-ID credit balance, plan tier, and remaining units from the sidebar (`GET /credits`).
- **⚙️ Advanced Animation Controls**: Toggle full-image seamless face stitching (`stitch`) versus close-up face crop.
- **🎞️ Session History & Video Gallery**: Automatically tracks all generated videos in your session so you can review, compare, re-download, or copy links anytime.
- **🔗 Share & Export Suite**: Copy public shareable URLs, direct download MP4s, or copy HTML embed codes.
- **🔒 Seamless Secret Management**: Supports `.env` files locally and `st.secrets` on Streamlit Community Cloud.

---

## 📋 Assignment Steps Covered

| Step | Implementation |
|---|---|
| **Step 1: Select or create a suitable avatar** | Upload any portrait photo with real-time size & preview validation. |
| **Step 2: Add a short script or spoken content** | Custom script editor with built-in templates, duration estimation, or custom audio upload. |
| **Step 3: Configure voice and language** | Multilingual neural voices, dialect selection, and emotional tone control. |
| **Step 4: Generate the AI avatar video** | Submits job to `POST /talks`, real-time status tracker, and progress animation. |
| **Step 5: Review output & copy public link** | Video player, verified public URL code box, download button, and HTML embed snippet. |

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/d-id-avatar-studio.git
cd d-id-avatar-studio
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure your D-ID API Key
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Add your key inside `.env`:
```ini
DID_API_KEY=your_d_id_api_key_here
```
> **Where to get your key**: Log in at [studio.d-id.com](https://studio.d-id.com/) → Click your profile icon → Select **API**.

### 4. Run the Streamlit App
```bash
python -m streamlit run app.py
```
Open **http://localhost:8501** in your browser.

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

1. Push your repository to GitHub (ensure `.env` is ignored by `.gitignore`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a **New app**.
3. Select your repository, branch, and set main file to `app.py`.
4. In **Advanced Settings → Secrets**, paste:
   ```toml
   DID_API_KEY = "your_d_id_api_key_here"
   ```
5. Click **Deploy**. The app will automatically read the secret!

---

## 📁 Project Structure

```
d-id/
├── app.py            # Streamlit application with full feature set
├── requirements.txt  # Dependencies (streamlit, requests, python-dotenv)
├── .env.example      # Template for environment variables
├── .gitignore        # Prevents secrets & cache from entering git
└── README.md         # Documentation & guide
```

---

## 📄 License
MIT
