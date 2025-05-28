import warnings
warnings.filterwarnings("ignore")
import os
import time
from decouple import config

# Record start time for uptime tracking
start_time = time.time()

from crewai_tools import FileReadTool
from routes.api_routes import router
from functions.functions import CustomCrew

# FastAPI imports
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Dict, List, Optional, Any

# FIXED: Use ANTHROPIC_API_KEY instead of OPENAI_API_KEY
api_key = config("BEDROCK_API_KEY")
os.environ["OPENAI_API_KEY"] = api_key

# Initialize tools
file_read_tool = FileReadTool()

# Create FastAPI app
app = FastAPI(title="Triage AI API", description="API for Triage AI agent system")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(router)

@app.get("/")
async def get_root():
    return {"message": "Welcome to the Triage AI API", "version": "1.0.0", "status": "running","docs": "/docs", "uptime": time.time() - start_time}

# Keep CLI functionality or run API server
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        # Start API server
        import uvicorn
        port = 8000  # Use a different port to avoid conflicts
        print(f"Starting Devyan API server at http://0.0.0.0:{port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # Run CLI version (original functionality)
        print("\n####### Welcome to Devyan #######")
        print("---------------------------------")
        user_input = input("What problem do you want me to solve?\n")
        crew = CustomCrew(user_input)
        result = crew.run()
        
        print("\n\n########################")
        print("## Here is your crew run result:")
        print("########################\n")
        print(result)
