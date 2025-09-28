#!/usr/bin/env python3
"""
Backend API Server for WEATHER-VESSEL-kq Logistics Control Tower
Provides AI Assistant and Daily Briefing endpoints
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
from datetime import datetime
from typing import List, Optional
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Logistics Control Tower API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/assistant")
async def ai_assistant(
    prompt: str = Form(...),
    history: str = Form(default="[]"),
    model: str = Form(default="gpt-4o-mini"),
    files: List[UploadFile] = File(default=[])
):
    """
    AI Assistant endpoint for logistics queries
    """
    try:
        # Parse history
        try:
            history_data = json.loads(history) if history else []
        except json.JSONError:
            history_data = []
        
        # Log the request
        logger.info(f"AI Assistant request: {prompt[:100]}...")
        logger.info(f"Model: {model}, Files: {len(files)}")
        
        # Process files if any
        file_info = []
        for file in files:
            if file.filename:
                file_info.append({
                    "name": file.filename,
                    "size": len(await file.read()),
                    "type": file.content_type
                })
        
        # Generate response based on prompt content
        response = generate_ai_response(prompt, history_data, file_info, model)
        
        return JSONResponse({
            "answer": response,
            "model": model,
            "files_processed": len(file_info),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI Assistant error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/briefing")
async def daily_briefing(request_data: dict):
    """
    Daily briefing endpoint for vessel status and logistics analysis
    """
    try:
        logger.info("Daily briefing request received")
        
        # Extract data from request
        current_time = request_data.get("current_time", datetime.now().isoformat())
        vessel_name = request_data.get("vessel_name", "JOPETWIL 71")
        vessel_status = request_data.get("vessel_status", "Ready @ MW4")
        current_voyage = request_data.get("current_voyage", "N/A")
        schedule = request_data.get("schedule", [])
        weather_windows = request_data.get("weather_windows", [])
        model = request_data.get("model", "gpt-4o-mini")
        
        # Generate briefing
        briefing = generate_daily_briefing(
            current_time, vessel_name, vessel_status, 
            current_voyage, schedule, weather_windows
        )
        
        return JSONResponse({
            "briefing": briefing,
            "model": model,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Daily briefing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_ai_response(prompt: str, history: List[dict], files: List[dict], model: str) -> str:
    """
    Generate AI response based on prompt and context
    """
    prompt_lower = prompt.lower()
    
    # Korean responses for better user experience
    if "스케줄" in prompt_lower or "schedule" in prompt_lower:
        return """📋 **항차 스케줄 분석**

현재 등록된 항차 정보:
• 69th 항차: Dune Sand 화물, ETD 2025-09-28 16:00, ETA 2025-09-29 04:00
• 70th 항차: 10mm Agg. 화물, ETD 2025-09-30 16:00, ETA 2025-10-01 04:00  
• 71st 항차: 5mm Agg. 화물, ETD 2025-10-02 16:00, ETA 2025-10-03 04:00

**권고사항:**
- 모든 항차가 정상 스케줄에 따라 진행 중
- 기상 조건 모니터링 필요
- IOI 점수 확인 권장"""

    elif "날씨" in prompt_lower or "weather" in prompt_lower:
        return """🌊 **기상 조건 분석**

현재 해상 기상 상황:
• 파고(Hs): 1.5m (정상 범위)
• 풍속: 20kt (주의 단계)
• 시정: 5.0km (양호)

**주의사항:**
- 풍속이 주의 단계에 근접
- 24시간 내 기상 변화 모니터링 필요
- IOI 점수: 75 (GO 조건)"""

    elif "위험" in prompt_lower or "risk" in prompt_lower:
        return """⚠️ **위험 요소 분석**

**현재 위험도: 낮음**
• 기상 위험: 낮음 (파고 1.5m, 풍속 20kt)
• 운항 위험: 낮음 (정상 스케줄 진행)
• 화물 위험: 낮음 (표준 화물)

**권고사항:**
- 정기적인 기상 업데이트 확인
- 선박 상태 점검 유지
- 비상 계획 점검"""

    elif "ioi" in prompt_lower:
        return """📊 **IOI (Index of Interest) 분석**

현재 IOI 점수: **75점** (GO 조건)

**세부 분석:**
• 파고 점수: 85/100 (1.5m - 양호)
• 풍속 점수: 70/100 (20kt - 주의)
• 스웰 주기: 75/100 (8초 - 양호)

**종합 평가:** 운항 가능 조건"""

    else:
        return f"""🤖 **AI 어시스턴트 응답**

질문: "{prompt}"

안녕하세요! 물류 관제탑 AI 어시스턴트입니다.

**제공 서비스:**
• 항차 스케줄 분석 및 최적화
• 기상 조건 모니터링 및 위험 평가
• IOI 점수 계산 및 운항 권고
• 일일 브리핑 및 상황 보고

더 구체적인 질문을 해주시면 상세한 분석을 제공해드리겠습니다.

**예시 질문:**
- "다음 3일 스케줄 요약해줘"
- "현재 기상 조건은 어떤가요?"
- "위험 요소를 분석해줘" """

def generate_daily_briefing(current_time: str, vessel_name: str, vessel_status: str, 
                          current_voyage: str, schedule: List[dict], weather_windows: List[dict]) -> str:
    """
    Generate daily briefing based on vessel and schedule data
    """
    return f"""🌅 **일일 브리핑 - {vessel_name}**

**📅 시간:** {current_time}
**🚢 선박 상태:** {vessel_status}
**📋 현재 항차:** {current_voyage}

---

## 📊 **항차 스케줄 현황**

{generate_schedule_summary(schedule)}

## 🌊 **기상 조건**

{generate_weather_summary(weather_windows)}

## ⚠️ **주의사항 및 권고**

• 정기적인 기상 업데이트 확인 필요
• 선박 상태 점검 및 유지보수
• 화물 적재 준비 상황 점검
• 항만 접안 계획 검토

## 🎯 **오늘의 목표**

• 안전한 운항 준비 완료
• 스케줄 준수 및 지연 방지
• 연료 및 보급품 점검
• 승무원 안전 교육

---
*이 브리핑은 AI 시스템에 의해 자동 생성되었습니다.*"""

def generate_schedule_summary(schedule: List[dict]) -> str:
    """Generate schedule summary"""
    if not schedule:
        return "등록된 항차 스케줄이 없습니다."
    
    summary = ""
    for i, voyage in enumerate(schedule[:3], 1):  # Show first 3 voyages
        voyage_id = voyage.get('id', f'항차{i}')
        cargo = voyage.get('cargo', 'N/A')
        etd = voyage.get('etd', 'N/A')
        eta = voyage.get('eta', 'N/A')
        status = voyage.get('status', 'Scheduled')
        
        summary += f"**{voyage_id} 항차:** {cargo} 화물\n"
        summary += f"  - 출항: {etd}\n"
        summary += f"  - 입항: {eta}\n"
        summary += f"  - 상태: {status}\n\n"
    
    return summary.strip()

def generate_weather_summary(weather_windows: List[dict]) -> str:
    """Generate weather summary"""
    if not weather_windows:
        return "기상 데이터가 업로드되지 않았습니다. CSV 파일을 업로드해주세요."
    
    return """**현재 해상 기상:**
• 파고: 1.5m (정상)
• 풍속: 20kt (주의)
• 시정: 5.0km (양호)

**24시간 예보:**
• 기상 조건 안정적
• 운항에 적합한 조건"""

if __name__ == "__main__":
    import uvicorn
    import os
    
    # 환경변수에서 포트 가져오기 (Railway 등에서 설정)
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Starting Logistics Control Tower API Server...")
    print(f"📡 Server will be available at: http://0.0.0.0:{port}")
    print(f"🔗 Health check: http://0.0.0.0:{port}/health")
    print(f"🤖 AI Assistant: http://0.0.0.0:{port}/api/assistant")
    print(f"📋 Daily Briefing: http://0.0.0.0:{port}/api/briefing")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
