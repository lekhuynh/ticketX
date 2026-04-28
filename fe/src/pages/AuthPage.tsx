import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UserIcon, MailIcon, LockIcon, ArrowLeftIcon, TicketIcon } from 'lucide-react';
import { authApi } from '../services/api';

interface AuthPageProps {
  onBack: () => void;
  onSuccess: (user: any) => void;
}

export function AuthPage({ onBack, onSuccess }: AuthPageProps) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isLogin) {
        const data = await authApi.login(email, password);
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        
        // Fetch user data
        const user = await authApi.getMe();
        localStorage.setItem('user', JSON.stringify(user));
        onSuccess(user);
      } else {
        await authApi.register({ email, password, full_name: fullName });
        // After register, auto login or switch to login
        setIsLogin(true);
        setError('Đăng ký thành công! Vui lòng đăng nhập.');
      }
    } catch (err: any) {
      console.error('Auth error:', err);
      setError(err.response?.data?.detail || 'Có lỗi xảy ra. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-navy-900 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-coral-500/10 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-gold-500/10 rounded-full blur-[100px]" />
      </div>

      <motion.button
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        onClick={onBack}
        className="absolute top-8 left-8 flex items-center gap-2 text-navy-200 hover:text-white transition-colors"
      >
        <ArrowLeftIcon className="w-5 h-5" />
        Quay lại
      </motion.button>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-white rounded-3xl shadow-2xl overflow-hidden relative z-10"
      >
        <div className="bg-gradient-to-r from-coral-500 to-coral-600 p-8 text-center text-white">
          <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-4">
            <TicketIcon className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-heading font-bold mb-2">TicketX</h1>
          <p className="text-coral-100 italic">Đặt vé nhanh - Trải nghiệm đỉnh cao</p>
        </div>

        <div className="p-8">
          <div className="flex gap-4 mb-8 bg-navy-50 p-1 rounded-xl">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-2.5 rounded-lg text-sm font-bold transition-all ${
                isLogin ? 'bg-white text-navy-900 shadow-sm' : 'text-navy-400 hover:text-navy-600'
              }`}
            >
              Đăng nhập
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-2.5 rounded-lg text-sm font-bold transition-all ${
                !isLogin ? 'bg-white text-navy-900 shadow-sm' : 'text-navy-400 hover:text-navy-600'
              }`}
            >
              Đăng ký
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <AnimatePresence mode="wait">
              {!isLogin && (
                <motion.div
                  key="fullname"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <label className="block text-sm font-bold text-navy-700 mb-1.5">Họ và tên</label>
                  <div className="relative">
                    <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-400" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required={!isLogin}
                      className="w-full pl-12 pr-4 py-3 rounded-xl border border-navy-100 focus:ring-2 focus:ring-coral-500 outline-none transition-all"
                      placeholder="Nguyễn Văn A"
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="block text-sm font-bold text-navy-700 mb-1.5">Email</label>
              <div className="relative">
                <MailIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full pl-12 pr-4 py-3 rounded-xl border border-navy-100 focus:ring-2 focus:ring-coral-500 outline-none transition-all"
                  placeholder="nguyenvana@example.com"
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="text-sm font-bold text-navy-700">Mật khẩu</label>
                {isLogin && (
                  <button type="button" className="text-xs text-coral-500 font-bold hover:underline">
                    Quên mật khẩu?
                  </button>
                )}
              </div>
              <div className="relative">
                <LockIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-navy-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full pl-12 pr-4 py-3 rounded-xl border border-navy-100 focus:ring-2 focus:ring-coral-500 outline-none transition-all"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {error && (
              <p className={`text-sm text-center font-medium ${error.includes('thành công') ? 'text-green-500' : 'text-red-500'}`}>
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-navy-900 hover:bg-navy-800 text-white py-4 rounded-xl font-bold transition-all shadow-lg active:scale-95 disabled:bg-navy-300 flex justify-center items-center gap-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : isLogin ? (
                'Đăng nhập'
              ) : (
                'Tạo tài khoản'
              )}
            </button>
          </form>

          <div className="mt-8 pt-8 border-t border-navy-50 text-center">
            <p className="text-navy-500 text-sm">
              {isLogin ? 'Chưa có tài khoản?' : 'Đã có tài khoản?'}
              <button
                onClick={() => setIsLogin(!isLogin)}
                className="ml-2 text-coral-500 font-bold hover:underline"
              >
                {isLogin ? 'Đăng ký ngay' : 'Đăng nhập ngay'}
              </button>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
