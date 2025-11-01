import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { supabase } from '../lib/supabase';

interface AuthModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function AuthModal({ onClose, onSuccess }: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (mode === 'signup') {
        const { error: signupError } = await supabase.auth.signUp({
          email,
          password,
        });
        if (signupError) throw signupError;
        onSuccess();
      } else {
        const { error: loginError } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (loginError) throw loginError;
        onSuccess();
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={onClose}
      />

      <div className="relative w-full max-w-md bg-black/90 backdrop-blur-xl border border-[#00FF88]/20 rounded-2xl p-8 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-xl mx-auto mb-4 overflow-hidden">
            <img
              src="https://i.postimg.cc/QMtdc2Zy/jpg.jpg"
              alt="Logo"
              className="w-full h-full object-contain"
            />
          </div>
          <h2 className="text-3xl font-bold text-white">Hadithakhi.ai</h2>
        </div>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setMode('login')}
            className={`flex-1 py-2.5 rounded-lg font-bold transition-all ${
              mode === 'login'
                ? 'bg-gradient-to-r from-[#00FF88] to-[#00D97E] text-black shadow-lg'
                : 'bg-transparent text-gray-400 hover:text-white border border-[#2C2C2E]'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setMode('signup')}
            className={`flex-1 py-2.5 rounded-lg font-bold transition-all ${
              mode === 'signup'
                ? 'bg-gradient-to-r from-[#00FF88] to-[#00D97E] text-black shadow-lg'
                : 'bg-transparent text-gray-400 hover:text-white border border-[#2C2C2E]'
            }`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 bg-[#0D0D0D] border border-[#2C2C2E] rounded-xl text-white placeholder-gray-500 focus:border-[#00FF88] focus:ring-2 focus:ring-[#00FF88]/20 outline-none transition-all"
            />
          </div>

          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full px-4 py-3 bg-[#0D0D0D] border border-[#2C2C2E] rounded-xl text-white placeholder-gray-500 focus:border-[#00FF88] focus:ring-2 focus:ring-[#00FF88]/20 outline-none transition-all"
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded-lg px-4 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-[#00FF88] to-[#00D97E] text-black font-bold rounded-xl hover:shadow-lg hover:shadow-[#00FF88]/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {mode === 'login' ? 'Logging in...' : 'Signing up...'}
              </>
            ) : (
              mode === 'login' ? 'Login' : 'Sign Up'
            )}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button
            onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}
            className="text-[#00FF88] hover:underline font-semibold"
          >
            {mode === 'login' ? 'Sign up' : 'Login'}
          </button>
        </p>
      </div>
    </div>
  );
}
