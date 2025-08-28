# main.py
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import random
import json
import os
import tempfile
import io
import re
import sys
from typing import Optional
from datetime import datetime
import asyncio
from gtts import gTTS
import base64
from helper_functions import initialize_agentt, get_llm_response, speech_to_text

# folder to store temporary audio files
OUTPUT_DIR = "audio_cache"
os.makedirs(OUTPUT_DIR, exist_ok=True)
voice_response_count = 0



# Initialize FastAPI app
app = FastAPI(title="AI Chatbot with Speech and Gold Detection", version="1.0.0")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory
templates = Jinja2Templates(directory="templates")

# Pydantic models for request/response
class TextMessage(BaseModel):
    text: str
    timestamp: Optional[str] = None

class VoiceMessage(BaseModel):
    transcript: str
    timestamp: Optional[str] = None

class TextToSpeechRequest(BaseModel):
    text: str
    voice: Optional[str] = "default"

class ChatResponse(BaseModel):
    text: str
    timestamp: str
    message_id: str
    contains_gold: bool = False

class GoldGuidanceResponse(BaseModel):
    guidance: str
    timestamp: str
    message_id: str

class NameRequest(BaseModel):
    name: str

user_id = "random_user"
agent = initialize_agentt(user_id)

# Simple chatbot responses (same as Node.js version)
responses = {
    "greetings": [
        "Hello! How can I help you today?",
        "Hi there! What's on your mind?",
        "Greetings! I'm here to chat with you.",
        "Hey! How are you doing?"
    ],
    "questions": [
        "That's an interesting question! Let me think about that.",
        "I'd love to help you with that!",
        "That's a great point you're making.",
        "I appreciate you asking that."
    ],
    "default": [
        "I understand what you're saying.",
        "That's fascinating! Tell me more.",
        "I see your point. What else would you like to discuss?",
        "Thanks for sharing that with me!",
        "Interesting! How do you feel about that?"
    ],
    "farewell": [
        "Goodbye! Have a wonderful day!",
        "See you later! It was great chatting with you.",
        "Take care! Feel free to come back anytime.",
        "Farewell! Looking forward to our next conversation."
    ],
    "gold_related": [
        "I see you're interested in gold! Gold has been a valuable asset for centuries and remains an important investment option today.",
        "Gold is indeed a fascinating topic! It's often considered a hedge against inflation and economic uncertainty.",
        "That's a great question about gold! Many investors consider precious metals like gold as part of a diversified portfolio.",
        "Gold investment can be complex but rewarding! There are various ways to invest in gold, from physical bullion to ETFs.",
        "You're asking about gold - that's smart thinking! Gold has historically maintained its value during economic turbulence."
    ]
}

# Gold-related keywords for detection
GOLD_KEYWORDS = [
    'gold', 'golden', 'bullion', 'precious metals', 'gold price', 'gold investment',
    'gold coins', 'gold bars', 'gold etf', 'gold mining', 'gold market',
    'gold jewelry', 'gold trading', 'buy gold', 'sell gold', 'gold value'
]



def get_random_response(response_array):
    """Get a random response from the given array"""
    return random.choice(response_array)

def detect_gold_mention(message: str) -> bool:
    """Detect if the message contains gold-related keywords"""
    lower_message = message.lower()
    return any(keyword in lower_message for keyword in GOLD_KEYWORDS)

def generate_response(message: str) -> tuple[str, bool]:


    """Generate chatbot response based on message content and detect gold mentions"""
    contains_gold = detect_gold_mention(message)
    try:
        response = get_llm_response(message, agent)
    except:
        response = get_random_response(responses["default"])
    
    # Check for gold-related content first
    if contains_gold:
        return (response, True)
    
    
    # Default responses
    return response, False





# ENDPOINT 1: Render main page (index.html)
@app.get("/", response_class=HTMLResponse)
async def render_main_page(request: Request):
    """Render the main chatbot interface"""
    return templates.TemplateResponse("user_page.html", {"request": request})


@app.post("/send_name", response_class=HTMLResponse)
async def receive_name(request: Request, name: str = Form(...)):
    user_id = name
    agent = initialize_agentt(user_id)
    return templates.TemplateResponse("index2.html", {"request": request, "user_id": name})


# ENDPOINT 2: Handle text messages from user with gold detection
@app.post("/api/send-text-message", response_model=ChatResponse)
async def handle_text_message(message: TextMessage):
    """
    Handle text message from user, detect gold mentions, and return bot response
    """
    try:
        # Validate input
        if not message.text or message.text.strip() == "":
            raise HTTPException(status_code=400, detail="Message text cannot be empty")
        
        # Generate bot response with gold detection
        bot_response, contains_gold = generate_response(message.text)
        
        # Create response
        response = ChatResponse(
            text=bot_response,
            timestamp=datetime.now().isoformat(),
            message_id=f"msg_{random.randint(1000, 9999)}",
            contains_gold=contains_gold
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

# ENDPOINT 3: Handle voice messages from user with gold detection
@app.post("/api/send-voice-message")
async def handle_voice_message(audio: UploadFile = File(...)):
    """
    Handle voice message from user, transcribe it, detect gold mentions, and return bot response
    """
    global voice_response_count
    try:
        # Validate file type
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio file
        audio_data = await audio.read()
    
        transcript = speech_to_text(audio_data)
        
        
        # Generate bot response based on transcript with gold detection
        bot_response, contains_gold = generate_response(transcript)

        voice_response_count += 1

        filename = f"voice_response_{voice_response_count}.mp3"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # generate audio using gTTS
        tts = gTTS(text=bot_response, lang="en")
        tts.save(filepath)
        
        
        
        # read file and encode to base64
        with open(filepath, "rb") as f:
            audio_base64 = base64.b64encode(f.read()).decode("utf-8")

        # build response in frontend-expected format
        response = {
            "audio_response": audio_base64,
            "bot_response": bot_response,  # optional fallback
            "timestamp": datetime.now().isoformat(),
            "contains_gold": contains_gold # example flag
        }

        return JSONResponse(content=response)
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error processing voice message: {str(e)}")

# ENDPOINT 4: Gold Investment Guidance
@app.get("/api/buy-digital-gold", response_class=HTMLResponse)
async def buy_digital_gold(request: Request):
    """Render a simple page with a link to buy digital gold"""
    return templates.TemplateResponse("digital_gold.html", {"request": request})
    

    


# Additional endpoint for serving generated audio files (optional)
@app.get("/api/audio/{audio_id}")
async def serve_audio(audio_id: str):
    """
    Serve generated audio files
    """
    # In production, this would serve actual audio files
    return JSONResponse({
        "audio_id": audio_id,
        "status": "Audio file would be served here",
        "note": "This is a placeholder endpoint"
    })

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "features": ["text_chat", "voice_chat", "gold_detection", "investment_guidance"]
    })

# New endpoint: Get gold market info (bonus feature)
@app.get("/api/gold-market-info")
async def get_gold_market_info():
    """
    Get simulated gold market information
    """
    try:
        # In production, you would fetch real market data from APIs like:
        # - Alpha Vantage
        # - Yahoo Finance
        # - Quandl
        # - Metals API
        
        # Simulate market data
        base_price = 2000
        price_change = random.uniform(-50, 50)
        current_price = base_price + price_change
        
        market_info = {
            "current_price": round(current_price, 2),
            "price_change": round(price_change, 2),
            "price_change_percent": round((price_change / base_price) * 100, 2),
            "currency": "USD",
            "unit": "per ounce",
            "last_updated": datetime.now().isoformat(),
            "market_status": "open" if datetime.now().hour < 16 else "closed",
            "trend": "bullish" if price_change > 0 else "bearish" if price_change < -10 else "neutral"
        }
        
        return JSONResponse(market_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market info: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "path": str(request.url.path)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 AI Chatbot FastAPI Server Starting...")
    print("📝 Endpoints available:")
    print("   GET  /                       - Main chatbot interface")
    print("   POST /api/send-text-message  - Handle text messages (with gold detection)")
    print("   POST /api/send-voice-message - Handle voice messages (with gold detection)")
   
    print("   GET  /api/gold-market-info   - Get gold market information")
    print("   GET  /api/health             - Health check")
    
    # Create directories if they don't exist
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

