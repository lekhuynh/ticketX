import { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { HomePage } from './pages/HomePage';
import { EventDetailPage } from './pages/EventDetailPage';
import { SeatSelectionPage } from './pages/SeatSelectionPage';
import { CheckoutPage } from './pages/CheckoutPage';
import { AuthPage } from './pages/AuthPage';
import { AdminPage } from './pages/AdminPage';
import { CheckCircleIcon } from 'lucide-react';
import { ChatbotWidget } from './components/ChatbotWidget';

type PageView =
  | 'home'
  | 'event-detail'
  | 'seat-selection'
  | 'checkout'
  | 'success'
  | 'auth'
  | 'admin';

export function App() {
  const [currentView, setCurrentView] = useState<PageView>('home');
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedShowtimeId, setSelectedShowtimeId] = useState<string | null>(null);
  const [selectedSeatIds, setSelectedSeatIds] = useState<string[]>([]);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const navigateTo = (view: PageView) => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
    setCurrentView(view);
  };

  const handleEventSelect = (eventId: string) => {
    setSelectedEventId(eventId);
    navigateTo('event-detail');
  };

  const handleShowtimeSelect = (showtimeId: string) => {
    setSelectedShowtimeId(showtimeId);
    setSelectedSeatIds([]); // Reset seats when changing showtime
    navigateTo('seat-selection');
  };

  const handleProceedToCheckout = (seatIds: string[]) => {
    setSelectedSeatIds(seatIds);
    // If not logged in, go to auth
    if (!user) {
      navigateTo('auth');
    } else {
      navigateTo('checkout');
    }
  };

  const handleAuthSuccess = (userData: any) => {
    setUser(userData);
    // If was in checkout flow, go back to checkout
    if (selectedSeatIds.length > 0 && selectedShowtimeId) {
      navigateTo('checkout');
    } else {
      navigateTo('home');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    setUser(null);
    navigateTo('home');
  };

  // Handle VNPAY return
  useEffect(() => {
    const path = window.location.pathname;
    const search = window.location.search;
    
    if (path === '/payment/result') {
      const params = new URLSearchParams(search);
      const status = params.get('status');
      
      if (status === 'success') {
        setCurrentView('success');
      } else {
        // You might want a 'failed' view, but for now we can go home or show an alert
        alert('Thanh toán thất bại hoặc đã bị hủy.');
        setCurrentView('home');
      }
      
      // Clear the URL to avoid re-triggering on refresh
      window.history.replaceState({}, '', '/');
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col bg-background font-sans">
      <Header 
        onNavigate={navigateTo} 
        user={user} 
        onLogout={handleLogout} 
        onLoginClick={() => navigateTo('auth')}
      />

      <div className="flex-grow">
        <AnimatePresence mode="wait">
          {currentView === 'home' && (
            <HomePage key="home" onEventSelect={handleEventSelect} />
          )}

          {currentView === 'event-detail' && selectedEventId && (
            <EventDetailPage
              key="event-detail"
              eventId={selectedEventId}
              onShowtimeSelect={handleShowtimeSelect}
            />
          )}

          {currentView === 'seat-selection' && selectedShowtimeId && (
            <SeatSelectionPage
              key="seat-selection"
              showtimeId={selectedShowtimeId}
              onBack={() => navigateTo('event-detail')}
              onCheckout={handleProceedToCheckout}
            />
          )}

          {currentView === 'checkout' &&
            selectedShowtimeId &&
            selectedSeatIds.length > 0 && (
              <CheckoutPage
                key="checkout"
                showtimeId={selectedShowtimeId}
                selectedSeatIds={selectedSeatIds}
                onBack={() => navigateTo('seat-selection')}
              />
            )}

          {currentView === 'auth' && (
            <AuthPage
              key="auth"
              onBack={() => navigateTo('home')}
              onSuccess={handleAuthSuccess}
            />
          )}

          {currentView === 'admin' && (
            <AdminPage key="admin" />
          )}

          {currentView === 'success' && (
            <motion.div
              key="success"
              initial={{
                opacity: 0,
                scale: 0.9,
              }}
              animate={{
                opacity: 1,
                scale: 1,
              }}
              className="min-h-[70vh] flex items-center justify-center p-4"
            >
              <div className="bg-white p-10 rounded-3xl shadow-soft text-center max-w-md w-full border border-navy-50">
                <div className="w-20 h-20 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckCircleIcon className="w-10 h-10" />
                </div>
                <h2 className="text-3xl font-heading font-bold text-navy-900 mb-4">
                  Đặt vé thành công!
                </h2>
                <p className="text-navy-600 mb-8">
                  Cảm ơn bạn đã tin tưởng VeNhanh. Vé điện tử đã được gửi đến
                  email của bạn.
                </p>
                <button
                  onClick={() => {
                    setSelectedEventId(null);
                    setSelectedShowtimeId(null);
                    setSelectedSeatIds([]);
                    navigateTo('home');
                  }}
                  className="w-full bg-navy-900 hover:bg-navy-800 text-white py-4 rounded-xl font-bold transition-colors"
                >
                  Về trang chủ
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <Footer />
      <ChatbotWidget user={user} />
    </div>
  );
}