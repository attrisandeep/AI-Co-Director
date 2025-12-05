# pyright: reportMissingImports=false
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import os
import json
import warnings
import sys
from pathlib import Path
import fitz  # PyMuPDF for text extraction

"""Ensure local src layout is importable: script_writer/src."""
SRC_PATH = Path(__file__).parent / "script_writer" / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from script_writer.crew import ScriptWriter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

app = FastAPI(
    title="Script Writer API",
    description="An AI-powered multi-agent system that transforms scripts into a specified genre with iterative improvements.",
    version="1.2.0",
)

# -------------------------------
# Helper: Extract Text from PDF
# -------------------------------
def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file using PyMuPDF."""
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()

# -------------------------------
# Helper: Format Script Output
# -------------------------------
def format_script_output(script_text: str, genre: str, review_text: str = "") -> str:
    """Formats the final script and review in a structured screenplay-like layout."""
    formatted_output = f"""
------------------------------------------
🎬  FINAL REWRITTEN SCRIPT ({genre.upper()})
------------------------------------------

{script_text.strip()}


------------------------------------------
✅  END OF SCRIPT
------------------------------------------
"""
    return formatted_output.strip()

# -------------------------------
# Core Logic Function
# -------------------------------
def run_script_generation(original_script: str, genre: str):
    """Reusable function for both direct text and PDF input."""
    os.makedirs("output", exist_ok=True)

    script_to_rewrite = original_script
    target_genre = genre

    iteration = 0
    max_iterations = 2
    final_output = {}
    final_script_text = ""
    final_review_text = ""

    while iteration < max_iterations:
        iteration += 1
        print(f"\n====================\n=== ITERATION {iteration} ===\n====================\n")

        crew = ScriptWriter().crew()

        inputs = {
            "original_script": script_to_rewrite,
            "genre": target_genre,
        }

        supervisor_results = crew.kickoff(inputs=inputs)
        rewritten_script = crew.tasks[0].output.raw
        review_report = crew.tasks[1].output.raw

        final_script_text = rewritten_script
        final_review_text = review_report

        try:
            supervisor_data = json.loads(supervisor_results.raw)
        except json.JSONDecodeError:
            final_output = {
                "iteration": iteration,
                "ready": False,
                "message": "Supervisor output invalid JSON, stopped early.",
            }
            break

        if supervisor_data.get("ready", False):
            final_output = {
                "iteration": iteration,
                "ready": True,
                "message": "Script approved by supervisor.",
            }
            break
        else:
            rewrite_instructions = supervisor_data.get("rewrite_instructions", "")
            script_to_rewrite = (
                f"### PREVIOUS SCRIPT VERSION:\n{rewritten_script}\n\n"
                f"### INSTRUCTIONS FOR NEXT REWRITE:\n{rewrite_instructions}"
            )

    if not final_output:
        final_output = {
            "iteration": iteration,
            "ready": False,
            "message": "Max iterations reached without approval.",
        }

    # Generate structured formatted script
    structured_script = format_script_output(final_script_text, genre)

    # Save it to file
    final_path = f"output/final_script_structured_iter_{iteration}.md"
    with open(final_path, "w", encoding="utf-8") as f:
        f.write(structured_script)

    return {
        "status": "success",
        "result": final_output,
        "structured_script": structured_script,
        "file_path": final_path,
    }

# -------------------------------
# 1️⃣ Existing Text Input Endpoint
# -------------------------------
class ScriptRequest(BaseModel):
    original_script: str
    genre: str

@app.post("/generate-script/")
def generate_script(request: ScriptRequest):
    return run_script_generation(request.original_script, request.genre)

# -------------------------------
# 2️⃣ New PDF Upload Endpoint
# -------------------------------
@app.post("/generate-script-from-pdf/")
async def generate_script_from_pdf(file: UploadFile = File(...), genre: str = Form(...)):
    """Accepts a PDF file, extracts text, and generates the rewritten script."""
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"

        # Save PDF
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Extract text
        extracted_text = extract_text_from_pdf(file_path)
        if not extracted_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

        # Run generation
        result = run_script_generation(extracted_text, genre)

        # Include extracted text for frontend preview
        result["extracted_text_preview"] = (
            extracted_text[:1500] + "..." if len(extracted_text) > 1500 else extracted_text
        )

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------
# Run Locally
# -------------------------------
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
