import React from 'react';
import { motion } from 'framer-motion';
import { SearchIcon, MapPinIcon, CalendarIcon } from 'lucide-react';
export function HeroSection() {
  return (
    <div className="relative bg-navy-900 pt-24 pb-32 overflow-hidden">
      {/* Background Image with Overlay */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1540039155732-d674d40af4e0?auto=format&fit=crop&q=80&w=2000"
          alt="Concert Background"
          className="w-full h-full object-cover opacity-30" />
        
        <div className="absolute inset-0 bg-gradient-to-t from-navy-900 via-navy-900/80 to-transparent" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{
            opacity: 0,
            y: 30
          }}
          animate={{
            opacity: 1,
            y: 0
          }}
          transition={{
            duration: 0.7,
            ease: 'easeOut'
          }}>
          
          <span className="inline-block py-1 px-3 rounded-full bg-coral-500/20 text-coral-400 text-sm font-semibold tracking-wider mb-6 border border-coral-500/30">
            TRẢI NGHIỆM ĐỈNH CAO
          </span>
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-heading font-extrabold text-white mb-6 tracking-tight">
            Khám Phá Những <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-coral-400 to-gold-400">
              Sự Kiện Tuyệt Vời
            </span>
          </h1>
          <p className="text-lg md:text-xl text-navy-200 max-w-2xl mx-auto mb-12 font-light">
            Đặt vé dễ dàng, trải nghiệm khó quên. Hàng ngàn sự kiện âm nhạc, văn
            hóa và giải trí đang chờ đón bạn.
          </p>
        </motion.div>

        {/* Search Bar */}
        <motion.div
          initial={{
            opacity: 0,
            y: 20
          }}
          animate={{
            opacity: 1,
            y: 0
          }}
          transition={{
            duration: 0.7,
            delay: 0.2,
            ease: 'easeOut'
          }}
          className="max-w-4xl mx-auto bg-white p-2 md:p-3 rounded-2xl shadow-2xl flex flex-col md:flex-row gap-2">
          
          <div className="flex-1 flex items-center px-4 py-3 md:py-0 bg-navy-50 rounded-xl md:bg-transparent md:rounded-none md:border-r border-navy-100">
            <SearchIcon className="w-5 h-5 text-navy-400 mr-3" />
            <input
              type="text"
              placeholder="Tìm kiếm sự kiện, nghệ sĩ..."
              className="w-full bg-transparent border-none focus:ring-0 text-navy-900 placeholder-navy-400 outline-none" />
            
          </div>
          <div className="flex-1 flex items-center px-4 py-3 md:py-0 bg-navy-50 rounded-xl md:bg-transparent md:rounded-none md:border-r border-navy-100">
            <MapPinIcon className="w-5 h-5 text-navy-400 mr-3" />
            <select className="w-full bg-transparent border-none focus:ring-0 text-navy-900 outline-none appearance-none cursor-pointer">
              <option>Tất cả địa điểm</option>
              <option>Hà Nội</option>
              <option>TP. Hồ Chí Minh</option>
              <option>Đà Nẵng</option>
            </select>
          </div>
          <div className="flex-1 flex items-center px-4 py-3 md:py-0 bg-navy-50 rounded-xl md:bg-transparent md:rounded-none">
            <CalendarIcon className="w-5 h-5 text-navy-400 mr-3" />
            <select className="w-full bg-transparent border-none focus:ring-0 text-navy-900 outline-none appearance-none cursor-pointer">
              <option>Mọi thời gian</option>
              <option>Hôm nay</option>
              <option>Tuần này</option>
              <option>Tháng này</option>
            </select>
          </div>
          <button className="bg-coral-500 hover:bg-coral-600 text-white px-8 py-4 rounded-xl font-semibold transition-colors shadow-warm flex-shrink-0 mt-2 md:mt-0">
            Tìm kiếm
          </button>
        </motion.div>
      </div>
    </div>);

}