"""
FastAPI Backend for Deal Co-Pilot
Exposes Deep Research Agent as REST API
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, List
import asyncio
import json
from datetime import datetime
import os
import sys
from io import BytesIO

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from deal_copilot.agents.deep_research_agent_openai import DeepResearchAgentOpenAI
from deal_copilot.agents.deep_research_agent import DeepResearchAgent
from deal_copilot.agents.data_room_agent import DataRoomAgent
from deal_copilot.agents.risk_scanner_agent import RiskScannerAgent
from deal_copilot.agents.ic_memo_drafter_agent import ICMemoDrafterAgent

# Initialize FastAPI app
app = FastAPI(
    title="Deal Co-Pilot API",
    description="AI-powered investment due diligence research API",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ResearchRequest(BaseModel):
    """Request model for research generation"""
    prompt: str  # Natural language input from user
    agent_type: Optional[str] = "openai"  # "openai" or "gemini"
    include_data_room: Optional[bool] = False  # Whether to process data room files

class CompanyInfo(BaseModel):
    """Parsed company information"""
    company_name: str
    website: str
    sector: str
    region: str
    hq_location: Optional[str] = None

class ResearchResponse(BaseModel):
    """Response model for research results"""
    report_id: str
    company_info: CompanyInfo
    sections: List[Dict]
    generated_at: str
    agent_type: str

class StatusResponse(BaseModel):
    """Response model for status checks"""
    status: str
    message: str


# ============================================================================
# IN-MEMORY STORAGE (Replace with DB in production)
# ============================================================================

research_jobs = {}  # Store ongoing research jobs
completed_reports = {}  # Store completed reports
excel_files = {}  # Store generated Excel files {report_id: BytesIO}
risk_scanner_reports = {}  # Store risk scanner outputs {report_id: Dict}
ic_memos = {}  # Store IC memo outputs {report_id: Dict}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_natural_language_prompt(prompt: str) -> CompanyInfo:
    """
    Parse natural language prompt to extract company information
    
    Examples:
    - "Analyze Bizzi, a SaaS company in Vietnam at https://bizzi.vn/en/"
    - "Research Grab, a marketplace in Southeast Asia, website: https://grab.com"
    - "Do due diligence on Shopee / E-commerce / Singapore / https://shopee.sg"
    """
    # Simple parsing - in production, use LLM for better extraction
    lines = prompt.lower().replace(",", "\n").split("\n")
    
    info = {
        "company_name": "",
        "website": "",
        "sector": "",
        "region": "",
        "hq_location": None
    }
    
    # Extract company name (usually first word/phrase)
    first_line = lines[0].strip()
    for keyword in ["analyze", "research", "due diligence on", "investigate", "study"]:
        if keyword in first_line:
            first_line = first_line.replace(keyword, "").strip()
    
    words = first_line.split()
    if words:
        info["company_name"] = words[0].capitalize()
    
    # Extract website
    for line in lines:
        if "http" in line or "www" in line:
            parts = line.split()
            for part in parts:
                if "http" in part or "www" in part:
                    info["website"] = part.strip()
                    break
    
    # Extract sector
    sectors = ["saas", "fintech", "marketplace", "healthtech", "edtech", "e-commerce", "ecommerce"]
    for line in lines:
        for sector in sectors:
            if sector in line:
                info["sector"] = sector.upper() if sector == "saas" else sector.capitalize()
                break
    
    # Extract region
    regions = ["vietnam", "singapore", "southeast asia", "sea", "indonesia", "thailand", "philippines"]
    for line in lines:
        for region in regions:
            if region in line:
                info["region"] = region.title()
                break
    
    # Validation
    if not info["company_name"]:
        raise ValueError("Could not extract company name from prompt")
    if not info["website"]:
        raise ValueError("Could not extract website from prompt. Please include website URL.")
    if not info["sector"]:
        info["sector"] = "Technology"  # Default
    if not info["region"]:
        info["region"] = "Global"  # Default
    
    return CompanyInfo(**info)


async def generate_research_async(
    report_id: str,
    company_info: CompanyInfo,
    agent_type: str
):
    """
    Generate research report asynchronously
    Updates research_jobs dict with progress
    """
    try:
        research_jobs[report_id]["status"] = "processing"
        research_jobs[report_id]["message"] = "Initializing agent..."
        
        # Initialize agent based on type
        if agent_type == "openai":
            agent = DeepResearchAgentOpenAI()
        else:
            agent = DeepResearchAgent()
        
        research_jobs[report_id]["message"] = "Generating research report..."
        
        # Generate report (this is synchronous, so we run in executor)
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(
            None,
            agent.generate_full_report,
            company_info.company_name,
            company_info.website,
            company_info.sector,
            company_info.region,
            company_info.hq_location
        )
        
        # Store completed report
        completed_reports[report_id] = report
        research_jobs[report_id]["status"] = "completed"
        research_jobs[report_id]["message"] = "Research complete!"
        research_jobs[report_id]["report"] = report
        
    except Exception as e:
        research_jobs[report_id]["status"] = "failed"
        research_jobs[report_id]["message"] = f"Error: {str(e)}"
        research_jobs[report_id]["error"] = str(e)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API is running"""
    return {
        "message": "Deal Co-Pilot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/research", response_model=Dict)
async def create_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a new research job from natural language prompt
    
    Example:
    ```json
    {
        "prompt": "Analyze Bizzi, a SaaS company in Vietnam. Website: https://bizzi.vn/en/",
        "agent_type": "openai"
    }
    ```
    """
    try:
        # Parse the natural language prompt
        company_info = parse_natural_language_prompt(request.prompt)
        
        # Generate unique report ID
        report_id = f"report_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Initialize job tracking
        research_jobs[report_id] = {
            "status": "queued",
            "message": "Research job queued",
            "company_info": company_info.dict(),
            "agent_type": request.agent_type,
            "created_at": datetime.now().isoformat()
        }
        
        # Start background task
        background_tasks.add_task(
            generate_research_async,
            report_id,
            company_info,
            request.agent_type
        )
        
        return {
            "report_id": report_id,
            "status": "queued",
            "message": "Research job started",
            "company_info": company_info.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/research/{report_id}/status")
async def get_research_status(report_id: str):
    """
    Get the status of a research job with progress information
    """
    if report_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Report not found")
    
    job = research_jobs[report_id]
    
    response = {
        "report_id": report_id,
        "status": job["status"],
        "message": job["message"],
        "progress": job.get("progress", 0),  # Progress percentage
        "current_step": job.get("current_step", ""),  # Current processing step
        "company_info": job.get("company_info"),
        "company_name": job.get("company_name"),
        "created_at": job.get("created_at"),
        "job_type": job.get("type", "research")  # research or dataroom
    }
    
    # If completed, include report summary
    if job["status"] == "completed" and "report" in job:
        report = job["report"]
        if "sections" in report:  # Deep research report
            response["sections_count"] = len(report.get("sections", []))
        if "files_processed" in report:  # Data room report
            response["files_processed"] = report.get("files_processed")
            response["has_excel"] = job.get("has_excel", False)
    
    # Include error details if failed
    if job["status"] == "failed":
        response["error"] = job.get("error", "Unknown error")
    
    return response


@app.get("/api/research/{report_id}")
async def get_research_report(report_id: str):
    """
    Get the completed research report
    """
    if report_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Report not found")
    
    job = research_jobs[report_id]
    
    if job["status"] != "completed":
        return {
            "report_id": report_id,
            "status": job["status"],
            "message": job["message"]
        }
    
    if "report" not in job:
        raise HTTPException(status_code=500, detail="Report data missing")
    
    return {
        "report_id": report_id,
        "status": "completed",
        "report": job["report"]
    }


@app.get("/api/research")
async def list_research_jobs():
    """
    List all research jobs
    """
    jobs = []
    for report_id, job in research_jobs.items():
        jobs.append({
            "report_id": report_id,
            "status": job["status"],
            "company_name": job.get("company_info", {}).get("company_name"),
            "created_at": job.get("created_at")
        })
    
    return {"jobs": jobs, "total": len(jobs)}


@app.post("/api/dataroom")
async def process_data_room(
    files: List[UploadFile] = File(...),
    company_name: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Process data room files and extract qualitative/quantitative data
    
    Accepts:
    - PDF files (pitch decks, contracts)
    - Excel files (financials, KPIs, cap table)
    - PowerPoint files (presentations)
    """
    try:
        # Generate unique report ID
        report_id = f"dataroom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Validate files
        allowed_extensions = {'.pdf', '.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.doc'}
        processed_files = []
        
        for file in files:
            filename = file.filename
            ext = os.path.splitext(filename)[1].lower()
            
            if ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type not supported: {filename}. Allowed: PDF, Excel, PowerPoint, Word"
                )
            
            # Read file content
            content = await file.read()
            
            # Determine file type
            if ext in ['.pdf']:
                file_type = 'pdf'
            elif ext in ['.xlsx', '.xls']:
                file_type = 'excel'
            elif ext in ['.pptx', '.ppt']:
                file_type = 'powerpoint'
            elif ext in ['.docx', '.doc']:
                file_type = 'docx'
            else:
                file_type = 'unknown'
            
            processed_files.append({
                "filename": filename,
                "content": content,
                "file_type": file_type,
                "size": len(content)
            })
        
        # Initialize job tracking
        research_jobs[report_id] = {
            "status": "queued",
            "message": "Data room processing queued",
            "company_name": company_name,
            "files_count": len(processed_files),
            "created_at": datetime.now().isoformat(),
            "type": "dataroom"
        }
        
        # Start background task
        background_tasks.add_task(
            process_data_room_async,
            report_id,
            processed_files,
            company_name
        )
        
        return {
            "report_id": report_id,
            "status": "queued",
            "message": "Data room processing started",
            "files_processed": len(processed_files),
            "company_name": company_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


async def process_data_room_async(
    report_id: str,
    files: List[Dict],
    company_name: str
):
    """Process data room files asynchronously with progress updates"""
    try:
        research_jobs[report_id]["status"] = "processing"
        research_jobs[report_id]["message"] = "Initializing data room analysis..."
        research_jobs[report_id]["progress"] = 0
        research_jobs[report_id]["current_step"] = "initialization"
        
        # Progress callback to update job status
        def progress_callback(step: str, progress: int, message: str):
            research_jobs[report_id]["progress"] = progress
            research_jobs[report_id]["current_step"] = step
            research_jobs[report_id]["message"] = message
        
        # Initialize Data Room Agent with progress callback
        agent = DataRoomAgent(progress_callback=progress_callback)
        
        research_jobs[report_id]["message"] = "Processing files..."
        
        # Process all files (this is synchronous, so run in executor)
        loop = asyncio.get_event_loop()
        report = await loop.run_in_executor(
            None,
            agent.process_data_room,
            files,
            company_name
        )
        
        # Store completed report
        completed_reports[report_id] = report
        research_jobs[report_id]["status"] = "completed"
        research_jobs[report_id]["progress"] = 100
        research_jobs[report_id]["current_step"] = "completed"
        research_jobs[report_id]["message"] = "Data room analysis complete!"
        research_jobs[report_id]["report"] = report
        
        # Store Excel file if generated
        if "excel_file" in report and report["excel_file"]:
            excel_files[report_id] = report["excel_file"]
            research_jobs[report_id]["has_excel"] = True
        
    except Exception as e:
        error_msg = str(e)
        research_jobs[report_id]["status"] = "failed"
        research_jobs[report_id]["progress"] = -1
        research_jobs[report_id]["current_step"] = "error"
        
        # Better error messages
        if "timeout" in error_msg.lower() or "deadline" in error_msg.lower():
            research_jobs[report_id]["message"] = f"Processing timed out. Files may be too large. Try splitting into smaller batches."
        elif "empty response" in error_msg.lower():
            research_jobs[report_id]["message"] = f"AI model returned empty response. This may be due to content filters or API issues."
        else:
            research_jobs[report_id]["message"] = f"Error: {error_msg}"
        
        research_jobs[report_id]["error"] = error_msg


@app.get("/api/dataroom/{report_id}/excel")
async def download_excel(report_id: str):
    """
    Download the Excel file for a data room report
    """
    if report_id not in excel_files:
        raise HTTPException(status_code=404, detail="Excel file not found for this report")
    
    # Get the Excel file
    excel_buffer = excel_files[report_id]
    
    # Reset buffer position
    excel_buffer.seek(0)
    
    # Get company name for filename
    company_name = "Company"
    if report_id in research_jobs:
        company_name = research_jobs[report_id].get("company_name", "Company")
    
    # Clean company name for filename
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_name}_Financial_Data.xlsx"
    
    return StreamingResponse(
        BytesIO(excel_buffer.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ============================================================================
# COMPLETE ANALYSIS ENDPOINTS (All Agents)
# ============================================================================

@app.post("/api/complete-analysis")
async def create_complete_analysis(
    files: List[UploadFile] = File(...),
    prompt: str = Form(...),
    agent_type: str = Form("openai"),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Run complete analysis: Deep Research + Data Room + Risk Scanner + IC Memo
    
    This orchestrates all agents in sequence and generates the final IC memo.
    """
    try:
        # Parse company info
        company_info = parse_natural_language_prompt(prompt)
        company_name = company_info.company_name
        
        # Generate unique report ID
        report_id = f"complete_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Process uploaded files
        processed_files = []
        for file in files:
            filename = file.filename
            content = await file.read()
            ext = os.path.splitext(filename)[1].lower()
            
            if ext in ['.pdf']:
                file_type = 'pdf'
            elif ext in ['.xlsx', '.xls']:
                file_type = 'excel'
            elif ext in ['.pptx', '.ppt']:
                file_type = 'powerpoint'
            elif ext in ['.docx', '.doc']:
                file_type = 'docx'
            else:
                continue
            
            processed_files.append({
                "filename": filename,
                "content": content,
                "file_type": file_type,
                "size": len(content)
            })
        
        # Initialize job tracking
        research_jobs[report_id] = {
            "status": "queued",
            "message": "Complete analysis queued",
            "progress": 0,
            "current_step": "initialization",
            "company_info": company_info.dict(),
            "company_name": company_name,
            "agent_type": agent_type,
            "files_count": len(processed_files),
            "created_at": datetime.now().isoformat(),
            "type": "complete_analysis"
        }
        
        # Start background task
        background_tasks.add_task(
            run_complete_analysis_async,
            report_id,
            company_info,
            processed_files,
            agent_type
        )
        
        return {
            "report_id": report_id,
            "status": "queued",
            "message": "Complete analysis started",
            "company_info": company_info.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


async def run_complete_analysis_async(
    report_id: str,
    company_info,
    files: List[Dict],
    agent_type: str
):
    """Run all agents in sequence"""
    try:
        research_jobs[report_id]["status"] = "processing"
        research_jobs[report_id]["message"] = "Starting complete analysis..."
        research_jobs[report_id]["progress"] = 0
        
        # Progress callback
        def progress_callback(step: str, progress: int, message: str):
            research_jobs[report_id]["progress"] = progress
            research_jobs[report_id]["current_step"] = step
            research_jobs[report_id]["message"] = message
        
        loop = asyncio.get_event_loop()
        
        # Step 1: Deep Research (0-25%)
        research_jobs[report_id]["message"] = "Running deep research..."
        research_jobs[report_id]["current_step"] = "deep_research"
        research_jobs[report_id]["progress"] = 5
        
        if agent_type == "openai":
            deep_agent = DeepResearchAgentOpenAI()
        else:
            deep_agent = DeepResearchAgent()
        
        deep_report = await loop.run_in_executor(
            None,
            deep_agent.generate_full_report,
            company_info.company_name,
            company_info.website,
            company_info.sector,
            company_info.region,
            company_info.hq_location
        )
        research_jobs[report_id]["progress"] = 25
        
        # Step 2: Data Room (25-50%)
        research_jobs[report_id]["message"] = "Processing data room files..."
        research_jobs[report_id]["current_step"] = "data_room"
        
        data_room_agent = DataRoomAgent(progress_callback=progress_callback)
        data_room_report = await loop.run_in_executor(
            None,
            data_room_agent.process_data_room,
            files,
            company_info.company_name
        )
        research_jobs[report_id]["progress"] = 50
        
        # Step 3: Risk Scanner (50-70%)
        research_jobs[report_id]["message"] = "Scanning for risks..."
        research_jobs[report_id]["current_step"] = "risk_scanner"
        
        risk_agent = RiskScannerAgent(progress_callback=progress_callback)
        risk_report = await loop.run_in_executor(
            None,
            risk_agent.scan_risks,
            company_info.company_name,
            deep_report,
            data_room_report
        )
        research_jobs[report_id]["progress"] = 70
        
        # Step 4: IC Memo Drafter (70-95%)
        research_jobs[report_id]["message"] = "Drafting IC memo..."
        research_jobs[report_id]["current_step"] = "ic_memo"
        
        ic_agent = ICMemoDrafterAgent(progress_callback=progress_callback)
        ic_memo = await loop.run_in_executor(
            None,
            ic_agent.draft_memo,
            company_info.company_name,
            company_info.dict(),
            deep_report,
            data_room_report,
            risk_report
        )
        research_jobs[report_id]["progress"] = 95
        
        # Store all outputs
        completed_reports[report_id] = {
            "deep_research": deep_report,
            "data_room": data_room_report,
            "risk_scanner": risk_report,
            "ic_memo": ic_memo
        }
        
        risk_scanner_reports[report_id] = risk_report
        ic_memos[report_id] = ic_memo
        
        if "excel_file" in data_room_report and data_room_report["excel_file"]:
            excel_files[report_id] = data_room_report["excel_file"]
        
        # Complete
        research_jobs[report_id]["status"] = "completed"
        research_jobs[report_id]["progress"] = 100
        research_jobs[report_id]["current_step"] = "completed"
        research_jobs[report_id]["message"] = "Complete analysis finished!"
        research_jobs[report_id]["has_ic_memo"] = True
        research_jobs[report_id]["has_risk_report"] = True
        research_jobs[report_id]["has_excel"] = report_id in excel_files
        
    except Exception as e:
        research_jobs[report_id]["status"] = "failed"
        research_jobs[report_id]["progress"] = -1
        research_jobs[report_id]["current_step"] = "error"
        research_jobs[report_id]["message"] = f"Error: {str(e)}"
        research_jobs[report_id]["error"] = str(e)


@app.get("/api/analysis/{report_id}/ic-memo")
async def get_ic_memo(report_id: str):
    """Get the IC memo for a report"""
    if report_id not in ic_memos:
        raise HTTPException(status_code=404, detail="IC memo not found")
    
    return ic_memos[report_id]


@app.get("/api/analysis/{report_id}/risk-report")
async def get_risk_report(report_id: str):
    """Get the risk scanner report"""
    if report_id not in risk_scanner_reports:
        raise HTTPException(status_code=404, detail="Risk report not found")
    
    return risk_scanner_reports[report_id]


@app.get("/api/analysis/{report_id}/full")
async def get_full_analysis(report_id: str):
    """Get all agent outputs for a complete analysis"""
    if report_id not in completed_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return completed_reports[report_id]


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)



