"use client";

import { useState } from "react";
import { Sparkles, TrendingUp, Users, Building2, FolderOpen } from "lucide-react";
import FileUpload from "./FileUpload";

interface HeroSectionProps {
  onGenerate: (prompt: string, agentType: string, files?: File[]) => void;
}

const examplePrompts = [
  {
    icon: <Building2 className="w-4 h-4" />,
    text: "Research Grab, a marketplace in Southeast Asia. Website: https://grab.com",
    label: "Grab - Marketplace",
  },
  {
    icon: <TrendingUp className="w-4 h-4" />,
    text: "Analyze Gojek, a super app in Indonesia. Website: https://www.gojek.com",
    label: "Gojek - Super App",
  },
  {
    icon: <Users className="w-4 h-4" />,
    text: "Due diligence on Shopee, an e-commerce platform in SEA. Website: https://shopee.sg",
    label: "Shopee - E-commerce",
  },
];

export default function HeroSection({ onGenerate }: HeroSectionProps) {
  const [prompt, setPrompt] = useState("");
  const [agentType, setAgentType] = useState("openai");
  const [isGenerating, setIsGenerating] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim()) {
      setIsGenerating(true);
      onGenerate(prompt, agentType, files.length > 0 ? files : undefined);
    }
  };

  const handleFilesChange = (newFiles: File[]) => {
    setFiles(newFiles);
  };

  const handleExampleClick = (examplePrompt: string) => {
    setPrompt(examplePrompt);
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Hero Header */}
      <div className="text-center mb-12">
        <h1 className="text-6xl font-bold mb-6 bg-gradient-primary bg-clip-text text-transparent leading-tight">
          AI-Powered Investment Analysis
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
          Complete due diligence with professional IC memo in minutes.
          <br />
          <span className="text-base text-gray-500 mt-2 inline-block">
            Upload deal documents and describe the company for complete analysis.
          </span>
        </p>
      </div>

      {/* Input Card */}
      <div className="card shadow-2xl">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder='e.g., "Analyze Bizzi, a SaaS company in Vietnam. Website: https://bizzi.vn/en/"'
              className="input-field resize-none"
              rows={4}
              disabled={isGenerating}
            />
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
            <div className="flex gap-3">
              <select
                value={agentType}
                onChange={(e) => setAgentType(e.target.value)}
                className="px-4 py-3 border-2 border-gray-200 rounded-xl bg-white focus:outline-none focus:border-primary-500 font-medium"
                disabled={isGenerating}
              >
                <option value="openai">OpenAI (Faster)</option>
                <option value="gemini">Gemini + Tavily (Cheaper)</option>
              </select>

              <button
                type="button"
                onClick={() => setShowFileUpload(!showFileUpload)}
                className={`px-4 py-3 border-2 rounded-xl font-medium transition-all flex items-center gap-2 ${
                  showFileUpload || files.length > 0
                    ? 'border-primary-500 text-primary-500 bg-primary-50'
                    : 'border-gray-300 text-gray-600 hover:border-gray-400'
                }`}
                disabled={isGenerating}
                title="Add data room files (optional)"
              >
                <FolderOpen className="w-5 h-5" />
                <span className="text-sm">
                  {files.length > 0 ? `${files.length} file${files.length > 1 ? 's' : ''}` : 'Add Files'}
                </span>
              </button>
            </div>

            <button
              type="submit"
              disabled={!prompt.trim() || isGenerating}
              className="btn-primary flex items-center justify-center gap-2"
            >
              <Sparkles className="w-5 h-5" />
              Generate Research
            </button>
          </div>
        </form>

        {/* File Upload Section */}
        {showFileUpload && (
          <div className="mt-6 p-6 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl border-2 border-indigo-200">
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-1 flex items-center gap-2">
                <FolderOpen className="w-5 h-5 text-primary-600" />
                Data Room Files (Optional)
              </h3>
              <p className="text-sm text-gray-700">
                Upload pitch decks, financials, cap tables, and other deal documents for deeper analysis.
                <span className="text-gray-500"> If no files are provided, the Data Room agent will be skipped.</span>
              </p>
            </div>
            <FileUpload onFilesChange={handleFilesChange} />
          </div>
        )}
      </div>

      {/* Example Prompts */}
      <div className="mt-8">
        <div className="flex items-center gap-4 flex-wrap justify-center">
          <span className="text-sm font-medium text-gray-600">Try these examples:</span>
          {examplePrompts.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleClick(example.text)}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gradient-primary hover:text-white 
                       border border-gray-200 rounded-full text-sm font-medium transition-all duration-200
                       transform hover:-translate-y-0.5 hover:shadow-md"
              disabled={isGenerating}
            >
              {example.icon}
              {example.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

