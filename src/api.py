#!/usr/bin/env python3
"""
FastAPI server for Chrome Extension integration
"""

import os
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pipeline import analyzer_pipeline

app = FastAPI(title="Terms & Conditions Analyzer API", version="1.0.0")

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Chrome extension needs this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    content: str
    page_title: str = ""
    page_url: str = ""

class AnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    error: str = None

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Terms & Conditions Analyzer API is running"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(request: AnalysisRequest):
    """
    Analyze terms and conditions content using the analyzer pipeline
    """
    try:
        if not request.content or len(request.content.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="Content too short - need at least 50 characters for analysis"
            )
        
        print(f"📋 Analyzing content from: {request.page_url}")
        print(f"📄 Content length: {len(request.content)} characters")
        
        # Call the analyzer pipeline with just the content
        result = analyzer_pipeline(request.content)
        
        if "error" in result:
            error_msg = result["error"]
            # Make error messages more user-friendly
            if "Failed to extract product info" in error_msg:
                error_msg = "Could not identify the financial product from the page content. Please ensure you're analyzing a terms and conditions page."
            
            return AnalysisResponse(
                success=False,
                error=error_msg
            )
        
        # Add page metadata to the result
        if "metadata" not in result:
            result["metadata"] = {}
        
        result["metadata"]["page_title"] = request.page_title
        result["metadata"]["page_url"] = request.page_url
        result["metadata"]["content_length"] = len(request.content)
        
        return AnalysisResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return AnalysisResponse(
            success=False,
            error=f"Analysis failed: {str(e)}"
        )

@app.get("/test")
async def test_endpoint():
    """Test endpoint for Chrome extension"""
    return {
        "success": True,
        "message": "API connection successful!",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/",
            "test": "/test"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Terms & Conditions Analyzer API...")
    print("📋 Available at: http://localhost:8000")
    print("📊 Docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
