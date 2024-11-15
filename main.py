from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import os
from dotenv import load_dotenv
import shutil
from pathlib import Path

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return "kuku"

@app.post("/process-image/")
async def process_image(image: UploadFile = File(...)):
    try:
        genai.configure(api_key=os.getenv("GENAI_API_KEY"))

        file_path = Path(f"uploads/{image.filename}")
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        myfile = genai.upload_file(file_path)
        print(f"File uploaded successfully: {myfile}")

        prompt = (
            "Proszę podać następujące informacje z tego zdjęcia:"
            "\n1. NIP firmy."
            "\n2. Data transakcji."
            "\n3. Kwota (łącznie z walutą)."
            "\n4. Sposób płatności (np. karta, przelew, gotówka)."
            "\n5. Kontrahent oferuje jakim rodzajem usług"
            "\nProszę podać odpowiedź w języku polskim."
        )
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content([myfile, "\n\n", prompt])

        os.remove(file_path)

        return JSONResponse(content={"response": result.text})
    except Exception as e:
        print("Error occurred:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)