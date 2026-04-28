import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { PopulatedShowtimeSeat } from '../types';
import { formatCurrency } from '../utils/format';

interface SeatMapProps {
  seats: PopulatedShowtimeSeat[];
  selectedSeatIds: string[];
  onSeatToggle: (seatId: string) => void;
}

export function SeatMap({
  seats,
  selectedSeatIds,
  onSeatToggle
}: SeatMapProps) {
  const rows = useMemo(() => {
    const grouped: Record<string, PopulatedShowtimeSeat[]> = {};
    seats.forEach((seat) => {
      const row = seat.seat.row_label;
      if (!grouped[row]) grouped[row] = [];
      grouped[row].push(seat);
    });
    const sortedRows = Object.keys(grouped).sort();
    sortedRows.forEach((row) => {
      grouped[row].sort((a, b) => a.seat.seat_number - b.seat.seat_number);
    });
    return {
      keys: sortedRows,
      data: grouped
    };
  }, [seats]);

  const getSeatColor = (status: string, isSelected: boolean, price: number) => {
    if (isSelected)
    return 'bg-coral-500 border-coral-600 text-white shadow-md scale-110 z-10';
    if (status === 'BOOKED')
    return 'bg-navy-100 border-navy-200 text-navy-300 cursor-not-allowed';
    if (status === 'HOLDING')
    return 'bg-gold-400 border-gold-500 text-white cursor-not-allowed';
    if (price > 1500000)
    return 'bg-white border-navy-300 text-navy-700 hover:border-coral-400 hover:text-coral-500';
    return 'bg-white border-navy-200 text-navy-600 hover:border-coral-400 hover:text-coral-500';
  };

  return (
    <div className="w-full overflow-x-auto pb-4 sm:pb-8 scrollbar-hide">
      <div className="min-w-[420px] max-w-4xl mx-auto bg-white p-3 sm:p-5 md:p-8 rounded-2xl sm:rounded-3xl shadow-soft border border-navy-50">
        {/* Stage */}
        <div className="mb-6 sm:mb-10 md:mb-16 relative">
          <div className="h-8 sm:h-10 md:h-12 w-3/4 mx-auto bg-gradient-to-b from-navy-100 to-transparent rounded-t-[60px] sm:rounded-t-[80px] md:rounded-t-[100px] border-t-2 sm:border-t-4 border-navy-300 flex items-center justify-center">
            <span className="text-navy-400 font-heading font-bold tracking-widest uppercase text-[10px] sm:text-xs md:text-sm">
              Sân Khấu
            </span>
          </div>
        </div>

        {/* Seat Grid */}
        <div className="flex flex-col gap-1.5 sm:gap-2.5 md:gap-4">
          {rows.keys.map((rowLabel) =>
          <div
            key={rowLabel}
            className="flex items-center justify-center gap-1 sm:gap-2 md:gap-4">
            
              <div className="w-4 sm:w-6 md:w-8 text-center font-bold text-navy-400 text-[10px] sm:text-xs md:text-sm flex-shrink-0">
                {rowLabel}
              </div>

              <div className="flex gap-[3px] sm:gap-1.5 md:gap-2">
                {rows.data[rowLabel].map((seat) => {
                const isSelected = selectedSeatIds.includes(seat.id);
                const isAvailable = seat.status === 'AVAILABLE';
                return (
                  <motion.button
                    key={seat.id}
                    whileHover={
                    isAvailable ?
                    {
                      scale: 1.1
                    } :
                    {}
                    }
                    whileTap={
                    isAvailable ?
                    {
                      scale: 0.95
                    } :
                    {}
                    }
                    onClick={() => isAvailable && onSeatToggle(seat.id)}
                    disabled={!isAvailable}
                    className={`w-6 h-6 sm:w-8 sm:h-8 md:w-10 md:h-10 rounded-t-md sm:rounded-t-lg rounded-b-sm border sm:border-2 flex items-center justify-center text-[8px] sm:text-[10px] md:text-xs font-semibold transition-colors ${getSeatColor(seat.status, isSelected, seat.price)}`}
                    title={`Ghế ${rowLabel}${seat.seat.seat_number} - ${formatCurrency(seat.price)}`}>
                    
                      {seat.seat.seat_number}
                    </motion.button>);

              })}
              </div>

              <div className="w-4 sm:w-6 md:w-8 text-center font-bold text-navy-400 text-[10px] sm:text-xs md:text-sm flex-shrink-0">
                {rowLabel}
              </div>
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="mt-6 sm:mt-8 md:mt-12 pt-4 sm:pt-6 md:pt-8 border-t border-navy-50 flex flex-wrap justify-center gap-3 sm:gap-5 md:gap-8">
          {[
          {
            bg: 'bg-white border-navy-300',
            label: 'Trống (VIP)'
          },
          {
            bg: 'bg-white border-navy-200',
            label: 'Trống (Thường)'
          },
          {
            bg: 'bg-coral-500 border-coral-600',
            label: 'Đã chọn'
          },
          {
            bg: 'bg-navy-100 border-navy-200',
            label: 'Đã bán'
          },
          {
            bg: 'bg-gold-400 border-gold-500',
            label: 'Đang giữ'
          }].
          map((item) =>
          <div
            key={item.label}
            className="flex items-center gap-1.5 sm:gap-2">
            
              <div
              className={`w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 rounded-t-md sm:rounded-t-lg rounded-b-sm border sm:border-2 ${item.bg}`}>
            </div>
              <span className="text-[11px] sm:text-xs md:text-sm text-navy-600">
                {item.label}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>);
}