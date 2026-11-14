# Clear-Text ("Ясный Текст")

> 🌐 **Language:** **English** | [Русский (README_Ru.md)](README_Ru.md)

An AI accessibility Telegram bot designed for visually impaired and elderly users who struggle to read fine print on medicine boxes, medical leaflets, or utility receipts.

## ✨ Features
- 📸 **Photo Recognition & Simplification** — uses the multimodal **Google Gemini** model to analyze photos of packaging, prescriptions, and documents.
- 🚨 **Built-in SOS Hazard Detector** — automatically scans leaflets and packaging for critical warnings (expired dates, strict contraindications, toxic substances, *"prescription-only"* or *"contraindicated during pregnancy / for children"* notices) and highlights them right at the top.
- 📋 **Clear & Concise Formatting** — translates complex medical and legal jargon into plain, easy-to-follow bullet points.
- 🔊 **Natural Voice Readout (TTS)** — synthesizes clean speech (`edge-tts`, `ru-RU-DmitryNeural` voice) and replies with an audio voice message.

## 🚀 Installation & Usage

1. Install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file from `.env.example` and add your API keys:
   ```bash
   cp .env.example .env
   ```
3. Start the bot:
   ```bash
   python3 bot.py
   ```
