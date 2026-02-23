import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from openai import OpenAI

# 1. OpenAI Client Setup
# Yahan apni API Key dalein
client = OpenAI(api_key="skApiKeys")

# 2. Data Models (Schemas)
# Ye class input comment handle karegi
class CommentInput(BaseModel):
    comment: str

# Ye class AI ke structured response ko enforce karegi
class SentimentResponse(BaseModel):
    sentiment: Literal["positive", "negative", "neutral"]
    rating: int = Field(..., ge=1, le=5, description="1 is very negative, 5 is very positive")

# 3. FastAPI App Initialize
app = FastAPI(title="Sentiment Analysis API")

# 4. POST Endpoint
@app.post("/comment", response_model=SentimentResponse)
async def analyze_sentiment(input_data: CommentInput):
    try:
        # OpenAI API call with Structured Outputs
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a customer feedback analyst. Extract the sentiment and a rating (1-5) from the user comment. Be consistent."
                },
                {"role": "user", "content": input_data.comment},
            ],
            response_format=SentimentResponse, # Pydantic model yahan pass kiya
        )

        # Parse kiya hua data nikaalein
        analysis = completion.choices[0].message.parsed
        
        if not analysis:
            raise HTTPException(status_code=500, detail="AI failed to generate a structured response.")

        return analysis

    except Exception as e:
        # Error handling for API failures or invalid input
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# Run karne ke liye command: uvicorn main:app --reload