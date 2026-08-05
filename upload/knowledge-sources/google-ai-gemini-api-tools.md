# Google AI, Gemini & LLM API Tools

Tools for Google Gemini API, generative AI SDKs, and LLM-powered applications.

## babaohuang/GeminiProChat ⭐4,882

**URL**: https://github.com/babaohuang/GeminiProChat

**Description**: Minimal web UI for GeminiPro.

# GeminiProChat

English | [中文](README_cn.md) | [Italiano](README_it.md) | [日本語](README_jp.md)

Minimal web UI for Gemini Pro Chat.

> [!WARNING]
> **Disclaimer:** This project is not affiliated with, endorsed by, or sponsored by Google. It is an independent project that uses Google's Gemini Pro API.

Live demo: [Gemini Pro Chat](https://gprochat.orzllc.com)

## Deploy

### Deploy With Vercel(Recommended)

Just click the button above and follow the instructions to deploy your own copy of the app.


### Deploy on Railway

Just click the button above and follow the instructions to deploy on Railway.

### Deploy on Zeabur

Just click the button above and follow the instructions to deploy on Zeabur.

### Deploy With Docker

To deploy with Docker, you can use the following command:

```bash
docker run --name geminiprochat \
--restart always \
-p 3000:3000 \
-itd \
-e GEMINI_API_KEY=your_api_key_here \
babaohuang/geminiprochat:latest
```
Please make sure to replace `your_api_key_here` with your own GEMINI API key.

This will start the **geminiprochat** service, accessible at `http://localhost:3000`. 

## Environment Variables

You can control the website through environment variables.

| Name | Description | Required |
| --- | --- | --- |
| `GEMINI_API_KEY` | Your API Key for GEMINI. You can get it from [here](https://makersuite.google.com/app/apikey).| **✔** |
| `API_BASE_URL` | Custom base url for GEMINI API. Click [here](https://github.com/babaohuang/GeminiProChat?tab=readme-ov-file#solution-for-user-location-is-not-supported-for-the-api-use) to see when to use this. | ❌ |
| `HEAD_SCRIPTS` | Inject analytics or other scripts before `</head>` of the page | ❌ |
| `PUBLIC_SECRET_KEY` | Secret string for the project. Use for generating signatures for API calls | ❌ |
| `SITE_PASSWORD` | Set password for site, support multiple password separated by comma. If not set, site will be public | ❌ |
| `GEMINI_MODEL_NAME` | Customize the Gemini model to use. Defaults to `gemini-2.5-flash` if not set | ❌ |

## Running Locally

### Pre environment
1. **Node**: Check that both your development environment and deployment environment are using `Node v18` or later. You can use [nvm](https://github.com/nvm-sh/nvm) to manage multiple `node` versions locally.

   ```bash
    node -v
   ```

2. **PNPM**: We recommend using [pnpm](https://pnpm.io/) to manage dependencies. If you have never installed pnpm, you can install it with the following command:

   ```bash
    npm i -g pnpm
   ```

3. **GEMINI_API_KEY**: Before running this application, you need to obtain the API key from Google. You can register the API key at [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey).

### Getting Started

1. Install dependencies

   ```bash
    pnpm install
   ```

2. Copy the `.env.example` file, then rename it to `.env`, and add your [`GEMINI_API_KEY`](https://makersuite.google.com/app/apikey) to the `.env` file.

   ```bash
    GEMINI_API_KEY=AIzaSy...

---

## ViaAnthroposBenevolentia/gemini-2-live-api-demo ⭐387

**URL**: https://github.com/ViaAnthroposBenevolentia/gemini-2-live-api-demo

**Description**: Vanilla JS web interface for Gemini 2.0 flash-exp  Multimodal API with text, audio, camera, screen inputs and audio responses and function calling

# Gemini 2.0 Flash Multimodal Live API Client

A lightweight vanilla JavaScript implementation of the Gemini 2.0 Flash Multimodal Live API client. This project provides real-time interaction with Gemini's API through text, audio, video, and screen sharing capabilities.

This is a simplified version of [Google's original React implementation](https://github.com/google-gemini/multimodal-live-api-web-console), created in response to [this issue](https://github.com/google-gemini/multimodal-live-api-web-console/issues/19).

## Live Demo on GitHub Pages

[Live Demo](https://viaanthroposbenevolentia.github.io/gemini-2-live-api-demo/)

## Key Features

- Real-time chat with Gemini 2.0 Flash Multimodal Live API
- Real-time audio responses from the model
- Real-time audio input from the user, allowing interruptions
- Real-time video streaming from the user's webcam
- Real-time screen sharing from the user's screen
- Function calling
- Transcription of the model's audio (if Deepgram API key provided)
- Built with vanilla JavaScript (no dependencies)
- Mobile-friendly

## Prerequisites

- Modern web browser with WebRTC, WebSocket, and Web Audio API support
- Google AI Studio API key
- `python -m http.server` or `npx http-server` or Live Server extension for VS Code (to host a server for index.html)

## Quick Start

1. Get your API key from Google AI Studio
2. Clone the repository

   ```bash
   git clone https://github.com/ViaAnthroposBenevolentia/gemini-2-live-api-demo.git
   ```

3. Start the development server (adjust port if needed):

   ```bash
   cd gemini-2-live-api-demo
   python -m http.server 8000 # or npx http-server 8000 or Open with Live Server extension for VS Code
   ```

4. Access the application at `http://localhost:8000`

5. Open the settings at the top right, paste your API key, and click "Save"
6. Get free API key from [Deepgram](https://deepgram.com/pricing) and paste in the settings to get real-time transcript (Optional).

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License.

---

## mscraftsman/generative-ai ⭐213

**URL**: https://github.com/mscraftsman/generative-ai

**Description**: Gemini SDK for .NET and ASP.NET Core enables developers to use Google's state-of-the-art generative AI models to build AI-powered features and applications.



---

## haseeb-heaven/langchain-coder ⭐126

**URL**: https://github.com/haseeb-heaven/langchain-coder

**Description**: Web Application that can generate code and fix bugs and run using various LLM's (GPT,Gemini,PALM)



---

## Addy-shetty/Vibe-Prompting ⭐121

**URL**: https://github.com/Addy-shetty/Vibe-Prompting

**Description**: 🎨 AI-Powered Prompt Generator | Transform ideas into powerful AI prompts instantly with smart credit system, real-time streaming, and 14 specialized categories. Built with React, TypeScript, Supabase & deployed on Vercel. Try 3 free generations - no signup required! ⚡



---

