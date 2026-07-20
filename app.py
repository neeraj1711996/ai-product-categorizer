"""
AI Product Categorizer
-----------------------
A beginner-friendly app that uses Google's Gemini AI to look at a product
photo + description, and automatically suggest:
  - Category
  - Subcategory
  - Attributes (material, color, condition, brand, etc.)

Built with Gradio (the web UI) and Google Generative AI (the "brain").

HOW TO RUN LOCALLY:
    1. pip install -r requirements.txt
    2. Create a file named ".env" in this same folder with:
           GEMINI_API_KEY=your-real-key-here
    3. python app.py
    4. Open the local URL Gradio prints in your terminal.
"""

import os
import json
import gradio as gr
import google.generativeai as genai
from dotenv import load_dotenv

# -----------------------------------------------------------------------
# STEP 1: Load the API key
# -----------------------------------------------------------------------
# load_dotenv() reads a local ".env" file (if it exists) and makes its
# values available via os.environ. This lets us keep the real key OUT
# of the code and out of GitHub.
load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

MODEL_NAME = "gemini-1.5-pro"

GENERATION_CONFIG = {
    "temperature": 0.4,          # lower = more consistent/predictable answers
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 2048,
    "response_mime_type": "application/json",  # ask Gemini to return JSON directly
}

# -----------------------------------------------------------------------
# STEP 2: The instructions we give the AI (the "prompt")
# -----------------------------------------------------------------------
# We ask Gemini to always answer in a strict JSON shape, so our app can
# parse it reliably instead of guessing at free-form text.
SYSTEM_PROMPT = """
You are a product categorization engine for an e-commerce / auction
platform. Given a product's title/description and an image, determine:

1. "categories": one or more high-level categories the item belongs to
   (e.g. "Furniture", "Electronics", "Jewelry & Watches").
2. "subcategories": one or more specific subcategories within those
   categories (e.g. "Writing Desks", "Smartphones", "Wristwatches").
3. "attributes": a list of relevant attribute objects with "name" and
   "value" fields, drawn from what's typical for that category
   (e.g. material, color, brand, condition, era, size, model).

Respond ONLY with valid JSON in exactly this shape, no extra commentary:

{
  "categories": ["string", ...],
  "subcategories": ["string", ...],
  "attributes": [
    {"name": "string", "value": "string"},
    ...
  ]
}

If something can't be determined from the text/image, use "Unknown" as
the value rather than guessing wildly.
"""


# -----------------------------------------------------------------------
# STEP 3: The function that actually talks to Gemini
# -----------------------------------------------------------------------
def categorize_product(image_path: str, description: str, api_key_override: str):
    """
    Sends the image + description to Gemini and returns a formatted
    Markdown string with the category, subcategory, and attributes.
    """

    # --- Basic validation (friendly errors instead of crashes) ---
    if not image_path:
        return "⚠️ Please upload a product image first."
    if not description or not description.strip():
        return "⚠️ Please enter a product title or description."

    key_to_use = (api_key_override or "").strip() or GEMINI_API_KEY
    if not key_to_use:
        return (
            "❌ No API key found.\n\n"
            "Either set GEMINI_API_KEY in a .env file (for local use) / "
            "as a repository secret (on Hugging Face), or paste a key "
            "into the 'Gemini API Key' box above."
        )

    try:
        genai.configure(api_key=key_to_use)

        # Upload the image to Gemini's file service
        uploaded_file = genai.upload_file(image_path)

        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config=GENERATION_CONFIG,
        )

        response = model.generate_content(
            [SYSTEM_PROMPT, f"Product description: {description.strip()}", uploaded_file]
        )

        # Gemini was asked to return JSON — parse it so we can format it nicely
        data = json.loads(response.text)

        return format_result_as_markdown(data)

    except json.JSONDecodeError:
        # If parsing fails, just show the raw text so the user still gets something
        return f"⚠️ Got a response, but couldn't parse it as JSON. Raw output:\n\n{response.text}"
    except Exception as e:
        return f"❌ Something went wrong: {e}"


def format_result_as_markdown(data: dict) -> str:
    """Turns the parsed JSON result into a clean, readable Markdown block."""

    categories = data.get("categories", [])
    subcategories = data.get("subcategories", [])
    attributes = data.get("attributes", [])

    lines = []
    lines.append("### 🗂️ Category")
    lines.append(", ".join(categories) if categories else "Unknown")
    lines.append("")
    lines.append("### 📁 Subcategory")
    lines.append(", ".join(subcategories) if subcategories else "Unknown")
    lines.append("")
    lines.append("### 🏷️ Attributes")

    if attributes:
        for attr in attributes:
            name = attr.get("name", "Unknown")
            value = attr.get("value", "Unknown")
            lines.append(f"- **{name}:** {value}")
    else:
        lines.append("_No attributes detected._")

    return "\n".join(lines)


# -----------------------------------------------------------------------
# STEP 4: Build the Gradio UI
# -----------------------------------------------------------------------
with gr.Blocks(title="AI Product Categorizer", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🛍️ AI Product Categorizer
        Upload a product photo and a short description. The AI will
        suggest a **category**, **subcategory**, and key **attributes**
        — useful for auction listings, marketplaces, or inventory tagging.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                type="filepath",
                label="Product Image",
                height=320,
            )
            description_input = gr.Textbox(
                label="Product Title / Description",
                placeholder="e.g. Vintage leather messenger bag, brown, "
                            "brass buckles, light wear on the strap",
                lines=5,
            )
            api_key_input = gr.Textbox(
                label="Gemini API Key (optional — only needed if not set as a secret)",
                placeholder="Leave blank to use the environment/secret key",
                type="password",
            )

            with gr.Row():
                submit_btn = gr.Button("Categorize", variant="primary")
                clear_btn = gr.Button("Clear")

        with gr.Column(scale=1):
            output_box = gr.Markdown(label="Result")

    submit_btn.click(
        fn=categorize_product,
        inputs=[image_input, description_input, api_key_input],
        outputs=output_box,
    )

    clear_btn.click(
        fn=lambda: (None, "", "", ""),
        inputs=[],
        outputs=[image_input, description_input, api_key_input, output_box],
    )

    gr.Markdown(
        """
        ---
        *Powered by Google Gemini. Your API key is only used for this
        request and is not stored.*
        """
    )

# -----------------------------------------------------------------------
# STEP 5: Launch
# -----------------------------------------------------------------------
if __name__ == "__main__":
    demo.launch()
