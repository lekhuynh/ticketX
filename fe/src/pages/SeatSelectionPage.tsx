import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeftIcon, TicketIcon } from 'lucide-react';
import { SeatMap } from '../components/SeatMap';
import { PopulatedEvent, PopulatedShowtimeSeat, Showtime } from '../types';
import { eventApi, seatApi, showtimeApi } from '../services/api';
import { formatCurrency, formatDate } from '../utils/format';

interface SeatSelectionPageProps {
  showtimeId: string;
  onBack: () => void;
  onCheckout: (seatIds: string[]) => void;
}

export function SeatSelectionPage({
  showtimeId,
  onBack,
  onCheckout
}: SeatSelectionPageProps) {
  const [selectedSeatIds, setSelectedSeatIds] = useState<string[]>([]);
  const [availableSeats, setAvailableSeats] = useState<PopulatedShowtimeSeat[]>([]);
  const [currentEvent, setCurrentEvent] = useState<PopulatedEvent | null>(null);
  const [currentShowtime, setCurrentShowtime] = useState<Showtime | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const fetchInitialData = async () => {
      try {
        setLoading(true);
        // 1. Get showtime info
        const showtimeData = await showtimeApi.getById(showtimeId);
        setCurrentShowtime(showtimeData);

        // 2. Get event info
        const eventData = await eventApi.getById(showtimeData.event_id);
        setCurrentEvent({
          ...eventData,
          venue: eventData.venue || { id: '', name: 'Unknown Venue', address: '', capacity: 0 },
          showtimes: eventData.showtimes || [],
          minPrice: 0
        });

        // 3. Get seats for this showtime
        const seatsData = await seatApi.getByShowtimeId(showtimeId);
        setAvailableSeats(seatsData);
      } catch (err) {
        console.error('Failed to fetch seat data:', err);
        setError('Không thể tải dữ liệu chỗ ngồi. Vui lòng thử lại sau.');
      } finally {
        setLoading(false);
      }
    };

    const pollSeats = async () => {
      try {
        const seatsData = await seatApi.getByShowtimeId(showtimeId);
        setAvailableSeats(seatsData);
      } catch (err) {
        console.error('Failed to poll seat data:', err);
      }
    };

    fetchInitialData().then(() => {
      // Poll every 10 seconds
      intervalId = setInterval(pollSeats, 10000);
    });

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [showtimeId]);

  const handleSeatToggle = (seatId: string) => {
    setSelectedSeatIds((prev) =>
      prev.includes(seatId) ?
      prev.filter((id) => id !== seatId) :
      [...prev, seatId]
    );
  };

  const selectedSeatsData = availableSeats.filter((s) =>
    selectedSeatIds.includes(s.id)
  );

  const totalPrice = selectedSeatsData.reduce(
    (sum, seat) => sum + seat.price,
    0
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-coral-500"></div>
      </div>
    );
  }

  if (error || !currentEvent || !currentShowtime) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <h2 className="text-2xl font-bold text-navy-900 mb-4">{error || 'Lỗi tải dữ liệu'}</h2>
        <button 
          onClick={onBack}
          className="bg-coral-500 text-white px-6 py-2 rounded-full font-bold"
        >
          Quay lại
        </button>
      </div>
    );
  }

  return (
    <motion.div
      initial={{
        opacity: 0,
        x: 20
      }}
      animate={{
        opacity: 1,
        x: 0
      }}
      exit={{
        opacity: 0,
        x: -20
      }}
      className="min-h-screen bg-background pb-32">
      
      {/* Header Bar */}
      <div className="bg-white border-b border-navy-100 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 hover:bg-navy-50 rounded-full transition-colors text-navy-600">
              
              <ArrowLeftIcon className="w-6 h-6" />
            </button>
            <div>
              <h1 className="font-heading font-bold text-lg text-navy-900">
                {currentEvent.name}
              </h1>
              <p className="text-sm text-navy-500">
                {formatDate(currentShowtime.start_time)} •{' '}
                {currentEvent.venue.name}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-heading font-bold text-navy-900 mb-2">
            Sơ đồ chỗ ngồi
          </h2>
          <p className="text-navy-500">
            Vui lòng chọn ghế bạn muốn đặt. Bạn có thể chọn tối đa 4 ghế.
          </p>
        </div>

        <SeatMap
          seats={availableSeats}
          selectedSeatIds={selectedSeatIds}
          onSeatToggle={handleSeatToggle} />
        
      </div>

      {/* Bottom Action Bar */}
      <motion.div
        initial={{
          y: 100
        }}
        animate={{
          y: selectedSeatIds.length > 0 ? 0 : 100
        }}
        className="fixed bottom-0 left-0 w-full bg-white border-t border-navy-100 shadow-[0_-10px_40px_rgba(27,42,74,0.05)] z-50 p-4 sm:p-6">
        
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-6">
            <div className="bg-coral-50 p-3 rounded-xl text-coral-500 hidden sm:block">
              <TicketIcon className="w-8 h-8" />
            </div>
            <div>
              <p className="text-sm text-navy-500 mb-1">
                Đã chọn {selectedSeatIds.length} ghế:
              </p>
              <p className="font-bold text-navy-900">
                {selectedSeatsData.
                map((s) => `${s.seat.row_label}${s.seat.seat_number}`).
                join(', ')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-6 w-full sm:w-auto justify-between sm:justify-end">
            <div className="text-right">
              <p className="text-sm text-navy-500 mb-1">Tổng cộng</p>
              <p className="font-bold text-2xl text-coral-500">
                {formatCurrency(totalPrice)}
              </p>
            </div>
            <button
              onClick={() => onCheckout(selectedSeatIds)}
              className="bg-coral-500 hover:bg-coral-600 text-white px-8 py-3.5 rounded-xl font-bold transition-colors shadow-warm">
              
              Thanh toán ngay
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>);
}