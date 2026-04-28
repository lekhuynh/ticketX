import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronRightIcon, CalendarIcon, MapPinIcon, ClockIcon } from 'lucide-react';
import { AdminEvents } from '../components/admin/AdminEvents';
import { AdminVenues } from '../components/admin/AdminVenues';
import { AdminShowtimes } from '../components/admin/AdminShowtimes';

type AdminTab = 'events' | 'venues' | 'showtimes';

export function AdminPage() {
  const [activeTab, setActiveTab] = useState<AdminTab>('events');

  return (
    <div className="min-h-screen bg-navy-50 pt-8 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row gap-8">
          
          {/* Sidebar */}
          <div className="w-full md:w-64 flex-shrink-0">
            <div className="bg-white rounded-2xl shadow-soft p-4 border border-navy-100 flex flex-col gap-2">
              <h2 className="text-xl font-heading font-bold text-navy-900 px-4 py-2 mb-2">
                Quản trị viên
              </h2>
              
              <button
                onClick={() => setActiveTab('events')}
                className={`flex items-center justify-between px-4 py-3 rounded-xl transition-colors ${
                  activeTab === 'events' 
                  ? 'bg-navy-900 text-white shadow-md' 
                  : 'text-navy-600 hover:bg-navy-50 hover:text-navy-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <CalendarIcon className="w-5 h-5" />
                  <span className="font-bold">Sự kiện</span>
                </div>
                {activeTab === 'events' && <ChevronRightIcon className="w-4 h-4" />}
              </button>

              <button
                onClick={() => setActiveTab('venues')}
                className={`flex items-center justify-between px-4 py-3 rounded-xl transition-colors ${
                  activeTab === 'venues' 
                  ? 'bg-navy-900 text-white shadow-md' 
                  : 'text-navy-600 hover:bg-navy-50 hover:text-navy-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <MapPinIcon className="w-5 h-5" />
                  <span className="font-bold">Địa điểm</span>
                </div>
                {activeTab === 'venues' && <ChevronRightIcon className="w-4 h-4" />}
              </button>

              <button
                onClick={() => setActiveTab('showtimes')}
                className={`flex items-center justify-between px-4 py-3 rounded-xl transition-colors ${
                  activeTab === 'showtimes' 
                  ? 'bg-navy-900 text-white shadow-md' 
                  : 'text-navy-600 hover:bg-navy-50 hover:text-navy-900'
                }`}
              >
                <div className="flex items-center gap-3">
                  <ClockIcon className="w-5 h-5" />
                  <span className="font-bold">Lịch diễn</span>
                </div>
                {activeTab === 'showtimes' && <ChevronRightIcon className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 min-w-0">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-white rounded-3xl shadow-soft border border-navy-100 p-6 min-h-[600px]"
            >
              {activeTab === 'events' && <AdminEvents />}
              {activeTab === 'venues' && <AdminVenues />}
              {activeTab === 'showtimes' && <AdminShowtimes />}
            </motion.div>
          </div>

        </div>
      </div>
    </div>
  );
}
