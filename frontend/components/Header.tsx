import { Sparkles } from "lucide-react";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-lg bg-white/90 border-b border-gray-200">
      <div className="container mx-auto px-4 py-4 max-w-7xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-primary flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              Deal Co-Pilot
            </span>
          </div>
          
          <nav className="hidden md:flex items-center gap-8">
            <a href="#" className="text-gray-600 hover:text-primary-500 font-medium transition-colors">
              Research
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-500 font-medium transition-colors">
              History
            </a>
            <a href="#" className="text-gray-600 hover:text-primary-500 font-medium transition-colors">
              Docs
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}

