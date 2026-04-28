import { motion } from 'framer-motion';
import { MapPinIcon, CalendarIcon } from 'lucide-react';
import { PopulatedEvent } from '../types';
import { formatCurrency } from '../utils/format';

interface EventCardProps {
  event: PopulatedEvent;
  onClick: (eventId: string) => void;
  index: number;
}

export function EventCard({ event, onClick, index }: EventCardProps) {
  const imageUrl = event.image_url || 'https://images.unsplash.com/photo-1540039155732-d674d40af4e0?auto=format&fit=crop&q=80&w=1600';
  const category = event.category || 'Sự kiện';
  const showtimesCount = event.showtimes?.length || 0;
  const venueName = event.venue?.name || 'Chưa xác định';
  const minPrice = event.minPrice || 0;

  return (
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
        duration: 0.5,
        delay: index * 0.1
      }}
      className="group bg-white rounded-2xl overflow-hidden shadow-soft hover:shadow-warm transition-all duration-300 cursor-pointer border border-navy-50 flex flex-col h-full"
      onClick={() => onClick(event.id)}>
      
      <div className="relative h-56 overflow-hidden">
        <div className="absolute inset-0 bg-navy-900/20 group-hover:bg-transparent transition-colors z-10" />
        <motion.img
          whileHover={{
            scale: 1.05
          }}
          transition={{
            duration: 0.4
          }}
          src={imageUrl}
          alt={event.name}
          className="w-full h-full object-cover" />
        
        <div className="absolute top-4 left-4 z-20">
          <span className="bg-white/90 backdrop-blur-sm text-navy-800 text-xs font-bold px-3 py-1.5 rounded-full shadow-sm">
            {category}
          </span>
        </div>
      </div>

      <div className="p-6 flex flex-col flex-grow">
        <h3 className="font-heading font-bold text-xl text-navy-900 mb-3 line-clamp-2 group-hover:text-coral-500 transition-colors">
          {event.name}
        </h3>

        <div className="space-y-2 mb-6 flex-grow">
          <div className="flex items-start gap-2 text-navy-600 text-sm">
            <CalendarIcon className="w-4 h-4 mt-0.5 flex-shrink-0 text-coral-500" />
            <span>{showtimesCount} suất diễn sắp tới</span>
          </div>
          <div className="flex items-start gap-2 text-navy-600 text-sm">
            <MapPinIcon className="w-4 h-4 mt-0.5 flex-shrink-0 text-coral-500" />
            <span className="line-clamp-1">{venueName}</span>
          </div>
        </div>

        <div className="pt-4 border-t border-navy-50 flex items-center justify-between mt-auto">
          <div>
            <p className="text-xs text-navy-400 mb-0.5">Giá từ</p>
            <p className="font-bold text-coral-500 text-lg">
              {minPrice > 0 ? formatCurrency(minPrice) : 'Liên hệ'}
            </p>
          </div>
          <button className="bg-navy-50 text-navy-800 px-4 py-2 rounded-lg font-medium text-sm group-hover:bg-coral-500 group-hover:text-white transition-colors">
            Xem chi tiết
          </button>
        </div>
      </div>
    </motion.div>);
}