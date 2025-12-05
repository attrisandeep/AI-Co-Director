from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from starlette.responses import JSONResponse
from typing import Optional

from .video_utils import save_upload_and_trim
from .model_wrapper import predict_from_video
from .openai_client import generate_recommendations

app = FastAPI(title="Multimodal Emotion Detection API")


@app.post("/predict")
async def predict(
    video: UploadFile = File(...),
    user_emotion: str = Form(...),
    start_time: Optional[str] = Form(None),
    end_time: Optional[str] = Form(None)
):
    """
    Upload a video and optionally provide start and end times (in seconds).
    If no times are provided, defaults to analyzing the full clip (up to 5 minutes).
    """
    # --- Validate file type ---
    if not video.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid video.")

    # --- Safe conversion helper ---
    def to_float(value, default=None):
        try:
            if value is None or str(value).strip() == "":
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    start_val = to_float(start_time, 0.0)
    end_val = to_float(end_time, None)

    # --- Video trimming ---
    try:
        trimmed_path, duration = save_upload_and_trim(await video.read(), video.filename, start_val, end_val)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video trimming failed: {e}")

    # --- Model prediction ---
    try:
        prediction = predict_from_video(trimmed_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    predicted_emotion = prediction.get("predicted_emotion", "unknown")
    confidence = prediction.get("confidence", None)

    # --- Compare with user expectation ---
    match = predicted_emotion.lower() == user_emotion.lower().strip().lower()
    recommendations = None

    if not match:
        try:
            recommendations = generate_recommendations(prediction, user_emotion)
        except Exception as e:
            recommendations = f"Recommendation generation failed: {e}"

    # --- Build final response ---
    return JSONResponse({
        "predicted_emotion": predicted_emotion,
        "confidence": confidence,
        "user_emotion": user_emotion,
        "match": match,
        "recommendations": recommendations,
        "clip_duration_seconds": duration,
    })
