import { Loader2 } from "lucide-react";
import type { CompanyInfo } from "@/lib/types";

interface LoadingSectionProps {
  companyInfo: CompanyInfo | null;
  message: string;
  progress: number;
  currentStep?: string;
}

export default function LoadingSection({
  companyInfo,
  message,
  progress,
  currentStep,
}: LoadingSectionProps) {
  const getStepLabel = (step: string | undefined) => {
    const steps: Record<string, string> = {
      extraction: "📄 Extracting Files",
      qualitative: "📝 Qualitative Analysis",
      quantitative: "📊 Quantitative Extraction",
      excel: "📈 Generating Excel",
      initialization: "🚀 Initializing",
      processing: "⚙️ Processing",
      completed: "✅ Complete",
      error: "❌ Error"
    };
    return step ? steps[step] || step : "";
  };

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <div className="card text-center p-12">
        {/* Spinner */}
        <div className="flex justify-center mb-8">
          <div className="relative">
            <Loader2 className="w-16 h-16 text-primary-500 animate-spin" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-12 h-12 rounded-full bg-primary-50"></div>
            </div>
          </div>
        </div>

        {/* Title */}
        <h3 className="text-2xl font-bold mb-3 text-gray-900">
          Generating Research Report
        </h3>

        {/* Current Step Badge */}
        {currentStep && (
          <div className="mb-4">
            <span className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
              {getStepLabel(currentStep)}
            </span>
          </div>
        )}

        {/* Message */}
        <p className="text-gray-600 mb-8 text-lg">{message}</p>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-primary transition-all duration-500 ease-out rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-2 text-sm font-semibold text-primary-600">
            {Math.round(progress)}%
          </p>
        </div>

        {/* Company Info */}
        {companyInfo && (
          <div className="pt-6 border-t border-gray-200">
            <div className="flex flex-wrap items-center justify-center gap-3 text-sm text-gray-600">
              <span className="font-semibold text-gray-900">
                {companyInfo.company_name}
              </span>
              <span className="text-gray-400">•</span>
              <span>{companyInfo.sector}</span>
              <span className="text-gray-400">•</span>
              <span>{companyInfo.region}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

