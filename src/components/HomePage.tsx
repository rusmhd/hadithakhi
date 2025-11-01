import { Shield, CheckCircle, Zap, Sparkles } from 'lucide-react';

interface HomePageProps {
  onVerifyClick: () => void;
}

export default function HomePage({ onVerifyClick }: HomePageProps) {
  return (
    <div className="min-h-screen bg-black">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <div className="w-20 h-20 rounded-2xl mx-auto mb-6 overflow-hidden">
            <img
              src="https://i.postimg.cc/QMtdc2Zy/jpg.jpg"
              alt="Logo"
              className="w-full h-full object-contain"
            />
          </div>
          <h1 className="text-6xl font-bold mb-4">
            <span className="text-gradient">Hadithakhi.ai</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Verify the authenticity of Hadiths with AI-powered precision
          </p>
        </div>

        <div className="max-w-xl mx-auto mb-20">
          <button
            onClick={onVerifyClick}
            className="w-full py-4 bg-gradient-to-r from-[#00FF88] to-[#00D97E] text-black font-bold text-lg rounded-xl button-hover glow-effect flex items-center justify-center gap-2"
          >
            <Sparkles className="w-5 h-5" />
            Start Verifying Hadiths
          </button>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="glass-effect p-8 rounded-2xl card-hover text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-[#00FF88]/20 to-[#00D97E]/20 rounded-xl flex items-center justify-center mx-auto mb-6">
              <Shield className="w-8 h-8 text-[#00FF88]" />
            </div>
            <h3 className="text-xl font-bold mb-3">Authentic Sources</h3>
            <p className="text-gray-400">
              Cross-referenced with authentic hadith collections
            </p>
          </div>

          <div className="glass-effect p-8 rounded-2xl card-hover text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-[#FFE44D]/20 to-[#FFA500]/20 rounded-xl flex items-center justify-center mx-auto mb-6">
              <Zap className="w-8 h-8 text-[#FFE44D]" />
            </div>
            <h3 className="text-xl font-bold mb-3">AI-Powered</h3>
            <p className="text-gray-400">
              Advanced machine learning for accurate verification
            </p>
          </div>

          <div className="glass-effect p-8 rounded-2xl card-hover text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-[#00D97E]/20 to-[#00FF88]/20 rounded-xl flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-8 h-8 text-[#00D97E]" />
            </div>
            <h3 className="text-xl font-bold mb-3">Instant Results</h3>
            <p className="text-gray-400">
              Get detailed verification results in seconds
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}