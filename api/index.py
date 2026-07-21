import os
import json
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

app = FastAPI(title="AI Product Categorizer")

# 1. Individual key-value schema for Gemini (bypasses additionalProperties issue)
class AttributeItem(BaseModel):
    key: str = Field(description="Attribute name (e.g., Color, Material, Brand, Style)")
    value: str = Field(description="Attribute value (e.g., Black, Leather, Nike, Casual)")

# 2. Main response schema
class ProductAnalysis(BaseModel):
    title: str = Field(description="A concise, attractive product title")
    description: str = Field(description="A 2-3 sentence marketing description of the product")
    category: str = Field(description="Main Category > Subcategory (e.g., Electronics > Audio > Headphones)")
    attributes: List[AttributeItem] = Field(description="List of observable key visual attributes")

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is missing from environment variables.")
    return genai.Client(api_key=api_key)

@app.post("/api/analyze")
async def analyze_product(image: UploadFile = File(...)):
    """API endpoint to receive image, process via Gemini, and return structured product info."""
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        contents = await image.read()
        mime_type = image.content_type
        
        client = get_gemini_client()

        prompt = (
            "Analyze this product image carefully. Extract and generate:\n"
            "1. An appropriate e-commerce product title.\n"
            "2. A compelling product description.\n"
            "3. The primary category path (e.g., Home & Kitchen > Furniture).\n"
            "4. A list of key visual attributes (e.g., Color, Material, Brand/Logo if visible, Style)."
        )

        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=[
                types.Part.from_bytes(data=contents, mime_type=mime_type),
                prompt
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ProductAnalysis,
                temperature=0.2,
            ),
        )

        result_data = json.loads(response.text)
        
        # Convert List[AttributeItem] back into a simple Dict for the UI
        if isinstance(result_data.get("attributes"), list):
            attr_dict = {
                item["key"]: item["value"] 
                for item in result_data["attributes"] 
                if isinstance(item, dict) and "key" in item and "value" in item
            }
            result_data["attributes"] = attr_dict

        return {"success": True, "data": result_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serves a modern, clean HTML UI with Tailwind CSS."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Product Categorizer</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-50 text-slate-800 min-h-screen py-10 px-4">
        <div class="max-w-4xl mx-auto">
            <!-- Header -->
            <div class="text-center mb-10">
                <h1 class="text-4xl font-extrabold text-slate-900 mb-2">🏷️ AI Product Categorizer</h1>
                <p class="text-slate-600">Upload a product image to instantly extract Title, Description, Category, and Attributes.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <!-- Upload Section -->
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h2 class="text-lg font-semibold mb-4 text-slate-900">1. Select Product Image</h2>
                    
                    <label class="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed border-slate-300 rounded-xl cursor-pointer hover:border-indigo-500 bg-slate-50 hover:bg-slate-100 transition duration-150 overflow-hidden relative">
                        <div id="upload-placeholder" class="flex flex-col items-center justify-center pt-5 pb-6">
                            <svg class="w-10 h-10 mb-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                            <p class="mb-2 text-sm text-slate-600 font-medium">Click to upload or drag & drop</p>
                            <p class="text-xs text-slate-400">PNG, JPG, WEBP</p>
                        </div>
                        <img id="image-preview" class="hidden absolute inset-0 w-full h-full object-contain p-2 bg-white" />
                        <input id="image-input" type="file" accept="image/*" class="hidden" onchange="previewImage(event)" />
                    </label>

                    <button id="analyze-btn" onclick="analyzeImage()" class="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-xl shadow transition duration-150 disabled:opacity-50">
                        Analyze Image
                    </button>
                </div>

                <!-- Results Section -->
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                    <h2 class="text-lg font-semibold mb-4 text-slate-900">2. Extracted Product Information</h2>
                    
                    <div id="loading" class="hidden flex-col items-center justify-center py-16 text-indigo-600">
                        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-3"></div>
                        <p class="text-sm font-medium text-slate-600">Analyzing image with Gemini Vision AI...</p>
                    </div>

                    <div id="empty-state" class="text-center py-20 text-slate-400 text-sm">
                        Upload an image and click "Analyze Image" to view extracted details.
                    </div>

                    <div id="result-container" class="hidden space-y-5">
                        <div>
                            <span class="text-xs font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md" id="res-category">Category</span>
                            <h3 class="text-xl font-bold text-slate-900 mt-2" id="res-title">Product Title</h3>
                        </div>

                        <div>
                            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Description</p>
                            <p class="text-sm text-slate-700 mt-1 leading-relaxed" id="res-description"></p>
                        </div>

                        <div>
                            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Attributes</p>
                            <div class="bg-slate-50 rounded-xl p-3 border border-slate-200 text-sm" id="res-attributes">
                                <!-- Dynamic key-value pairs -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let selectedFile = null;

            function previewImage(event) {
                const file = event.target.files[0];
                if (file) {
                    selectedFile = file;
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.getElementById('image-preview');
                        preview.src = e.target.result;
                        preview.classList.remove('hidden');
                        document.getElementById('upload-placeholder').classList.add('hidden');
                    }
                    reader.readAsDataURL(file);
                }
            }

            async function analyzeImage() {
                if (!selectedFile) {
                    alert("Please select an image first!");
                    return;
                }

                const btn = document.getElementById('analyze-btn');
                const loading = document.getElementById('loading');
                const emptyState = document.getElementById('empty-state');
                const resultContainer = document.getElementById('result-container');

                btn.disabled = true;
                emptyState.classList.add('hidden');
                resultContainer.classList.add('hidden');
                loading.classList.remove('hidden');
                loading.classList.add('flex');

                const formData = new FormData();
                formData.append('image', selectedFile);

                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });

                    const json = await response.json();

                    if (response.ok && json.success) {
                        const data = json.data;
                        document.getElementById('res-title').innerText = data.title;
                        document.getElementById('res-description').innerText = data.description;
                        document.getElementById('res-category').innerText = data.category;

                        const attrContainer = document.getElementById('res-attributes');
                        attrContainer.innerHTML = '';
                        for (const [key, val] of Object.entries(data.attributes)) {
                            attrContainer.innerHTML += `
                                <div class="flex justify-between py-1 border-b border-slate-200 last:border-b-0">
                                    <span class="font-medium text-slate-600">${key}:</span>
                                    <span class="text-slate-900 font-semibold">${val}</span>
                                </div>
                            `;
                        }

                        resultContainer.classList.remove('hidden');
                    } else {
                        alert("Error: " + (json.detail || "Failed to process image."));
                        emptyState.classList.remove('hidden');
                    }
                } catch (err) {
                    alert("Network error occurred.");
                    emptyState.classList.remove('hidden');
                } finally {
                    btn.disabled = false;
                    loading.classList.add('hidden');
                    loading.classList.remove('flex');
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
