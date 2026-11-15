from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = FastAPI()

#  CORS BOUNCER 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIREBASE CONNECTION 
try:
    cred = credentials.Certificate("firebase_credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print(" Firebase Connected Successfully!")
except Exception as e:
    print(f" Firebase Connection Failed: {e}")

# MOCK AI FUNCTION 
def analyze_leaf(image_bytes):
    return {
        "crop": "Tomato",
        "disease": "Early Blight",
        "confidence": "94%",
        "status": "Disease detected",
        "treatment": "Use copper-based fungicides. Remove infected lower leaves."
    }

#  THE MAIN ENDPOINT 
@app.post("/api/detect-disease")
async def detect_disease(file: UploadFile = File(...)):
    # 1. Check if the uploaded file is actually an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # 2. Read the image sent by Flutter
    image_bytes = await file.read()

    # 3. Analyze the image (currently using our mock function)
    ai_result = analyze_leaf(image_bytes)

    # 4. Prepare the exact data structure for your 'scans' database collection
    scan_data = {
        "scan_date": datetime.utcnow().isoformat(),
        "crop_name": ai_result["crop"],
        "disease_name": ai_result["disease"],
        "confidence_score": ai_result["confidence"],
        "treatment_recommendation": ai_result["treatment"]
    }

    # 5. Save it to Firestore
    try:
        db.collection("scans").add(scan_data)
        print("💾 Scan saved to database!")
    except Exception as e:
        print(f"Database Error: {e}")

    # 6. Send the result back to the frontend
    return ai_result