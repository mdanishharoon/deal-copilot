import type { ResearchResponse, StatusResponse, ReportResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createResearch(
  prompt: string,
  agentType: string = "openai"
): Promise<ResearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/research`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      agent_type: agentType,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create research");
  }

  return response.json();
}

export async function checkStatus(reportId: string): Promise<StatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/research/${reportId}/status`);

  if (!response.ok) {
    throw new Error("Failed to check status");
  }

  return response.json();
}

export async function getReport(reportId: string): Promise<ReportResponse> {
  const response = await fetch(`${API_BASE_URL}/api/research/${reportId}`);

  if (!response.ok) {
    throw new Error("Failed to get report");
  }

  return response.json();
}

export async function uploadDataRoom(
  files: File[],
  companyName: string
): Promise<any> {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('company_name', companyName);

  const response = await fetch(`${API_BASE_URL}/api/dataroom`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to upload data room files");
  }

  return response.json();
}

export async function createCompleteAnalysis(
  prompt: string,
  files: File[],
  agentType: string = "openai"
): Promise<ResearchResponse> {
  const formData = new FormData();
  
  // Only append files if there are any
  if (files.length > 0) {
    files.forEach((file) => {
      formData.append('files', file);
    });
  }
  formData.append('prompt', prompt);
  formData.append('agent_type', agentType);

  const response = await fetch(`${API_BASE_URL}/api/complete-analysis`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create complete analysis");
  }

  return response.json();
}

export async function getICMemo(reportId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${reportId}/ic-memo`);

  if (!response.ok) {
    throw new Error("Failed to get IC memo");
  }

  return response.json();
}

export async function getRiskReport(reportId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${reportId}/risk-report`);

  if (!response.ok) {
    throw new Error("Failed to get risk report");
  }

  return response.json();
}

export async function getFullAnalysis(reportId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${reportId}/full`);

  if (!response.ok) {
    throw new Error("Failed to get full analysis");
  }

  return response.json();
}

// ============================================================================
// WORKFLOW API (Human-in-the-Loop)
// ============================================================================

export async function startWorkflow(
  prompt: string,
  files: File[],
  agentType: string = "openai"
): Promise<{ workflow_id: string; company_info: any; sse_endpoint: string }> {
  const formData = new FormData();
  
  // Only append files if there are any
  if (files.length > 0) {
    files.forEach((file) => {
      formData.append('files', file);
    });
  }
  formData.append('prompt', prompt);
  formData.append('agent_type', agentType);

  const response = await fetch(`${API_BASE_URL}/api/workflow/start`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to start workflow");
  }

  return response.json();
}

export async function getWorkflowStatus(workflowId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/workflow/${workflowId}/status`);

  if (!response.ok) {
    throw new Error("Failed to get workflow status");
  }

  return response.json();
}

export async function getStepOutput(workflowId: string, stepName: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/workflow/${workflowId}/output/${stepName}`);

  if (!response.ok) {
    throw new Error(`Failed to get output for ${stepName}`);
  }

  return response.json();
}

export async function continueWorkflow(workflowId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/workflow/${workflowId}/continue`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to continue workflow");
  }

  return response.json();
}

export async function refineStep(workflowId: string, stepName: string, feedback: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/workflow/${workflowId}/refine/${stepName}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ feedback }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to refine step");
  }

  return response.json();
}

export async function skipStep(workflowId: string, stepName: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/workflow/${workflowId}/skip/${stepName}`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to skip step");
  }

  return response.json();
}

export function createSSEConnection(
  workflowId: string,
  onMessage: (event: string, data: any) => void,
  onError: (error: any) => void
): EventSource {
  const eventSource = new EventSource(`${API_BASE_URL}/api/workflow/${workflowId}/stream`);
  
  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage("message", data);
    } catch (e) {
      console.error("Failed to parse SSE message:", e);
    }
  };
  
  eventSource.addEventListener("status", (event: any) => {
    try {
      const data = JSON.parse(event.data);
      onMessage("status", data);
    } catch (e) {
      console.error("Failed to parse status event:", e);
    }
  });
  
  eventSource.addEventListener("step_complete", (event: any) => {
    try {
      const data = JSON.parse(event.data);
      onMessage("step_complete", data);
    } catch (e) {
      console.error("Failed to parse step_complete event:", e);
    }
  });
  
  eventSource.addEventListener("chunk", (event: any) => {
    try {
      const data = JSON.parse(event.data);
      onMessage("chunk", data);
    } catch (e) {
      console.error("Failed to parse chunk event:", e);
    }
  });
  
  eventSource.addEventListener("error", (event: any) => {
    try {
      const data = JSON.parse(event.data);
      onMessage("error", data);
    } catch (e) {
      onError(event);
    }
  });
  
  eventSource.onerror = onError;
  
  return eventSource;
}

export async function downloadReport(reportId: string, companyName: string) {
  const report = await getReport(reportId);
  
  if (report.report) {
    const content = formatReportAsText(report.report);
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${companyName}_research_report.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

export async function downloadICMemo(reportId: string, companyName: string) {
  const memo = await getICMemo(reportId);
  
  if (memo.memo_content) {
    const content = memo.memo_content.content;
    const blob = new Blob([content], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${companyName}_IC_Memo.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

export async function downloadRiskReport(reportId: string, companyName: string) {
  const risk = await getRiskReport(reportId);
  
  if (risk.risk_analysis) {
    const content = JSON.stringify(risk.risk_analysis.structured_data, null, 2);
    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${companyName}_Risk_Report.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

function formatReportAsText(report: any): string {
  let text = "================================================================================\n";
  text += `DEEP RESEARCH REPORT\n`;
  text += "================================================================================\n\n";
  text += `Company: ${report.company_name}\n`;
  text += `Sector: ${report.sector}\n`;
  text += `Region: ${report.region}\n`;
  text += `Website: ${report.website}\n`;
  text += `Generated: ${report.generated_at}\n\n`;
  text += "================================================================================\n\n";

  report.sections.forEach((section: any) => {
    text += `\n## ${section.section}\n\n`;
    text += `${section.content}\n\n`;
    text += "--------------------------------------------------------------------------------\n";
  });

  return text;
}

