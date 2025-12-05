# app/openai_client.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_recommendations(prediction: dict, user_emotion: str) -> dict:
    """
    Uses OpenAI's new SDK interface (>=1.0.0) to generate structured, motivational,
    and actionable recommendations when predicted emotion doesn't match the user's intended one.
    """

    system_prompt = (
        "You are an expert communication and performance coach. "
        "You analyze emotion delivery in videos and provide detailed, structured feedback. "
        "Your goal is to help speakers express their intended emotions authentically and effectively. "
        "Always provide feedback in a structured, markdown-ready format with clear sections."
    )

    user_prompt = f"""
    The speaker intended to express **{user_emotion}**, but the multimodal model predicted **{prediction['predicted_emotion']}**.
    Model confidence: {prediction.get('confidence')}
    Modalities observed: {prediction.get('modalities', {})}

    Please provide feedback with the following structure:

    ### Explanation of Mismatch
    Briefly explain why the intended and detected emotions might differ.

    ### Improvement Tips
    Give **5 specific, actionable** recommendations covering:
    - Voice & Tone
    - Facial Expression
    - Body Language
    - Word Choice / Delivery
    - Environmental or Technical Adjustments

    ### Motivational Wrap-Up
    End with an encouraging message that motivates the speaker to improve, highlighting potential and progress.

    ### Summary in 3 Bullet Points
    List exactly 3 short, action-oriented takeaways that summarize your feedback.

    **Finally**, conclude with a one-line takeaway starting with:
    `KEY SUMMARY:` (example: KEY SUMMARY: Add more vocal energy and maintain open body posture to express enthusiasm.)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )

        full_text = response.choices[0].message.content.strip()

        # Extract KEY SUMMARY line if present
        key_summary = None
        for line in full_text.splitlines():
            if line.strip().startswith("KEY SUMMARY:"):
                key_summary = line.strip().replace("KEY SUMMARY:", "").strip()
                break

        return {
            "full_recommendation": full_text,
            "key_summary": key_summary or "No summary provided."
        }

    except Exception as e:
        return {
            "full_recommendation": f"OpenAI API error: {e}",
            "key_summary": "OpenAI API failed to generate feedback."
        }
