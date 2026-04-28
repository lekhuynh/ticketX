import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { HeroSection } from '../components/HeroSection';
import { EventCard } from '../components/EventCard';
import { eventApi } from '../services/api';
import { PopulatedEvent } from '../types';

interface HomePageProps {
  onEventSelect: (eventId: string) => void;
}

export function HomePage({ onEventSelect }: HomePageProps) {
  const [events, setEvents] = useState<PopulatedEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const data = await eventApi.getAll();
        
        // Map API data to PopulatedEvent type since backend returns venue and showtimes
        // But might need to calculate minPrice or hardcode for now if not in API
        const populatedEvents: PopulatedEvent[] = data.map((event: any) => ({
          ...event,
          venue: event.venue || { id: '', name: 'Unknown Venue', address: '', capacity: 0 },
          showtimes: event.showtimes || [],
          minPrice: 0 // Will need another API call or update backend to get min price
        }));
        
        setEvents(populatedEvents);
      } catch (err) {
        console.error('Failed to fetch events:', err);
        setError('Không thể tải danh sách sự kiện. Vui lòng thử lại sau.');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

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
      
      <HeroSection />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-16">
        <div className="flex justify-between items-end mb-10">
          <div>
            <h2 className="text-3xl font-heading font-bold text-navy-900 mb-2">
              Sự kiện nổi bật
            </h2>
            <p className="text-navy-500">
              Những sự kiện được mong chờ nhất trong tháng
            </p>
          </div>
          <button className="text-coral-500 font-semibold hover:text-coral-600 transition-colors hidden sm:block">
            Xem tất cả &rarr;
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-coral-500"></div>
          </div>
        ) : error ? (
          <div className="text-center py-20">
            <p className="text-red-500 text-lg mb-4">{error}</p>
            <button 
              onClick={() => window.location.reload()}
              className="bg-coral-500 text-white px-6 py-2 rounded-full font-bold"
            >
              Thử lại
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {events.length > 0 ? (
              events.map((event, index) =>
                <EventCard
                  key={event.id}
                  event={event}
                  onClick={onEventSelect}
                  index={index} />
              )
            ) : (
              <div className="col-span-full text-center py-20 text-navy-400">
                Chưa có sự kiện nào được diễn ra.
              </div>
            )}
          </div>
        )}

        {/* Categories Section */}
        <div className="mt-24">
          <h2 className="text-3xl font-heading font-bold text-navy-900 mb-10 text-center">
            Khám phá theo danh mục
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['Âm nhạc', 'Kịch nói', 'Hòa nhạc', 'Thể thao'].map((cat, i) =>
            <motion.div
              key={cat}
              whileHover={{
                y: -5
              }}
              className="bg-white p-8 rounded-2xl shadow-soft text-center cursor-pointer border border-navy-50 hover:border-coral-200 transition-colors group">
              
                <div className="w-16 h-16 mx-auto bg-navy-50 rounded-full flex items-center justify-center mb-4 group-hover:bg-coral-50 transition-colors">
                  <span className="text-2xl">
                    {['🎸', '🎭', '🎻', '⚽'][i]}
                  </span>
                </div>
                <h3 className="font-heading font-bold text-navy-800 group-hover:text-coral-500 transition-colors">
                  {cat}
                </h3>
              </motion.div>
            )}
          </div>
        </div>
      </main>
    </motion.div>);
}