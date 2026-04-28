import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  CalendarIcon,
  MapPinIcon,
  ClockIcon,
  TicketIcon,
  ChevronRightIcon } from 'lucide-react';
import { PopulatedEvent } from '../types';
import { eventApi } from '../services/api';
import { formatDate, formatCurrency } from '../utils/format';

interface EventDetailPageProps {
  eventId: string;
  onShowtimeSelect: (showtimeId: string) => void;
}

export function EventDetailPage({
  eventId,
  onShowtimeSelect
}: EventDetailPageProps) {
  const [event, setEvent] = useState<PopulatedEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEventDetails = async () => {
      try {
        setLoading(true);
        const data = await eventApi.getById(eventId);
        
        // Map API data to PopulatedEvent type
        const populatedEvent: PopulatedEvent = {
          ...data,
          venue: data.venue || { id: '', name: 'Unknown Venue', address: '', capacity: 0 },
          showtimes: data.showtimes || [],
          minPrice: 0 // In a real app, this would come from the API or showtimes
        };
        
        setEvent(populatedEvent);
      } catch (err) {
        console.error('Failed to fetch event details:', err);
        setError('Không tìm thấy sự kiện hoặc có lỗi xảy ra.');
      } finally {
        setLoading(false);
      }
    };

    fetchEventDetails();
  }, [eventId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-coral-500"></div>
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <h2 className="text-2xl font-bold text-navy-900 mb-4">{error || 'Không tìm thấy sự kiện'}</h2>
        <button 
          onClick={() => window.location.href = '/'}
          className="bg-coral-500 text-white px-6 py-2 rounded-full font-bold"
        >
          Quay lại trang chủ
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{
        opacity: 0
      }}
      animate={{
        opacity: 1
      }}
      exit={{
        opacity: 0
      }}
      className="min-h-screen bg-background pb-24">
      
      {/* Event Hero */}
      <div className="relative h-[50vh] min-h-[400px] w-full">
        <div className="absolute inset-0">
          <img
            src={event.image_url || 'https://images.unsplash.com/photo-1540039155732-d674d40af4e0?auto=format&fit=crop&q=80&w=1600'}
            alt={event.name}
            className="w-full h-full object-cover" />
          
          <div className="absolute inset-0 bg-gradient-to-t from-navy-900 via-navy-900/60 to-transparent" />
        </div>

        <div className="absolute bottom-0 left-0 w-full">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
            <span className="inline-block bg-coral-500 text-white text-sm font-bold px-3 py-1 rounded-full mb-4">
              {event.category || 'Sự kiện'}
            </span>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-heading font-bold text-white mb-4 max-w-4xl leading-tight">
              {event.name}
            </h1>
            <div className="flex flex-wrap items-center gap-6 text-navy-100">
              <div className="flex items-center gap-2">
                <MapPinIcon className="w-5 h-5 text-coral-400" />
                <span className="text-lg">{event.venue.name}</span>
              </div>
              <div className="flex items-center gap-2">
                <TicketIcon className="w-5 h-5 text-coral-400" />
                <span className="text-lg">
                  {event.minPrice > 0 ? `Từ ${formatCurrency(event.minPrice)}` : 'Giá liên hệ'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-12">
            <section>
              <h2 className="text-2xl font-heading font-bold text-navy-900 mb-6">
                Giới thiệu sự kiện
              </h2>
              <div className="prose prose-lg text-navy-600 leading-relaxed">
                <p>{event.description || 'Chưa có mô tả cho sự kiện này.'}</p>
                <p className="mt-4">
                  Hãy đến và trải nghiệm một không gian nghệ thuật đỉnh cao, nơi
                  những cảm xúc thăng hoa và những kỷ niệm khó quên được tạo
                  nên. Đừng bỏ lỡ cơ hội tham gia sự kiện đặc biệt này!
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-heading font-bold text-navy-900 mb-6">
                Thông tin địa điểm
              </h2>
              <div className="bg-white p-6 rounded-2xl shadow-soft border border-navy-50 flex items-start gap-4">
                <div className="bg-navy-50 p-3 rounded-xl text-navy-600">
                  <MapPinIcon className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-navy-900 mb-1">
                    {event.venue.name}
                  </h3>
                  <p className="text-navy-600 mb-2">{event.venue.address}</p>
                  <p className="text-sm text-navy-400">
                    Sức chứa: {event.venue.capacity} người
                  </p>
                </div>
              </div>
            </section>
          </div>

          {/* Sidebar - Showtimes */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-3xl shadow-soft border border-navy-50 p-6 sticky top-28">
              <h3 className="text-xl font-heading font-bold text-navy-900 mb-6 flex items-center gap-2">
                <CalendarIcon className="w-6 h-6 text-coral-500" />
                Chọn lịch diễn
              </h3>

              <div className="space-y-4">
                {event.showtimes.length > 0 ? (
                  event.showtimes.map((st) => (
                    <motion.button
                      key={st.id}
                      whileHover={{
                        scale: 1.02
                      }}
                      whileTap={{
                        scale: 0.98
                      }}
                      onClick={() => onShowtimeSelect(st.id)}
                      className="w-full flex items-center justify-between p-4 rounded-xl border border-navy-100 hover:border-coral-500 hover:bg-coral-50 transition-all group text-left">
                      
                        <div>
                          <div className="font-bold text-navy-900 group-hover:text-coral-600 mb-1">
                            {formatDate(st.start_time).split(',')[0]}
                          </div>
                          <div className="text-sm text-navy-500 flex items-center gap-1">
                            <ClockIcon className="w-4 h-4" />
                            {formatDate(st.start_time).split(',')[1]}
                          </div>
                        </div>
                        <div className="bg-navy-50 p-2 rounded-lg group-hover:bg-coral-500 group-hover:text-white transition-colors text-navy-400">
                          <ChevronRightIcon className="w-5 h-5" />
                        </div>
                    </motion.button>
                  ))
                ) : (
                  <p className="text-center py-10 text-navy-400">Chưa có lịch diễn nào.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>);
}