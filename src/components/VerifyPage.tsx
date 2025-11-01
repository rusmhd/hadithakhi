import { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, XCircle, LogOut, ChevronRight } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface HadithMatch {
  id: number;
  hadithArabic: string;
  hadithEnglish: string;
  authenticity: string;
  source: string;
  reference: string;
  relevanceScore: number;
}

interface HadithSearchResponse {
  found: boolean;
  matches: HadithMatch[];
  searchText: string;
  cached?: boolean;
}

interface VerifyPageProps {
  onLogout: () => void;
}

export default function VerifyPage({ onLogout }: VerifyPageProps) {
  const [searchText, setSearchText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<HadithSearchResponse | null>(null);
  const [selectedHadith, setSelectedHadith] = useState<HadithMatch | null>(null);
  const [error, setError] = useState<string>('');
  const [userEmail, setUserEmail] = useState('');

  useEffect(() => {
    const getUser = async () => {
      const { data } = await supabase.auth.getUser();
      if (data.user) {
        setUserEmail(data.user.email || '');
      }
    };
    getUser();
  }, []);

  const verifyHadith = async () => {
    if (!searchText.trim()) {
      setError('Please enter text to verify');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);
    setSelectedHadith(null);

    try {
      const apiUrl = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/verify-hadith`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: searchText }),
      });

      if (!response.ok) {
        throw new Error('Failed to verify hadith');
      }

      const data: HadithSearchResponse = await response.json();
      setResult(data);

      if (data.found && data.matches.length > 0) {
        setSelectedHadith(data.matches[0]);
      }
    } catch (err) {
      setError('An error occurred while verifying. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !loading) {
      e.preventDefault();
      verifyHadith();
    }
  };

  const getAuthenticityColor = (authenticity?: string) => {
    if (!authenticity) return 'text-gray-400';
    const lower = authenticity.toLowerCase();
    if (lower.includes('sahih')) return 'text-[#00FF88]';
    if (lower.includes('hasan')) return 'text-blue-400';
    if (lower.includes('daif')) return 'text-amber-400';
    return 'text-gray-400';
  };

  const getAuthenticityBg = (authenticity?: string) => {
    if (!authenticity) return 'bg-gray-900 border-gray-700';
    const lower = authenticity.toLowerCase();
    if (lower.includes('sahih')) return 'bg-[#00FF88]/5 border-[#00FF88]/30';
    if (lower.includes('hasan')) return 'bg-blue-400/5 border-blue-400/30';
    if (lower.includes('daif')) return 'bg-amber-400/5 border-amber-400/30';
    return 'bg-gray-900 border-gray-700';
  };

  const getRelevancePercentage = (score: number) => {
    return Math.min(Math.round(score * 100), 100);
  };

  return (
    <div className="min-h-screen bg-black">
      <div className="fixed inset-0 pointer-events-none">
        <div
          className="absolute inset-0"
          style={{
            background:
              'radial-gradient(ellipse at 70% 20%, rgba(0,255,136,0.06) 0%, transparent 40%), radial-gradient(ellipse at 30% 80%, rgba(0,255,136,0.04) 0%, transparent 40%)',
          }}
        />
      </div>

      <header className="relative glass-effect border-b border-[#2C2C2E]">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl">✓</span>
            <h2 className="text-xl font-bold text-white">Hadithakhi Chat</h2>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">{userEmail}</span>
            <button
              onClick={onLogout}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-transparent border border-[#2C2C2E] text-gray-400 hover:text-white hover:border-[#00FF88]/50 transition-all"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <main className="relative max-w-6xl mx-auto px-6 py-8">
        <div className="glass-effect rounded-2xl p-6 border border-[#00FF88]/20 mb-6">
          <label className="block text-sm font-semibold text-gray-300 mb-3">
            Enter Hadith Text or Keywords
          </label>
          <textarea
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Mention any hadith, a portion of it, or share your understanding of a particular hadith..."
            className="w-full px-4 py-3 bg-[#0D0D0D] border border-[#2C2C2E] rounded-xl text-white placeholder-gray-600 focus:border-[#00FF88] focus:ring-2 focus:ring-[#00FF88]/20 outline-none transition-all resize-none"
            rows={4}
            disabled={loading}
          />

          {error && (
            <div className="flex items-center gap-2 text-red-400 bg-red-400/10 border border-red-400/20 px-4 py-3 rounded-lg mt-4">
              <XCircle className="w-5 h-5" />
              <span>{error}</span>
            </div>
          )}

          <button
            onClick={verifyHadith}
            disabled={loading || !searchText.trim()}
            className="w-full mt-4 py-4 rounded-xl font-bold text-black disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-3 button-hover"
            style={{
              background: 'linear-gradient(135deg, #00FF88, #00D97E)',
            }}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <span className="text-xl">➤</span>
                Search Hadith
              </>
            )}
          </button>
        </div>

        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-4">
              <div className="glass-effect rounded-xl p-4 border border-[#00FF88]/20">
                <div className="flex items-center gap-3 mb-3">
                  {result.found ? (
                    <CheckCircle2 className="w-6 h-6 text-[#00FF88]" />
                  ) : (
                    <XCircle className="w-6 h-6 text-red-400" />
                  )}
                  <h3 className="text-lg font-bold text-white">
                    {result.found ? `${result.matches.length} Matches Found` : 'No Matches'}
                  </h3>
                </div>
                {result.found ? (
                  <p className="text-sm text-gray-400 mb-4">
                    Select a hadith to view details. Results are sorted by relevance.
                  </p>
                ) : (
                  <p className="text-sm text-gray-400">
                    No hadiths found matching your search. Try different keywords or check spelling.
                  </p>
                )}
              </div>

              {result.found && result.matches.length > 0 && (
                <div className="space-y-2 max-h-[calc(100vh-400px)] overflow-y-auto pr-2">
                  {result.matches.map((match, index) => (
                    <button
                      key={match.id}
                      onClick={() => setSelectedHadith(match)}
                      className={`w-full text-left glass-effect rounded-xl p-4 border-2 transition-all hover:border-[#00FF88]/50 ${
                        selectedHadith?.id === match.id
                          ? 'border-[#00FF88] bg-[#00FF88]/5'
                          : 'border-[#2C2C2E]'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-bold text-[#00FF88] bg-[#00FF88]/10 px-2 py-0.5 rounded">
                              #{index + 1}
                            </span>
                            <span className="text-xs text-gray-500">
                              {getRelevancePercentage(match.relevanceScore)}% match
                            </span>
                          </div>
                          <h4 className="text-sm font-semibold text-white line-clamp-1">
                            {match.source}
                          </h4>
                          <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                            {match.hadithEnglish}
                          </p>
                        </div>
                        <ChevronRight className={`w-5 h-5 flex-shrink-0 transition-all ${
                          selectedHadith?.id === match.id ? 'text-[#00FF88]' : 'text-gray-600'
                        }`} />
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <span className={`text-xs font-semibold ${getAuthenticityColor(match.authenticity)}`}>
                          {match.authenticity}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {selectedHadith && (
              <div className="lg:col-span-2 glass-effect rounded-2xl p-8 border border-[#00FF88]/20 animate-in fade-in slide-in-from-right-4 duration-500 max-h-[calc(100vh-200px)] overflow-y-auto">
                <div className="space-y-6">
                  <div
                    className={`border-2 rounded-xl p-6 ${getAuthenticityBg(selectedHadith.authenticity)}`}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-white">Authenticity Grade</h3>
                      <span
                        className={`text-2xl font-bold ${getAuthenticityColor(
                          selectedHadith.authenticity
                        )}`}
                      >
                        {selectedHadith.authenticity}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-semibold text-gray-400">Source:</span>
                        <span className="ml-2 text-white">{selectedHadith.source}</span>
                      </div>
                      <div>
                        <span className="font-semibold text-gray-400">Reference:</span>
                        <span className="ml-2 text-white">{selectedHadith.reference}</span>
                      </div>
                      <div>
                        <span className="font-semibold text-gray-400">Relevance:</span>
                        <span className="ml-2 text-white">
                          {getRelevancePercentage(selectedHadith.relevanceScore)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-[#0D0D0D] border-2 border-[#2C2C2E] rounded-xl p-6">
                    <h3 className="text-lg font-bold text-white mb-3">Arabic Text</h3>
                    <p className="text-2xl leading-loose text-right text-white" dir="rtl">
                      {selectedHadith.hadithArabic}
                    </p>
                  </div>

                  <div className="bg-[#00FF88]/5 border-2 border-[#00FF88]/30 rounded-xl p-6">
                    <h3 className="text-lg font-bold text-white mb-3">English Translation</h3>
                    <p className="text-lg leading-relaxed text-gray-300">
                      {selectedHadith.hadithEnglish}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
