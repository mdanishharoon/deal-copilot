"use client";

import { useState } from "react";
import { Check, ArrowRight, RefreshCw, SkipForward, Loader2, AlertCircle, X } from "lucide-react";

interface WorkflowStep {
  name: string;
  label: string;
  description: string;
}

const ALL_WORKFLOW_STEPS: WorkflowStep[] = [
  { name: "deep_research", label: "Deep Research", description: "Public intelligence gathering" },
  { name: "data_room", label: "Data Room", description: "Document analysis" },
  { name: "risk_scanner", label: "Risk Scanner", description: "Risk identification" },
  { name: "ic_memo", label: "IC Memo", description: "Final memo drafting" },
];

interface WorkflowSectionProps {
  workflowId: string;
  currentStep: string;
  stepStatus: Record<string, string>;
  stepOutput: any;
  isProcessing: boolean;
  streamingContent: string;
  activeSteps?: string[];  // Steps that will be executed (excludes skipped)
  onContinue: () => void;
  onRefine: (feedback: string) => void;
  onSkip: () => void;
  onCancel: () => void;
}

export default function WorkflowSection({
  workflowId,
  currentStep,
  stepStatus,
  stepOutput,
  isProcessing,
  streamingContent,
  activeSteps,
  onContinue,
  onRefine,
  onSkip,
  onCancel,
}: WorkflowSectionProps) {
  const [showRefineInput, setShowRefineInput] = useState(false);
  const [feedback, setFeedback] = useState("");
  
  // Use provided activeSteps or default to all steps
  const workflowSteps = activeSteps 
    ? ALL_WORKFLOW_STEPS.filter(s => activeSteps.includes(s.name) || stepStatus[s.name] === "skipped")
    : ALL_WORKFLOW_STEPS;

  const handleRefineSubmit = () => {
    if (feedback.trim()) {
      onRefine(feedback);
      setFeedback("");
      setShowRefineInput(false);
    }
  };

  const getStepIcon = (stepName: string) => {
    const status = stepStatus[stepName];
    if (status === "completed") {
      return <Check className="w-5 h-5 text-green-600" />;
    } else if (status === "skipped") {
      return <SkipForward className="w-5 h-5 text-gray-400" />;
    } else if (stepName === currentStep && isProcessing) {
      return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
    } else if (stepName === currentStep) {
      return <div className="w-5 h-5 rounded-full bg-blue-600" />;
    }
    return <div className="w-5 h-5 rounded-full bg-gray-300" />;
  };

  const renderStepOutput = () => {
    if (!stepOutput && !streamingContent) return null;

    const content = streamingContent || formatOutput(stepOutput, currentStep);

    return (
      <div className="mt-6 bg-gray-50 rounded-lg p-6 max-h-[500px] overflow-y-auto">
        <h4 className="font-semibold text-gray-900 mb-3">
          {getStepLabel(currentStep)} Output
        </h4>
        <div 
          className="prose prose-sm max-w-none text-gray-700"
          dangerouslySetInnerHTML={{ __html: content }}
        />
      </div>
    );
  };

  const getStepLabel = (stepName: string): string => {
    const step = ALL_WORKFLOW_STEPS.find(s => s.name === stepName);
    return step?.label || stepName;
  };

  const formatOutput = (output: any, step: string): string => {
    if (!output) return "";
    
    if (step === "deep_research" && output.sections) {
      return output.sections.map((s: any) => `<h3>${s.title || s.section}</h3>${s.content}`).join("\n");
    }
    if (step === "data_room") {
      // Show ONLY human-readable summary (not raw quantitative/qualitative JSON)
      if (output.human_readable_summary?.content) {
        // Format the summary with proper HTML styling (similar to deep research)
        let formattedSummary = output.human_readable_summary.content
          // Convert markdown-style headers to HTML
          .replace(/\*\*\*(.+?)\*\*\*/g, '<h3 style="margin-top: 1.5rem; margin-bottom: 0.75rem; font-weight: 600; color: #1f2937;">$1</h3>')
          .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
          .replace(/\n\n/g, '</p><p style="margin-bottom: 1rem; line-height: 1.6;">')
          .replace(/\n/g, '<br/>');
        
        // Wrap in paragraphs
        formattedSummary = '<p style="margin-bottom: 1rem; line-height: 1.6;">' + formattedSummary + '</p>';
        
        return `<div style="font-size: 0.95rem;">${formattedSummary}</div>`;
      }
      // Fallback if summary not available
      return `<p style="color: #6b7280;">Data room summary not available. Raw data has been processed for IC Memo.</p>`;
    }
    if (step === "risk_scanner") {
      // Display human-readable summary for frontend, not the JSON
      if (output.human_readable_summary) {
        // Convert markdown to basic HTML
        const summary = output.human_readable_summary
          .replace(/\n/g, '<br/>')
          .replace(/### (.*?)(<br\/>|$)/g, '<h4>$1</h4>')
          .replace(/## (.*?)(<br\/>|$)/g, '<h3>$1</h3>')
          .replace(/# (.*?)(<br\/>|$)/g, '<h2>$1</h2>')
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/---<br\/>/g, '<hr/>');
        return summary;
      }
      // Fallback to JSON if summary not available
      return `<pre style="white-space: pre-wrap;">${JSON.stringify(output.risk_analysis, null, 2)}</pre>`;
    }
    if (step === "ic_memo" && output.memo_content?.content) {
      return output.memo_content.content;
    }
    
    return `<pre style="white-space: pre-wrap;">${JSON.stringify(output, null, 2)}</pre>`;
  };

  const awaitingReview = stepStatus[currentStep] === "completed" && !isProcessing;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Step Progress */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Workflow Progress</h3>
        
        <div className="flex items-center justify-between">
          {ALL_WORKFLOW_STEPS.map((step, index) => (
            <div key={step.name} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center
                  ${stepStatus[step.name] === "completed" ? "bg-green-100" : ""}
                  ${stepStatus[step.name] === "skipped" ? "bg-gray-100 opacity-50" : ""}
                  ${step.name === currentStep ? "bg-blue-100 ring-2 ring-blue-600" : "bg-gray-100"}
                `}>
                  {getStepIcon(step.name)}
                </div>
                <span className={`
                  mt-2 text-xs font-medium
                  ${step.name === currentStep ? "text-blue-600" : ""}
                  ${stepStatus[step.name] === "skipped" ? "text-gray-400 line-through" : "text-gray-500"}
                `}>
                  {step.label}
                  {stepStatus[step.name] === "skipped" && " (skipped)"}
                </span>
              </div>
              
              {index < ALL_WORKFLOW_STEPS.length - 1 && (
                <div className={`
                  w-16 h-0.5 mx-2
                  ${stepStatus[step.name] === "completed" ? "bg-green-400" : ""}
                  ${stepStatus[step.name] === "skipped" ? "bg-gray-200 opacity-50" : "bg-gray-200"}
                `} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              {getStepLabel(currentStep)}
            </h3>
            <p className="text-gray-500 text-sm">
              {ALL_WORKFLOW_STEPS.find(s => s.name === currentStep)?.description}
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            {isProcessing && (
              <div className="flex items-center text-blue-600">
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                <span className="text-sm font-medium">Processing...</span>
              </div>
            )}
            
            {(isProcessing || !awaitingReview) && currentStep !== "completed" && (
              <button
                onClick={onCancel}
                className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 border border-red-600 rounded-lg flex items-center gap-2 transition-colors"
                title="Cancel workflow"
              >
                <X className="w-4 h-4" />
                Stop
              </button>
            )}
          </div>
        </div>

        {/* Output Display */}
        {renderStepOutput()}

        {/* Action Buttons */}
        {awaitingReview && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Review the output above. Continue to next step or refine with feedback.
              </p>
              
              <div className="flex items-center gap-3">
                <button
                  onClick={onSkip}
                  className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 flex items-center gap-2"
                >
                  <SkipForward className="w-4 h-4" />
                  Skip
                </button>
                
                <button
                  onClick={() => setShowRefineInput(!showRefineInput)}
                  className="px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 border border-blue-600 rounded-lg flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refine
                </button>
                
                <button
                  onClick={onContinue}
                  className="px-6 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2"
                >
                  Continue
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Refine Input */}
            {showRefineInput && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provide feedback for refinement
                </label>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="e.g., Focus more on the competitive landscape, add more specific metrics..."
                  className="w-full h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                />
                <div className="mt-3 flex justify-end gap-2">
                  <button
                    onClick={() => setShowRefineInput(false)}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleRefineSubmit}
                    disabled={!feedback.trim()}
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Submit Feedback
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
