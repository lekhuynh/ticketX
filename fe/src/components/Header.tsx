import React, { useState } from 'react';
import { TicketIcon, SearchIcon, UserIcon, MenuIcon, LogOutIcon, LayoutDashboardIcon } from 'lucide-react';

interface HeaderProps {
  onNavigate: (view: any) => void;
  user: any;
  onLogout: () => void;
  onLoginClick: () => void;
}

export function Header({ onNavigate, user, onLogout, onLoginClick }: HeaderProps) {
  const [showUserMenu, setShowUserMenu] = useState(false);

  return (
    <header className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-navy-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <div
            className="flex items-center gap-2 cursor-pointer group"
            onClick={() => onNavigate('home')}>
            
            <div className="bg-coral-500 text-white p-2 rounded-xl group-hover:bg-coral-600 transition-colors">
              <TicketIcon className="w-6 h-6" />
            </div>
            <span className="font-heading font-bold text-2xl text-navy-800 tracking-tight">
              Ticket<span className="text-coral-500">X</span>
            </span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-8">
            <button
              onClick={() => onNavigate('home')}
              className="text-navy-800 font-medium hover:text-coral-500 transition-colors">
              Trang chủ
            </button>
            <button className="text-navy-600 font-medium hover:text-coral-500 transition-colors">
              Sự kiện
            </button>
            <button className="text-navy-600 font-medium hover:text-coral-500 transition-colors">
              Lịch diễn
            </button>
            <button className="text-navy-600 font-medium hover:text-coral-500 transition-colors">
              Liên hệ
            </button>
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-4">
            <button className="p-2 text-navy-600 hover:text-coral-500 hover:bg-coral-50 rounded-full transition-all">
              <SearchIcon className="w-5 h-5" />
            </button>
            
            {user ? (
              <div className="relative">
                <button 
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center gap-2 bg-navy-50 text-navy-900 px-4 py-2 rounded-full font-bold hover:bg-navy-100 transition-colors border border-navy-100"
                >
                  <div className="w-6 h-6 bg-coral-500 text-white rounded-full flex items-center justify-center text-xs">
                    {user.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="hidden sm:inline">{user.full_name}</span>
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-2xl shadow-xl border border-navy-50 py-2 z-50 overflow-hidden">
                    <div className="px-4 py-3 border-b border-navy-50">
                      <p className="text-xs text-navy-400 font-bold uppercase tracking-wider">Tài khoản</p>
                      <p className="text-sm font-bold text-navy-900 truncate">{user.email}</p>
                    </div>
                    <button className="w-full text-left px-4 py-2.5 text-sm text-navy-600 hover:bg-navy-50 hover:text-coral-500 transition-colors flex items-center gap-2">
                      <UserIcon className="w-4 h-4" />
                      Hồ sơ cá nhân
                    </button>
                    <button className="w-full text-left px-4 py-2.5 text-sm text-navy-600 hover:bg-navy-50 hover:text-coral-500 transition-colors flex items-center gap-2">
                      <TicketIcon className="w-4 h-4" />
                      Vé đã đặt
                    </button>
                    <button 
                      onClick={() => {
                        setShowUserMenu(false);
                        onNavigate('admin');
                      }}
                      className="w-full text-left px-4 py-2.5 text-sm text-purple-600 hover:bg-purple-50 hover:text-purple-700 transition-colors flex items-center gap-2 border-t border-navy-50"
                    >
                      <LayoutDashboardIcon className="w-4 h-4" />
                      Admin Dashboard
                    </button>
                    <button 
                      onClick={() => {
                        setShowUserMenu(false);
                        onLogout();
                      }}
                      className="w-full text-left px-4 py-2.5 text-sm text-red-500 hover:bg-red-50 transition-colors flex items-center gap-2 mt-2 border-t border-navy-50"
                    >
                      <LogOutIcon className="w-4 h-4" />
                      Đăng xuất
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button 
                onClick={onLoginClick}
                className="hidden sm:flex items-center gap-2 bg-navy-800 text-white px-5 py-2.5 rounded-full font-medium hover:bg-navy-700 transition-colors shadow-soft"
              >
                <UserIcon className="w-4 h-4" />
                <span>Đăng nhập</span>
              </button>
            )}

            <button className="md:hidden p-2 text-navy-800">
              <MenuIcon className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}