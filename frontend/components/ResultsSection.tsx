"use client";

import { Download, FileText, Shield, TrendingUp, FileSpreadsheet } from "lucide-react";
import { downloadICMemo, downloadRiskReport } from "@/lib/api";

interface ResultsSectionProps {
  icMemo: any;
  fullAnalysis: any;
  reportId: string | null;
  companyInfo: any;
  onNewResearch: () => void;
}

export default function ResultsSection({
  icMemo,
  fullAnalysis,
  reportId,
  companyInfo,
  onNewResearch,
}: ResultsSectionProps) {
  const companyName = companyInfo?.company_name || "Company";

  const handleDownloadICMemo = async () => {
    if (reportId) {
      await downloadICMemo(reportId, companyName);
    }
  };

  const handleDownloadRiskReport = async () => {
    if (reportId) {
      await downloadRiskReport(reportId, companyName);
    }
  };

  const handleDownloadDeepResearch = () => {
    if (fullAnalysis?.deep_research) {
      const report = fullAnalysis.deep_research;
      let text = "================================================================================\n";
      text += "DEEP RESEARCH REPORT\n";
      text += "================================================================================\n\n";
      text += `Company: ${report.company_name}\n`;
      text += `Sector: ${report.sector}\n`;
      text += `Region: ${report.region}\n\n`;

      report.sections?.forEach((section: any) => {
        text += `\n## ${section.section}\n\n`;
        // Strip HTML tags
        const content = section.content.replace(/<[^>]*>/g, '');
        text += `${content}\n\n`;
      });

      const blob = new Blob([text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${companyName}_Deep_Research.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleDownloadExcel = () => {
    if (reportId) {
      window.open(`http://localhost:8000/api/dataroom/${reportId}/excel`, '_blank');
    }
  };

  return (
    <div className="animate-fade-in space-y-8">
      {/* Header with Company Info */}
      <div className="card">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-3 bg-gradient-primary bg-clip-text text-transparent">
              Investment Committee Memo
            </h1>
            <div className="flex flex-wrap items-center gap-3 text-gray-600">
              <span className="font-semibold text-xl text-gray-900">
                {companyName}
              </span>
              <span className="text-gray-400">•</span>
              <span>{companyInfo?.sector || "N/A"}</span>
              <span className="text-gray-400">•</span>
              <span>{companyInfo?.region || "N/A"}</span>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              Generated: {new Date(icMemo.generated_at).toLocaleString()}
            </p>
          </div>
          <button
            onClick={onNewResearch}
            className="px-6 py-3 bg-white border-2 border-gray-300 rounded-xl
                     font-medium text-gray-700 hover:border-primary-500 hover:text-primary-500
                     transition-all duration-200"
          >
            New Analysis
          </button>
        </div>
      </div>

      {/* Download Buttons */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Download Reports</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            onClick={handleDownloadICMemo}
            className="flex items-center gap-3 px-4 py-3 bg-gradient-primary text-white rounded-lg
                     hover:shadow-lg transition-all duration-200"
          >
            <FileText className="w-5 h-5" />
            <span className="font-medium">IC Memo (HTML)</span>
          </button>

          <button
            onClick={handleDownloadRiskReport}
            className="flex items-center gap-3 px-4 py-3 bg-red-500 text-white rounded-lg
                     hover:shadow-lg hover:bg-red-600 transition-all duration-200"
          >
            <Shield className="w-5 h-5" />
            <span className="font-medium">Risk Report (JSON)</span>
          </button>

          <button
            onClick={handleDownloadDeepResearch}
            className="flex items-center gap-3 px-4 py-3 bg-blue-500 text-white rounded-lg
                     hover:shadow-lg hover:bg-blue-600 transition-all duration-200"
          >
            <TrendingUp className="w-5 h-5" />
            <span className="font-medium">Deep Research (TXT)</span>
          </button>

          <button
            onClick={handleDownloadExcel}
            className="flex items-center gap-3 px-4 py-3 bg-green-500 text-white rounded-lg
                     hover:shadow-lg hover:bg-green-600 transition-all duration-200"
          >
            <FileSpreadsheet className="w-5 h-5" />
            <span className="font-medium">Data Room (Excel)</span>
          </button>
        </div>
      </div>

      {/* IC Memo Content */}
      <div className="card">
        <div className="prose prose-lg max-w-none">
          <div
            dangerouslySetInnerHTML={{
              __html: icMemo.memo_content?.content || "<p>No content available</p>",
            }}
            className="ic-memo-content"
          />
        </div>
      </div>

      {/* Quick Stats (if available) */}
      {fullAnalysis?.risk_scanner?.risk_analysis?.structured_data && (
        <div className="card bg-gradient-to-br from-red-50 to-orange-50 border-l-4 border-red-500">
          <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-red-900">
            <Shield className="w-6 h-6" />
            Risk Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-600">Top Risks Identified</p>
              <p className="text-3xl font-bold text-red-600">
                {fullAnalysis.risk_scanner.risk_analysis.structured_data.top_risks?.length || 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Open DD Questions</p>
              <p className="text-3xl font-bold text-orange-600">
                {fullAnalysis.risk_scanner.risk_analysis.structured_data.open_questions?.length || 0}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Data Quality Issues</p>
              <p className="text-3xl font-bold text-yellow-600">
                {fullAnalysis.risk_scanner.risk_analysis.structured_data.data_quality_issues?.length || 0}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
