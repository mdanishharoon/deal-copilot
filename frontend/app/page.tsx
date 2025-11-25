"use client";

import { useState } from "react";
import Header from "@/components/Header";
import HeroSection from "@/components/HeroSection";
import LoadingSection from "@/components/LoadingSection";
import ResultsSection from "@/components/ResultsSection";
import { createCompleteAnalysis, checkStatus, getICMemo, getFullAnalysis } from "@/lib/api";
import type { CompanyInfo } from "@/lib/types";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [reportId, setReportId] = useState<string | null>(null);
  const [icMemo, setICMemo] = useState<any | null>(null);
  const [fullAnalysis, setFullAnalysis] = useState<any | null>(null);

  const handleGenerate = async (prompt: string, agentType: string, files?: File[]) => {
    // Require files for complete analysis
    if (!files || files.length === 0) {
      alert("Please upload at least one file (PDF, Excel, PowerPoint, or Word) to run complete analysis.");
      return;
    }

    setIsLoading(true);
    setProgress(0);
    setCurrentStep("initialization");
    setLoadingMessage("Starting complete analysis...");

    try {
      // Start Complete Analysis (all agents in sequence)
      const response = await createCompleteAnalysis(prompt, files, agentType);
      setReportId(response.report_id);
      setCompanyInfo(response.company_info);

      // Poll for status updates
      const pollInterval = setInterval(async () => {
        try {
          const status = await checkStatus(response.report_id);

          // Update UI with real-time progress
          setProgress(status.progress || 0);
          setLoadingMessage(status.message || "Processing...");
          
          if (status.current_step) {
            setCurrentStep(status.current_step);
          }

          // Check if completed
          if (status.status === "completed") {
            clearInterval(pollInterval);
            setProgress(100);
            setCurrentStep("completed");
            setLoadingMessage("Analysis complete!");
            
            // Get IC Memo (primary output)
            const memo = await getICMemo(response.report_id);
            setICMemo(memo);

            // Get full analysis (for downloads)
            const full = await getFullAnalysis(response.report_id);
            setFullAnalysis(full);

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

      // Cleanup after 20 minutes
      setTimeout(() => clearInterval(pollInterval), 1200000);
    } catch (error: any) {
      console.error("Error:", error);
      alert(error.message || "Failed to start analysis");
      setIsLoading(false);
    }
  };

  const handleNewResearch = () => {
    setIsLoading(false);
    setICMemo(null);
    setFullAnalysis(null);
    setReportId(null);
    setCompanyInfo(null);
    setProgress(0);
    setCurrentStep("");
    setLoadingMessage("");
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="container mx-auto px-4 py-16 max-w-7xl">
        {!isLoading && !icMemo && (
          <HeroSection onGenerate={handleGenerate} />
        )}

        {isLoading && (
          <LoadingSection
            companyInfo={companyInfo}
            message={loadingMessage}
            progress={progress}
            currentStep={currentStep}
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


