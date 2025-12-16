"""
FastAPI Backend for Deal Co-Pilot
Exposes Deep Research Agent as REST API
Human-in-the-Loop workflow with SSE streaming
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
from sse_starlette.sse import EventSourceResponse

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

# Workflow state for human-in-the-loop
workflow_states = {}  # {report_id: WorkflowState}

class WorkflowState:
    """Track the state of a step-by-step analysis workflow"""
    ALL_STEPS = ["deep_research", "data_room", "risk_scanner", "ic_memo"]
    
    def __init__(self, report_id: str, company_info: Dict, files: List[Dict], agent_type: str, 
                 run_deep_research: bool = True, run_data_room: bool = True):
        self.report_id = report_id
        self.company_info = company_info
        self.files = files
        self.agent_type = agent_type
        self.has_files = len(files) > 0
        self.run_deep_research = run_deep_research
        self.run_data_room = run_data_room and self.has_files
        
        # Build steps based on selected agents
        self.steps = []
        if self.run_deep_research:
            self.steps.append("deep_research")
        if self.run_data_room:
            self.steps.append("data_room")
        self.steps.append("risk_scanner")
        self.steps.append("ic_memo")
        
        self.current_step = 0  # Index into steps
        self.step_status = {step: "pending" for step in self.ALL_STEPS}
        
        # Mark skipped steps
        if not self.run_deep_research:
            self.step_status["deep_research"] = "skipped"
        if not self.run_data_room:
            self.step_status["data_room"] = "skipped"
            
        self.step_outputs = {}  # {step_name: output}
        self.awaiting_review = False
        self.cancelled = False  # Track if workflow was cancelled
        self.created_at = datetime.now().isoformat()
    
    def get_current_step_name(self) -> str:
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return "completed"
    
    def to_dict(self) -> Dict:
        return {
            "report_id": self.report_id,
            "company_info": self.company_info,
            "current_step": self.get_current_step_name(),
            "current_step_index": self.current_step,
            "total_steps": len(self.steps),
            "steps": self.steps,
            "has_files": self.has_files,
            "step_status": self.step_status,
            "cancelled": self.cancelled,
            "awaiting_review": self.awaiting_review,
            "created_at": self.created_at,
            "has_outputs": {step: step in self.step_outputs for step in self.ALL_STEPS}
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parse_natural_language_prompt(prompt: str) -> CompanyInfo:
    """
    Parse natural language prompt using LLM to extract company information intelligently
    
    Examples:
    - "Analyze Bizzi, a SaaS company in Vietnam at https://bizzi.vn/en/"
    - "Research Grab, a marketplace in Southeast Asia, website: https://grab.com"
    - "Re.K, HK-based stablecoin company"
    """
    from openai import OpenAI
    from deal_copilot.config import config_openai
    import json
    
    client = OpenAI(api_key=config_openai.OPENAI_API_KEY)
    
    extraction_prompt = f"""Extract company information from this user prompt and return ONLY a JSON object with these exact fields:
{{
  "company_name": "exact company name",
  "website": "full URL if mentioned, otherwise empty string",
  "sector": "specific industry/sector (e.g., 'Fintech', 'Stablecoin', 'E-commerce', 'SaaS', 'Healthcare', 'PropTech')",
  "region": "geographic market (e.g., 'Hong Kong', 'Singapore', 'Southeast Asia', 'United States', 'Vietnam')",
  "hq_location": "headquarters location if mentioned, otherwise null"
}}

User prompt: "{prompt}"

Rules:
- Be SPECIFIC with sector (e.g., "Stablecoin" or "Fintech" not just "Technology")
- Be SPECIFIC with region (e.g., "Hong Kong" not just "Asia")
- Recognize abbreviations (HK = Hong Kong, SG = Singapore, SEA = Southeast Asia, US = United States)
- If website not found, return empty string (don't make one up)
- Return ONLY the JSON object, no other text
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap for extraction
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise data extraction assistant. You extract structured information from text and return only valid JSON."
                },
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        info = json.loads(response.choices[0].message.content)
        
        # Validation
        if not info.get("company_name"):
            raise ValueError("Could not extract company name from prompt")
        
        # Set defaults only if truly empty
        if not info.get("sector"):
            info["sector"] = "Technology"
        if not info.get("region"):
            info["region"] = "Global"
        if not info.get("website"):
            # Website is optional now - agent can search without it
            info["website"] = ""
        
        return CompanyInfo(**info)
        
    except Exception as e:
        print(f"Error in LLM-based parsing: {e}")
        # Fallback: try to extract at least company name
        words = prompt.split()
        if words:
            return CompanyInfo(
                company_name=words[0],
                website="",
                sector="Technology",
                region="Global",
                hq_location=None
            )
        raise ValueError("Could not parse prompt. Please provide company name.")


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


@app.get("/api/dataroom/{report_id}/summary-docx")
async def download_dataroom_summary_docx(report_id: str):
    """
    Download the human-readable data room summary as DOCX
    """
    # Get the full report
    report = None
    if report_id in completed_reports and "data_room" in completed_reports[report_id]:
        report = completed_reports[report_id]["data_room"]
    elif report_id in research_jobs and "report" in research_jobs[report_id]:
        job_report = research_jobs[report_id]["report"]
        if isinstance(job_report, dict) and "data_room" in job_report:
            report = job_report["data_room"]
    
    if not report or "human_readable_summary" not in report:
        raise HTTPException(status_code=404, detail="Data room summary not found for this report")
    
    # Generate DOCX
    from deal_copilot.agents.data_room_agent import DataRoomAgent
    agent = DataRoomAgent()
    docx_buffer = agent.generate_docx_summary(report)
    
    if not docx_buffer:
        raise HTTPException(status_code=500, detail="Failed to generate DOCX file")
    
    # Get company name for filename
    company_name = report.get("company_name", "Company")
    safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip()
    filename = f"{safe_name}_Data_Room_Summary.docx"
    
    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# ============================================================================
# COMPLETE ANALYSIS ENDPOINTS (All Agents)
# ============================================================================

@app.post("/api/complete-analysis")
async def create_complete_analysis(
    prompt: str = Form(...),
    agent_type: str = Form("openai"),
    files: List[UploadFile] = File(default=[]),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Run complete analysis: Deep Research + Data Room (if files) + Risk Scanner + IC Memo
    
    This orchestrates all agents in sequence and generates the final IC memo.
    Data Room agent is skipped if no files are provided.
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
    """Run all agents in sequence. Data Room is skipped if no files provided."""
    try:
        research_jobs[report_id]["status"] = "processing"
        research_jobs[report_id]["message"] = "Starting complete analysis..."
        research_jobs[report_id]["progress"] = 0
        
        has_files = len(files) > 0
        
        # Progress callback
        def progress_callback(step: str, progress: int, message: str):
            research_jobs[report_id]["progress"] = progress
            research_jobs[report_id]["current_step"] = step
            research_jobs[report_id]["message"] = message
        
        loop = asyncio.get_event_loop()
        
        # Step 1: Deep Research (0-30% or 0-40% if no files)
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
        research_jobs[report_id]["progress"] = 30 if has_files else 40
        
        # Step 2: Data Room (30-55%) - SKIP if no files
        data_room_report = None
        if has_files:
            research_jobs[report_id]["message"] = "Processing data room files..."
            research_jobs[report_id]["current_step"] = "data_room"
            
            data_room_agent = DataRoomAgent(progress_callback=progress_callback)
            data_room_report = await loop.run_in_executor(
                None,
                data_room_agent.process_data_room,
                files,
                company_info.company_name
            )
            research_jobs[report_id]["progress"] = 55
        else:
            research_jobs[report_id]["message"] = "Skipping data room (no files provided)..."
            research_jobs[report_id]["current_step"] = "data_room_skipped"
        
        # Step 3: Risk Scanner (55-75% or 40-60% if no files)
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
        research_jobs[report_id]["progress"] = 75 if has_files else 70
        
        # Step 4: IC Memo Drafter (75-95% or 70-95%)
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
        
        if data_room_report and "excel_file" in data_room_report and data_room_report["excel_file"]:
            excel_files[report_id] = data_room_report["excel_file"]
        
        # Complete
        research_jobs[report_id]["status"] = "completed"
        research_jobs[report_id]["progress"] = 100
        research_jobs[report_id]["current_step"] = "completed"
        research_jobs[report_id]["message"] = "Complete analysis finished!"
        research_jobs[report_id]["has_ic_memo"] = True
        research_jobs[report_id]["has_risk_report"] = True
        research_jobs[report_id]["has_excel"] = report_id in excel_files
        research_jobs[report_id]["has_data_room"] = has_files
        
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
# HUMAN-IN-THE-LOOP WORKFLOW ENDPOINTS
# ============================================================================

@app.post("/api/workflow/start")
async def start_workflow(
    prompt: str = Form(...),
    agent_type: str = Form("openai"),
    files: List[UploadFile] = File(default=[]),
    run_deep_research: str = Form("true"),
    run_data_room: str = Form("true")
):
    """
    Start a new step-by-step workflow.
    Returns workflow_id and initiates the first step.
    """
    try:
        # Parse company info
        company_info = parse_natural_language_prompt(prompt)
        company_name = company_info.company_name
        
        # Generate unique workflow ID
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
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
        
        # Parse boolean values
        should_run_deep_research = run_deep_research.lower() == "true"
        should_run_data_room = run_data_room.lower() == "true" and len(processed_files) > 0
        
        # Create workflow state with selected agents
        state = WorkflowState(
            report_id=workflow_id,
            company_info=company_info.dict(),
            files=processed_files,
            agent_type=agent_type,
            run_deep_research=should_run_deep_research,
            run_data_room=should_run_data_room
        )
        workflow_states[workflow_id] = state
        
        # Determine first step
        first_step = state.get_current_step_name()
        
        # Initialize job tracking for status polling
        research_jobs[workflow_id] = {
            "status": "processing",
            "message": f"Starting {first_step.replace('_', ' ')}...",
            "progress": 0,
            "current_step": first_step,
            "company_info": company_info.dict(),
            "company_name": company_name,
            "type": "workflow",
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Workflow started. Connect to SSE endpoint to receive streaming updates.",
            "company_info": company_info.dict(),
            "sse_endpoint": f"/api/workflow/{workflow_id}/stream"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/workflow/{workflow_id}/stream")
async def stream_workflow_step(workflow_id: str):
    """
    SSE endpoint to stream the current step's output.
    Client connects here to receive real-time updates.
    """
    if workflow_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    state = workflow_states[workflow_id]
    
    async def event_generator():
        step_name = state.get_current_step_name()
        
        # Send initial status
        yield {
            "event": "status",
            "data": json.dumps({
                "step": step_name,
                "status": "starting",
                "message": f"Starting {step_name.replace('_', ' ')}..."
            })
        }
        
        try:
            # Run the current step with streaming for all agents
            loop = asyncio.get_event_loop()
            stream_queue = asyncio.Queue()
            
            # Create streaming task for current step
            if step_name == "deep_research":
                output_task = asyncio.create_task(
                    run_deep_research_step_streaming(state, stream_queue, loop)
                )
            elif step_name == "data_room":
                output_task = asyncio.create_task(
                    run_data_room_step_streaming(state, stream_queue, loop)
                )
            elif step_name == "risk_scanner":
                output_task = asyncio.create_task(
                    run_risk_scanner_step_streaming(state, stream_queue, loop)
                )
            elif step_name == "ic_memo":
                output_task = asyncio.create_task(
                    run_ic_memo_step_streaming(state, stream_queue, loop)
                )
            else:
                output_task = None
            
            # Yield chunks as they arrive (for all streaming steps)
            if output_task:
                while True:
                    # Check if workflow was cancelled
                    if state.cancelled:
                        output_task.cancel()
                        yield {
                            "event": "error",
                            "data": json.dumps({
                                "step": step_name,
                                "error": "Workflow cancelled by user"
                            })
                        }
                        return
                    
                    try:
                        chunk = await asyncio.wait_for(stream_queue.get(), timeout=0.1)
                        if chunk is None:  # Sentinel value indicating completion
                            break
                        yield {
                            "event": "chunk",
                            "data": json.dumps({
                                "content": chunk
                            })
                        }
                    except asyncio.TimeoutError:
                        # Check if task is done
                        if output_task.done():
                            break
                        continue
                
                # Get final output
                output = await output_task
            else:
                output = None
            
            # Store output
            if output:
                state.step_outputs[step_name] = output
                state.step_status[step_name] = "completed"
                state.awaiting_review = True
            
            # Send completion event
            yield {
                "event": "step_complete",
                "data": json.dumps({
                    "step": step_name,
                    "status": "completed",
                    "awaiting_review": True,
                    "output_preview": str(output)[:500] if output else None
                })
            }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({
                    "step": step_name,
                    "error": str(e)
                })
            }
    
    return EventSourceResponse(event_generator())


async def event_generator_helper(event_type: str, data: Dict):
    """Helper to yield SSE events from within agent execution"""
    return {
        "event": event_type,
        "data": json.dumps(data)
    }


async def run_deep_research_step(state: WorkflowState, yield_event) -> Dict:
    """Run deep research agent (non-streaming version)"""
    company_info = state.company_info
    
    # Update job status
    research_jobs[state.report_id]["message"] = "Running deep research..."
    research_jobs[state.report_id]["current_step"] = "deep_research"
    
    loop = asyncio.get_event_loop()
    
    if state.agent_type == "openai":
        agent = DeepResearchAgentOpenAI()
    else:
        agent = DeepResearchAgent()
    
    report = await loop.run_in_executor(
        None,
        agent.generate_full_report,
        company_info["company_name"],
        company_info["website"],
        company_info["sector"],
        company_info["region"],
        company_info.get("hq_location")
    )
    
    return report


async def run_deep_research_step_streaming(state: WorkflowState, stream_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> Dict:
    """Run deep research agent with streaming support"""
    company_info = state.company_info
    
    # Update job status
    research_jobs[state.report_id]["message"] = "Running deep research..."
    research_jobs[state.report_id]["current_step"] = "deep_research"
    
    def stream_callback(chunk: str):
        """Put streaming chunk in queue from synchronous context"""
        asyncio.run_coroutine_threadsafe(stream_queue.put(chunk), loop)
    
    if state.agent_type == "openai":
        agent = DeepResearchAgentOpenAI(stream_callback=stream_callback)
    else:
        agent = DeepResearchAgent()  # Gemini version doesn't support streaming yet
    
    report = await loop.run_in_executor(
        None,
        agent.generate_full_report,
        company_info["company_name"],
        company_info["website"],
        company_info["sector"],
        company_info["region"],
        company_info.get("hq_location")
    )
    
    # Signal completion
    await stream_queue.put(None)
    
    return report


async def run_data_room_step(state: WorkflowState, yield_event) -> Dict:
    """Run data room agent (non-streaming version)"""
    research_jobs[state.report_id]["message"] = "Processing data room files..."
    research_jobs[state.report_id]["current_step"] = "data_room"
    
    loop = asyncio.get_event_loop()
    
    def progress_callback(step: str, progress: int, message: str):
        research_jobs[state.report_id]["progress"] = progress
        research_jobs[state.report_id]["message"] = message
    
    agent = DataRoomAgent(progress_callback=progress_callback)
    report = await loop.run_in_executor(
        None,
        agent.process_data_room,
        state.files,
        state.company_info["company_name"]
    )
    
    # Store excel file if generated
    if "excel_file" in report and report["excel_file"]:
        excel_files[state.report_id] = report["excel_file"]
    
    return report


async def run_data_room_step_streaming(state: WorkflowState, stream_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> Dict:
    """Run data room agent with streaming support"""
    research_jobs[state.report_id]["message"] = "Processing data room files..."
    research_jobs[state.report_id]["current_step"] = "data_room"
    
    def progress_callback(step: str, progress: int, message: str):
        research_jobs[state.report_id]["progress"] = progress
        research_jobs[state.report_id]["message"] = message
    
    def stream_callback(chunk: str):
        """Put streaming chunk in queue from synchronous context"""
        asyncio.run_coroutine_threadsafe(stream_queue.put(chunk), loop)
    
    agent = DataRoomAgent(
        progress_callback=progress_callback,
        stream_callback=stream_callback
    )
    
    report = await loop.run_in_executor(
        None,
        agent.process_data_room,
        state.files,
        state.company_info["company_name"]
    )
    
    # Signal completion
    await stream_queue.put(None)
    
    # Store excel file if generated
    if "excel_file" in report and report["excel_file"]:
        excel_files[state.report_id] = report["excel_file"]
    
    return report


async def run_risk_scanner_step(state: WorkflowState, yield_event) -> Dict:
    """Run risk scanner agent (non-streaming version)"""
    research_jobs[state.report_id]["message"] = "Scanning for risks..."
    research_jobs[state.report_id]["current_step"] = "risk_scanner"
    
    loop = asyncio.get_event_loop()
    
    def progress_callback(step: str, progress: int, message: str):
        research_jobs[state.report_id]["progress"] = progress
        research_jobs[state.report_id]["message"] = message
    
    agent = RiskScannerAgent(progress_callback=progress_callback)
    
    deep_research = state.step_outputs.get("deep_research", {})
    data_room = state.step_outputs.get("data_room", {})
    
    report = await loop.run_in_executor(
        None,
        agent.scan_risks,
        state.company_info["company_name"],
        deep_research,
        data_room
    )
    
    risk_scanner_reports[state.report_id] = report
    return report


async def run_risk_scanner_step_streaming(state: WorkflowState, stream_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> Dict:
    """Run risk scanner agent with streaming support"""
    research_jobs[state.report_id]["message"] = "Scanning for risks..."
    research_jobs[state.report_id]["current_step"] = "risk_scanner"
    
    def progress_callback(step: str, progress: int, message: str):
        research_jobs[state.report_id]["progress"] = progress
        research_jobs[state.report_id]["message"] = message
    
    def stream_callback(chunk: str):
        """Put streaming chunk in queue from synchronous context"""
        asyncio.run_coroutine_threadsafe(stream_queue.put(chunk), loop)
    
    agent = RiskScannerAgent(
        progress_callback=progress_callback,
        stream_callback=stream_callback
    )
    
    deep_research = state.step_outputs.get("deep_research", {})
    data_room = state.step_outputs.get("data_room", {})
    
    report = await loop.run_in_executor(
        None,
        agent.scan_risks,
        state.company_info["company_name"],
        deep_research,
        data_room
    )
    
    # Signal completion
    await stream_queue.put(None)
    
    risk_scanner_reports[state.report_id] = report
    return report


async def run_ic_memo_step(state: WorkflowState, yield_event) -> Dict:
    """Run IC memo drafter agent with streaming updates"""
    research_jobs[state.report_id]["message"] = "Drafting IC memo..."
    research_jobs[state.report_id]["current_step"] = "ic_memo"
    
    loop = asyncio.get_event_loop()
    
    def progress_callback(step: str, progress: int, message: str):
        research_jobs[state.report_id]["progress"] = progress
        research_jobs[state.report_id]["message"] = message
    
    agent = ICMemoDrafterAgent(progress_callback=progress_callback)
    
    deep_research = state.step_outputs.get("deep_research", {})
    data_room = state.step_outputs.get("data_room", {})
    risk_scanner = state.step_outputs.get("risk_scanner", {})
    
    memo = await loop.run_in_executor(
        None,
        agent.draft_memo,
        state.company_info["company_name"],
        state.company_info,
        deep_research,
        data_room,
        risk_scanner
    )
    
    ic_memos[state.report_id] = memo
    return memo


async def run_ic_memo_step_streaming(state: WorkflowState, stream_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop) -> Dict:
    """Run IC memo drafter agent with streaming support"""
    research_jobs[state.report_id]["message"] = "Drafting IC memo..."
    research_jobs[state.report_id]["current_step"] = "ic_memo"
    
    def progress_callback(step: str, progress: int, message: str):
        research_jobs[state.report_id]["progress"] = progress
        research_jobs[state.report_id]["message"] = message
    
    def stream_callback(chunk: str):
        """Put streaming chunk in queue from synchronous context"""
        asyncio.run_coroutine_threadsafe(stream_queue.put(chunk), loop)
    
    agent = ICMemoDrafterAgent(
        progress_callback=progress_callback,
        stream_callback=stream_callback
    )
    
    deep_research = state.step_outputs.get("deep_research", {})
    data_room = state.step_outputs.get("data_room", {})
    risk_scanner = state.step_outputs.get("risk_scanner", {})
    
    # Run in executor (synchronous but with streaming callback)
    memo = await loop.run_in_executor(
        None,
        agent.draft_memo,
        state.company_info["company_name"],
        state.company_info,
        deep_research,
        data_room,
        risk_scanner
    )
    
    # Signal completion
    await stream_queue.put(None)
    
    ic_memos[state.report_id] = memo
    return memo


@app.get("/api/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get the current workflow state"""
    if workflow_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    state = workflow_states[workflow_id]
    return state.to_dict()


@app.get("/api/workflow/{workflow_id}/output/{step_name}")
async def get_step_output(workflow_id: str, step_name: str):
    """Get the output of a specific step"""
    if workflow_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    state = workflow_states[workflow_id]
    
    if step_name not in state.step_outputs:
        raise HTTPException(status_code=404, detail=f"Output for {step_name} not available")
    
    return {
        "step": step_name,
        "status": state.step_status.get(step_name, "unknown"),
        "output": state.step_outputs[step_name]
    }


@app.post("/api/workflow/{workflow_id}/continue")
async def continue_workflow(workflow_id: str):
    """
    User approves current step output and continues to next step.
    """
    if workflow_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    state = workflow_states[workflow_id]
    
    if not state.awaiting_review:
        raise HTTPException(status_code=400, detail="Workflow is not awaiting review")
    
    # Move to next step
    state.current_step += 1
    state.awaiting_review = False
    
    current_step = state.get_current_step_name()
    
    if current_step == "completed":
        # Store final outputs
        completed_reports[workflow_id] = {
            "deep_research": state.step_outputs.get("deep_research"),
            "data_room": state.step_outputs.get("data_room"),
            "risk_scanner": state.step_outputs.get("risk_scanner"),
            "ic_memo": state.step_outputs.get("ic_memo")
        }
        
        research_jobs[workflow_id]["status"] = "completed"
        research_jobs[workflow_id]["progress"] = 100
        research_jobs[workflow_id]["message"] = "Workflow completed!"
        
        return {
            "status": "completed",
            "message": "All steps completed!",
            "report_id": workflow_id
        }
    
    return {
        "status": "continuing",
        "next_step": current_step,
        "message": f"Moving to {current_step.replace('_', ' ')}",
        "sse_endpoint": f"/api/workflow/{workflow_id}/stream"
    }


class RefineRequest(BaseModel):
    feedback: str


@app.post("/api/workflow/{workflow_id}/refine/{step_name}")
async def refine_step(workflow_id: str, step_name: str, request: RefineRequest):
    """
    User provides feedback to refine the current step output.
    The step will be re-run with the feedback incorporated.
    """
    if workflow_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    state = workflow_states[workflow_id]
    
    if step_name not in WorkflowState.ALL_STEPS:
        raise HTTPException(status_code=400, detail=f"Invalid step: {step_name}")
    
    # Store feedback for refinement
    state.step_status[step_name] = "refining"
    state.awaiting_review = False
    
    # Clear previous output so it can be regenerated
    if step_name in state.step_outputs:
        del state.step_outputs[step_name]
    
    # Update job status
    research_jobs[workflow_id]["message"] = f"Refining {step_name} with feedback..."
    research_jobs[workflow_id]["current_step"] = step_name
    
    return {
        "status": "refining",
        "step": step_name,
        "feedback_received": request.feedback,
        "message": f"Refining {step_name}. Connect to SSE endpoint to receive updates.",
        "sse_endpoint": f"/api/workflow/{workflow_id}/stream"
    }


@app.post("/api/workflow/{workflow_id}/skip/{step_name}")
async def skip_step(workflow_id: str, step_name: str):
    """
    Skip the current step and move to the next one.
    """
    if workflow_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    state = workflow_states[workflow_id]
    
    if step_name != state.get_current_step_name():
        raise HTTPException(status_code=400, detail=f"Cannot skip {step_name}, current step is {state.get_current_step_name()}")
    
    # Mark as skipped and move on
    state.step_status[step_name] = "skipped"
    state.current_step += 1
    state.awaiting_review = False
    
    next_step = state.get_current_step_name()
    
    return {
        "status": "skipped",
        "skipped_step": step_name,
        "next_step": next_step,
        "message": f"Skipped {step_name}, moving to {next_step}"
    }


@app.post("/api/workflow/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str):
    """
    Cancel the workflow and stop all processing.
    """
    if workflow_id not in workflow_states:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    state = workflow_states[workflow_id]
    
    # Mark workflow as cancelled
    state.cancelled = True
    state.awaiting_review = False
    
    # Update current step status
    current_step = state.get_current_step_name()
    if current_step != "completed":
        state.step_status[current_step] = "cancelled"
    
    # Update job tracking
    if workflow_id in research_jobs:
        research_jobs[workflow_id]["status"] = "cancelled"
        research_jobs[workflow_id]["message"] = "Workflow cancelled by user"
    
    return {
        "status": "cancelled",
        "message": "Workflow has been cancelled",
        "workflow_id": workflow_id
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)



