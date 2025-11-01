import { useState, useEffect } from 'react';
import { supabase } from './lib/supabase';
import HomePage from './components/HomePage';
import VerifyPage from './components/VerifyPage';
import AuthModal from './components/AuthModal';

type View = 'home' | 'verify';

function App() {
  const [view, setView] = useState<View>('home');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();

    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      (() => {
        setIsAuthenticated(!!session);
        if (event === 'SIGNED_OUT') {
          setView('home');
        }
      })();
    });

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const checkAuth = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      setIsAuthenticated(!!session);
    } catch (error) {
      console.error('Error checking auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyClick = () => {
    if (isAuthenticated) {
      setView('verify');
    } else {
      setShowAuthModal(true);
    }
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
    setIsAuthenticated(true);
    setView('verify');
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setIsAuthenticated(false);
    setView('home');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-[#00FF88] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {view === 'home' && <HomePage onVerifyClick={handleVerifyClick} />}
      {view === 'verify' && isAuthenticated && <VerifyPage onLogout={handleLogout} />}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} onSuccess={handleAuthSuccess} />
      )}
    </>
  );
}

export default App;
