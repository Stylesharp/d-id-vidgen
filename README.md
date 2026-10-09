# 🎬 D-ID AI Avatar Video Generator

A Streamlit web app that uses the **D-ID API** to create realistic AI talking-avatar videos in five guided steps — matching the assignment requirements exactly.

## 📋 Assignment Steps Covered

| Step | What the app does |
|------|-------------------|
| 1 | Select or create a suitable avatar (presets or custom URL) |
| 2 | Add a short script or suitable spoken content |
| 3 | Configure voice and language settings (14 voices, 11 styles) |
| 4 | Generate the AI avatar video via the D-ID API |
| 5 | Review the output and copy the shareable video URL |

---

## 🚀 Quick Start (Local)

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/d-id-avatar-generator.git
cd d-id-avatar-generator
```

### 2. Create a virtual environment and install dependencies
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Set your D-ID API key
Copy the example env file and add your key:
```bash
cp .env.example .env
```
Then open `.env` and replace `your_d_id_api_key_here` with your actual key.

> **Where to get the key:** Log in to [D-ID Studio](https://studio.d-id.com/) → click your profile picture → **API**.

### 4. Run the app
```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**.

---

## ☁️ Deploy on Streamlit Community Cloud (free)

1. Push this repo to GitHub (make sure `.env` is in `.gitignore` — it already is).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select your repo and set the **Main file path** to `app.py`.
4. Open **Advanced settings → Secrets** and add:
   ```toml
   DID_API_KEY = "your_d_id_api_key_here"
   ```
5. Click **Deploy**. Done!

> **Note:** Streamlit Cloud reads `st.secrets` automatically from the Secrets panel, but `python-dotenv` also works locally via the `.env` file.

---

## 📁 Project Structure

```
d-id/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
├── .env.example      # Template — copy to .env and fill in your key
├── .gitignore        # Keeps secrets and cache out of git
└── README.md         # This file
```

---

## 🔑 D-ID API Details

| Item | Value |
|------|-------|
| Base URL | `https://api.d-id.com` |
| Auth | HTTP Basic — API key Base64-encoded |
| Create video | `POST /talks` |
| Poll status | `GET /talks/{id}` |
| TTS provider | Microsoft Azure Neural Voices |

---

## ⚠️ Important Notes

- Keep your `.env` file **secret** — never push it to GitHub.
- D-ID free accounts have a limited credit balance. Each video costs a few credits.
- Generation typically takes **15–60 seconds** depending on script length.

---

## 📄 License

MIT
