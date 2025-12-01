"use client";

import { useState, useEffect, useRef } from "react";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import LoadingSection from "@/components/LoadingSection";
import ResultsSection from "@/components/ResultsSection";
import WorkflowSection from "@/components/WorkflowSection";
import { 
  createCompleteAnalysis, 
  checkStatus, 
  getICMemo, 
  getFullAnalysis,
  startWorkflow,
  getWorkflowStatus,
  getStepOutput,
  continueWorkflow,
  refineStep,
  skipStep,
  createSSEConnection
} from "@/lib/api";
import type { CompanyInfo } from "@/lib/types";

type WorkflowMode = "auto" | "step-by-step";

export default function Home() {
  // Common state
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [reportId, setReportId] = useState<string | null>(null);
  const [icMemo, setICMemo] = useState<any | null>(null);
  const [fullAnalysis, setFullAnalysis] = useState<any | null>(null);
  
  // Workflow mode state
  const [workflowMode, setWorkflowMode] = useState<WorkflowMode>("step-by-step");
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [stepStatus, setStepStatus] = useState<Record<string, string>>({});
  const [stepOutput, setStepOutput] = useState<any>(null);
  const [streamingContent, setStreamingContent] = useState<string>("");
  const [isProcessingStep, setIsProcessingStep] = useState(false);
  const [awaitingReview, setAwaitingReview] = useState(false);
  const [activeSteps, setActiveSteps] = useState<string[]>([]);
  
  const eventSourceRef = useRef<EventSource | null>(null);

  // Cleanup SSE on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const handleGenerate = async (prompt: string, agentType: string, files?: File[]) => {
    if (workflowMode === "step-by-step") {
      await handleStepByStepWorkflow(prompt, agentType, files || []);
    } else {
      await handleAutoWorkflow(prompt, agentType, files || []);
    }
  };

  const handleAutoWorkflow = async (prompt: string, agentType: string, files: File[]) => {
    setIsLoading(true);
    setProgress(0);
    setCurrentStep("initialization");
    setLoadingMessage("Starting complete analysis...");

    try {
      const response = await createCompleteAnalysis(prompt, files, agentType);
      setReportId(response.report_id);
      setCompanyInfo(response.company_info);

      const pollInterval = setInterval(async () => {
        try {
          const status = await checkStatus(response.report_id);
          setProgress(status.progress || 0);
          setLoadingMessage(status.message || "Processing...");
          
          if (status.current_step) {
            setCurrentStep(status.current_step);
          }

          if (status.status === "completed") {
            clearInterval(pollInterval);
            setProgress(100);
            setCurrentStep("completed");
            setLoadingMessage("Analysis complete!");
            
            try {
              const memo = await getICMemo(response.report_id);
              setICMemo(memo);
            } catch (e) {
              console.error("Failed to get IC memo:", e);
            }

            try {
              const full = await getFullAnalysis(response.report_id);
              setFullAnalysis(full);
            } catch (e) {
              console.error("Failed to get full analysis:", e);
            }

            setIsLoading(false);
          } else if (status.status === "failed") {
            clearInterval(pollInterval);
            alert(`Analysis failed: ${status.message}`);
            setIsLoading(false);
          }
        } catch (error) {
          console.error("Polling error:", error);
        }
      }, 2000);

      setTimeout(() => clearInterval(pollInterval), 1200000);
    } catch (error: any) {
      console.error("Error:", error);
      alert(error.message || "Failed to start analysis");
      setIsLoading(false);
    }
  };

  const handleStepByStepWorkflow = async (prompt: string, agentType: string, files: File[]) => {
    setIsLoading(true);
    setProgress(0);
    setLoadingMessage("Starting step-by-step workflow...");

    try {
      const response = await startWorkflow(prompt, files, agentType);
      setWorkflowId(response.workflow_id);
      setReportId(response.workflow_id);
      setCompanyInfo(response.company_info);
      setCurrentStep("deep_research");
      
      // Determine which steps are active based on whether files were provided
      const hasFiles = files.length > 0;
      const steps = hasFiles 
        ? ["deep_research", "data_room", "risk_scanner", "ic_memo"]
        : ["deep_research", "risk_scanner", "ic_memo"];
      setActiveSteps(steps);
      
      setStepStatus({
        deep_research: "pending",
        data_room: hasFiles ? "pending" : "skipped",
        risk_scanner: "pending",
        ic_memo: "pending",
      });
      
      // Start SSE connection for streaming
      connectToSSE(response.workflow_id);
      
    } catch (error: any) {
      console.error("Error:", error);
      alert(error.message || "Failed to start workflow");
      setIsLoading(false);
    }
  };

  const connectToSSE = (wfId: string) => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    setIsProcessingStep(true);
    setStreamingContent("");
    setStepOutput(null);

    const eventSource = createSSEConnection(
      wfId,
      (eventType, data) => {
        console.log("SSE Event:", eventType, data);
        
        if (eventType === "status") {
          setLoadingMessage(data.message || "Processing...");
        } else if (eventType === "chunk") {
          setStreamingContent(prev => prev + (data.content || ""));
        } else if (eventType === "step_complete") {
          setIsProcessingStep(false);
          setAwaitingReview(true);
          setStepStatus(prev => ({
            ...prev,
            [data.step]: "completed"
          }));
          // Fetch the full output
          fetchStepOutput(wfId, data.step);
        } else if (eventType === "error") {
          setIsProcessingStep(false);
          setLoadingMessage(`Error: ${data.error}`);
        }
      },
      (error) => {
        console.error("SSE Error:", error);
        setIsProcessingStep(false);
      }
    );

    eventSourceRef.current = eventSource;
  };

  const fetchStepOutput = async (wfId: string, stepName: string) => {
    try {
      const output = await getStepOutput(wfId, stepName);
      setStepOutput(output.output);
    } catch (e) {
      console.error("Failed to fetch step output:", e);
    }
  };

  const handleContinue = async () => {
    if (!workflowId) return;

    try {
      const response = await continueWorkflow(workflowId);
      setAwaitingReview(false);
      setStepOutput(null);
      setStreamingContent("");

      if (response.status === "completed") {
        // Workflow complete - fetch final results
        setIsLoading(false);
        setCurrentStep("completed");
        
        try {
          const memo = await getICMemo(workflowId);
          setICMemo(memo);
        } catch (e) {
          console.error("Failed to get IC memo:", e);
        }

        try {
          const full = await getFullAnalysis(workflowId);
          setFullAnalysis(full);
        } catch (e) {
          console.error("Failed to get full analysis:", e);
        }
      } else {
        // Move to next step
        setCurrentStep(response.next_step);
        connectToSSE(workflowId);
      }
    } catch (error: any) {
      console.error("Error continuing workflow:", error);
      alert(error.message || "Failed to continue workflow");
    }
  };

  const handleRefine = async (feedback: string) => {
    if (!workflowId) return;

    try {
      await refineStep(workflowId, currentStep, feedback);
      setAwaitingReview(false);
      setStepOutput(null);
      setStreamingContent("");
      setStepStatus(prev => ({
        ...prev,
        [currentStep]: "refining"
      }));
      // Reconnect SSE for refined output
      connectToSSE(workflowId);
    } catch (error: any) {
      console.error("Error refining step:", error);
      alert(error.message || "Failed to refine step");
    }
  };

  const handleSkip = async () => {
    if (!workflowId) return;

    try {
      const response = await skipStep(workflowId, currentStep);
      setAwaitingReview(false);
      setStepOutput(null);
      setStreamingContent("");
      setStepStatus(prev => ({
        ...prev,
        [currentStep]: "skipped"
      }));

      if (response.next_step === "completed") {
        setIsLoading(false);
        setCurrentStep("completed");
        
        try {
          const memo = await getICMemo(workflowId);
          setICMemo(memo);
        } catch (e) {
          console.error("Failed to get IC memo:", e);
        }
      } else {
        setCurrentStep(response.next_step);
        connectToSSE(workflowId);
      }
    } catch (error: any) {
      console.error("Error skipping step:", error);
      alert(error.message || "Failed to skip step");
    }
  };

  const handleNewResearch = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    setIsLoading(false);
    setICMemo(null);
    setFullAnalysis(null);
    setReportId(null);
    setWorkflowId(null);
    setCompanyInfo(null);
    setProgress(0);
    setCurrentStep("");
    setLoadingMessage("");
    setStepStatus({});
    setStepOutput(null);
    setStreamingContent("");
    setIsProcessingStep(false);
    setAwaitingReview(false);
    setActiveSteps([]);
  };

  const showWorkflowUI = workflowMode === "step-by-step" && isLoading && workflowId;
  const showLoadingUI = workflowMode === "auto" && isLoading;

  return (
    <main className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="container mx-auto px-4 py-16 max-w-7xl">
        {!isLoading && !icMemo && (
          <>
            {/* Workflow Mode Toggle */}
            <div className="max-w-2xl mx-auto mb-8">
              <div className="flex items-center justify-center gap-4 p-2 bg-white rounded-lg shadow-sm border border-gray-200">
                <button
                  onClick={() => setWorkflowMode("step-by-step")}
                  className={`
                    px-4 py-2 rounded-md text-sm font-medium transition-colors
                    ${workflowMode === "step-by-step" 
                      ? "bg-blue-600 text-white" 
                      : "text-gray-600 hover:text-gray-900"}
                  `}
                >
                  Step-by-Step (Review Each Agent)
                </button>
                <button
                  onClick={() => setWorkflowMode("auto")}
                  className={`
                    px-4 py-2 rounded-md text-sm font-medium transition-colors
                    ${workflowMode === "auto" 
                      ? "bg-blue-600 text-white" 
                      : "text-gray-600 hover:text-gray-900"}
                  `}
                >
                  Automatic (Run All Agents)
                </button>
              </div>
              <p className="text-center text-sm text-gray-500 mt-2">
                {workflowMode === "step-by-step" 
                  ? "Review and refine each agent's output before proceeding"
                  : "Run all agents automatically without review"}
              </p>
            </div>
            
            <HeroSection onGenerate={handleGenerate} />
          </>
        )}

        {showLoadingUI && (
          <LoadingSection
            companyInfo={companyInfo}
            message={loadingMessage}
            progress={progress}
            currentStep={currentStep}
          />
        )}

        {showWorkflowUI && (
          <WorkflowSection
            workflowId={workflowId}
            currentStep={currentStep}
            stepStatus={stepStatus}
            stepOutput={stepOutput}
            isProcessing={isProcessingStep}
            streamingContent={streamingContent}
            activeSteps={activeSteps}
            onContinue={handleContinue}
            onRefine={handleRefine}
            onSkip={handleSkip}
          />
        )}

        {icMemo && !isLoading && (
          <ResultsSection 
            icMemo={icMemo}
            fullAnalysis={fullAnalysis}
            reportId={reportId}
            companyInfo={companyInfo}
            onNewResearch={handleNewResearch}
          />
        )}
      </div>
    </main>
  );
}
