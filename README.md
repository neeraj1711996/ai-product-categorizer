# 🏷️ AI Product Categorizer

An end-to-end, full-stack AI web application built with **FastAPI**, **Google Gemini Vision AI**, and **Tailwind CSS**. The app allows users to upload any product image and instantly extracts a structured title, marketing description, multi-level category path, and visual key-value attributes
---

Link - https://ai-product-categorizer-git-main-neeraj1711996s-projects.vercel.app/

## ✨ Features

- 📸 **Vision AI Analysis:** Uses Google Gemini 2.5 Flash to visually analyze product images in real time.
- 📐 **Structured Pydantic Output:** Enforces strict JSON schemas for consistent output parsing:
  - **Product Title:** Catchy, marketplace-ready title.
  - **Description:** Concise 2–3 sentence product overview.
  - **Category Path:** Multi-level taxonomy (`Category > Subcategory`).
  - **Visual Attributes:** Dynamic key-value extraction (Color, Material, Style, Brand, etc.).
- ⚡ **Lightweight FastAPI Backend:** Single serverless Python app serving both REST endpoints and frontend.
- 🎨 **Responsive UI:** Modern, clean user interface styled with Tailwind CSS.
- ☁️ **Zero-Configuration Deployment:** Configured for seamless, serverless hosting on **Vercel**.

---

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI / Uvicorn
- **AI Model:** Google Gemini API (`google-genai` SDK)
- **Data Validation:** Pydantic v2
- **Frontend:** HTML5 + Tailwind CSS + Vanilla JS
- **Deployment & Hosting:** Vercel (Serverless Python Runtime)

---

## 📁 Project Structure

```text
ai-product-categorizer/
├── api/
│   └── index.py        # Main FastAPI server, Gemini logic, and embedded UI HTML
├── .env                # Local environment variables (Git ignored)
├── .gitignore          # Excluded tracking files
├── README.md           # Project documentation
├── requirements.txt    # Python package dependencies
└── vercel.json         # Vercel serverless routing configuration
