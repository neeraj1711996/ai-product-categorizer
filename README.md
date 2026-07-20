---
title: AI Product Categorizer
emoji: 🛍️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# 🛍️ AI Product Categorizer

Upload a product photo + description, and get back an AI-suggested
**Category**, **Subcategory**, and **Attributes** — powered by Google Gemini.

## How it works

1. You upload an image and type a short description.
2. The app sends both to Gemini with instructions to return structured
   category data.
3. The result is parsed and displayed in a clean, readable format.

## Running locally

```bash
# 1. Clone this repo
git clone https://github.com/<your-username>/product-categorizer.git
cd product-categorizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your API key
cp .env.example .env
# then open .env and paste your real Gemini API key

# 4. Run the app
python app.py
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

## Deploying on Hugging Face Spaces

1. Go to https://huggingface.co/new-space
2. Choose **Gradio** as the Space SDK.
3. Either:
   - Push this repo's files to the Space's git remote, or
   - Connect your GitHub repo directly in the Space settings.
4. In the Space, go to **Settings → Repository secrets** and add:
   - Name: `GEMINI_API_KEY`
   - Value: your real Gemini API key
5. The Space builds automatically and gives you a live URL.

**Important:** Never commit your real `.env` file. Only `.env.example`
(with a placeholder) should ever be pushed to GitHub or Hugging Face.

## Project structure

```
product-categorizer/
├── app.py              # main application
├── requirements.txt    # Python dependencies
├── .env.example        # template for required environment variables
├── .gitignore           # keeps .env and other local files out of git
└── README.md            # this file
```
