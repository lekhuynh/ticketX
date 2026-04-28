import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  ClockIcon } from 'lucide-react';
import { PopulatedEvent, PopulatedShowtimeSeat, Showtime } from '../types';
import { eventApi, orderApi, paymentApi, seatApi, showtimeApi } from '../services/api';
import { formatCurrency, formatDate } from '../utils/format';

interface CheckoutPageProps {
  showtimeId: string;
  selectedSeatIds: string[];
  onBack: () => void;
}

export function CheckoutPage({
  showtimeId,
  selectedSeatIds,
  onBack,
}: CheckoutPageProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentEvent, setCurrentEvent] = useState<PopulatedEvent | null>(null);
  const [currentShowtime, setCurrentShowtime] = useState<Showtime | null>(null);
  const [selectedSeatsData, setSelectedSeatsData] = useState<PopulatedShowtimeSeat[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [order, setOrder] = useState<any>(null);
  const [timeLeft, setTimeLeft] = useState<number>(0);
  const [orderError, setOrderError] = useState<string | null>(null);
  const orderCreatedRef = useRef(false);

  useEffect(() => {
    const initializeCheckout = async () => {
      try {
        setLoading(true);
        
        // 1. Hold seats first by creating Order
        if (!orderCreatedRef.current) {
          orderCreatedRef.current = true;
          try {
            const orderData = {
              showtime_id: showtimeId,
              showtime_seat_ids: selectedSeatIds,
            };
            const createdOrder = await orderApi.create(orderData);
            setOrder(createdOrder);
          } catch(err: any) {
             console.error('Failed to hold seats:', err);
             const errorMsg = err.response?.data?.detail || 'Không thể giữ ghế. Có thể ghế đã được người dùng khác đặt mất.';
             setOrderError(errorMsg);
             setLoading(false);
             return;
          }
        }

        // 2. Fetch event and showtime info
        const showtimeData = await showtimeApi.getById(showtimeId);
        setCurrentShowtime(showtimeData);

        const eventData = await eventApi.getById(showtimeData.event_id);
        setCurrentEvent({
          ...eventData,
          venue: eventData.venue || { id: '', name: 'Unknown Venue', address: '', capacity: 0 },
          showtimes: eventData.showtimes || [],
          minPrice: 0
        });

        // 3. Get seat data
        const allSeatsForShowtime = await seatApi.getByShowtimeId(showtimeId);
        const filteredSeats = allSeatsForShowtime.filter((s: any) => selectedSeatIds.includes(s.id));
        setSelectedSeatsData(filteredSeats);
      } catch (err) {
        console.error('Failed to fetch checkout data:', err);
        setError('Không thể tải thông tin thanh toán.');
      } finally {
        setLoading(false);
      }
    };

    initializeCheckout();
  }, [showtimeId, selectedSeatIds]);

  // Timer effect
  useEffect(() => {
    if (!order || !order.expires_at) return;

    const calculateTimeLeft = () => {
      // Backend may return UTC or local time string. 
      // Ensure properly parsed as UTC if needed. Python ISO format handles this.
      const expiresAt = new Date(order.expires_at).getTime();
      const now = new Date().getTime();
      const difference = expiresAt - now;
      return difference > 0 ? Math.floor(difference / 1000) : 0;
    };

    setTimeLeft(calculateTimeLeft());

    const timer = setInterval(() => {
      const left = calculateTimeLeft();
      setTimeLeft(left);
      if (left <= 0) {
        clearInterval(timer);
        setOrderError('Thời gian giữ ghế đã kết thúc. Vui lòng quay lại chọn ghế khác.');
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [order]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const totalPrice = selectedSeatsData.reduce(
    (sum, seat) => sum + seat.price,
    0
  );

  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!order) return;
    setIsProcessing(true);
    
    try {
      // 1. Create payment and get VNPAY URL
      const paymentData = {
        order_id: order.id,
        provider: 'vnpay'
      };
      
      const paymentResponse = await paymentApi.create(paymentData);
      
      if (paymentResponse.payment_url) {
        // 2. Redirect to VNPAY
        window.location.href = paymentResponse.payment_url;
      } else {
        throw new Error('Không nhận được URL thanh toán từ hệ thống.');
      }
    } catch (err: any) {
      console.error('Payment failed:', err);
      const errorMsg = err.response?.data?.detail || 'Có lỗi xảy ra trong quá trình thanh toán. Vui lòng thử lại.';
      alert(errorMsg);
      setIsProcessing(false);
    }
  };

  if (orderError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <div className="bg-white p-8 rounded-3xl shadow-soft text-center max-w-md w-full border border-navy-50">
          <div className="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-navy-900 mb-4">Rất tiếc!</h2>
          <p className="text-navy-600 mb-8">{orderError}</p>
          <button 
            onClick={onBack}
            className="w-full bg-coral-500 hover:bg-coral-600 text-white px-6 py-3 rounded-xl font-bold transition-colors shadow-warm"
          >
            Quay lại chọn ghế
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-col gap-4 justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-coral-500"></div>
        <p className="text-navy-500 font-medium animate-pulse">Đang giữ ghế...</p>
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
        y: 20
      }}
      animate={{
        opacity: 1,
        y: 0
      }}
      className="min-h-screen bg-background py-12">
      
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-navy-500 hover:text-navy-900 mb-8 transition-colors font-medium">
          
          <ArrowLeftIcon className="w-5 h-5" />
          Quay lại chọn ghế
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Payment Form */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white p-8 rounded-3xl shadow-soft border border-navy-50">
              <h2 className="text-2xl font-heading font-bold text-navy-900 mb-6 flex items-center gap-3">
                <span className="bg-navy-900 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm">
                  1
                </span>
                Thông tin người đặt
              </h2>
              <form className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-navy-700 mb-1">
                      Họ và tên
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 rounded-xl border border-navy-200 focus:ring-2 focus:ring-coral-500 focus:border-coral-500 outline-none transition-all"
                      placeholder="Nguyễn Văn A" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-navy-700 mb-1">
                      Số điện thoại
                    </label>
                    <input
                      type="tel"
                      className="w-full px-4 py-3 rounded-xl border border-navy-200 focus:ring-2 focus:ring-coral-500 focus:border-coral-500 outline-none transition-all"
                      placeholder="090 123 4567" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-navy-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    className="w-full px-4 py-3 rounded-xl border border-navy-200 focus:ring-2 focus:ring-coral-500 focus:border-coral-500 outline-none transition-all"
                    placeholder="nguyenvana@example.com" />
                  <p className="text-xs text-navy-400 mt-1">
                    Vé điện tử sẽ được gửi về email này.
                  </p>
                </div>
              </form>
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-soft border border-navy-50">
              <h2 className="text-2xl font-heading font-bold text-navy-900 mb-6 flex items-center gap-3">
                <span className="bg-navy-900 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm">
                  2
                </span>
                Phương thức thanh toán
              </h2>
              <div className="space-y-3">
                <label className="flex items-center justify-between p-5 border-2 border-coral-500 bg-coral-50 rounded-2xl cursor-pointer shadow-sm">
                  <div className="flex items-center gap-4">
                    <div className="w-6 h-6 border-2 border-coral-500 rounded-full flex items-center justify-center">
                      <div className="w-3 h-3 bg-coral-500 rounded-full"></div>
                    </div>
                    <div>
                      <span className="font-bold text-navy-900 block">
                        Cổng thanh toán VNPAY
                      </span>
                      <span className="text-sm text-navy-500">
                        Thanh toán qua thẻ ATM, Visa, Master, QR Code
                      </span>
                    </div>
                  </div>
                  <img
                    src="https://sandbox.vnpayment.vn/paymentv2/Images/design/logo_vnpay.png"
                    alt="VNPAY"
                    className="h-8 object-contain" />
                </label>
              </div>
              
              <div className="mt-8 p-6 bg-navy-50 rounded-2xl border border-navy-100 flex items-start gap-3">
                <div className="mt-1">
                  <CheckCircleIcon className="w-5 h-5 text-green-500" />
                </div>
                <p className="text-sm text-navy-600 leading-relaxed">
                  Bạn sẽ được chuyển hướng đến cổng thanh toán bảo mật của <strong>VNPAY</strong> để hoàn tất giao dịch. TicketX không lưu trữ thông tin thẻ của bạn.
                </p>
              </div>
            </div>
          </div>

          {/* Order Summary */}
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-3xl shadow-soft border border-navy-50 sticky top-28">
              <h3 className="text-xl font-heading font-bold text-navy-900 mb-6 flex justify-between items-center">
                <span>Thông tin đặt vé</span>
                {timeLeft > 0 && (
                  <span className="text-sm bg-coral-50 text-coral-500 px-3 py-1 rounded-full font-bold flex items-center gap-1.5 shadow-sm border border-coral-100">
                    <ClockIcon className="w-4 h-4" />
                    {formatTime(timeLeft)}
                  </span>
                )}
              </h3>

              <div className="flex gap-4 mb-6 pb-6 border-b border-navy-100">
                <img
                  src={currentEvent.image_url || 'https://images.unsplash.com/photo-1540039155732-d674d40af4e0?auto=format&fit=crop&q=80&w=1600'}
                  alt={currentEvent.name}
                  className="w-20 h-20 object-cover rounded-lg" />
                
                <div>
                  <h4 className="font-bold text-navy-900 line-clamp-2 mb-1">
                    {currentEvent.name}
                  </h4>
                  <p className="text-sm text-navy-500">
                    {currentEvent.venue.name}
                  </p>
                </div>
              </div>

              <div className="space-y-4 mb-6 pb-6 border-b border-navy-100">
                <div className="flex justify-between text-sm">
                  <span className="text-navy-500">Thời gian</span>
                  <span className="font-medium text-navy-900 text-right">
                    {formatDate(currentShowtime.start_time)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-navy-500">
                    Ghế đã chọn ({selectedSeatsData.length})
                  </span>
                  <span className="font-medium text-navy-900 font-bold">
                    {selectedSeatsData.
                    map((s) => `${s.seat.row_label}${s.seat.seat_number}`).
                    join(', ')}
                  </span>
                </div>
              </div>

              <div className="space-y-3 mb-8">
                {selectedSeatsData.map((seat) =>
                <div key={seat.id} className="flex justify-between text-sm">
                    <span className="text-navy-600">
                      Ghế {seat.seat.row_label}
                      {seat.seat.seat_number}
                    </span>
                    <span className="font-medium text-navy-900">
                      {formatCurrency(seat.price)}
                    </span>
                  </div>
                )}
                <div className="flex justify-between text-sm pt-3 border-t border-navy-50">
                  <span className="text-navy-500">Phí dịch vụ</span>
                  <span className="font-medium text-navy-900">Miễn phí</span>
                </div>
              </div>

              <div className="flex justify-between items-end mb-8">
                <span className="text-navy-900 font-bold">Tổng cộng</span>
                <span className="text-3xl font-bold text-coral-500">
                  {formatCurrency(totalPrice)}
                </span>
              </div>

              <button
                onClick={handlePayment}
                disabled={isProcessing}
                className="w-full bg-coral-500 hover:bg-coral-600 disabled:bg-coral-300 text-white py-4 rounded-xl font-bold transition-colors shadow-warm flex justify-center items-center gap-2">
                
                {isProcessing ?
                <motion.div
                  animate={{
                    rotate: 360
                  }}
                  transition={{
                    repeat: Infinity,
                    duration: 1,
                    ease: 'linear'
                  }}
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full" /> :
                <>
                    <CheckCircleIcon className="w-5 h-5" />
                    Xác nhận thanh toán
                  </>
                }
              </button>
              <p className="text-xs text-center text-navy-400 mt-4">
                Bằng việc thanh toán, bạn đồng ý với Điều khoản sử dụng của
                chúng tôi.
              </p>
            </div>
          </div>
        </div>
      </div>
    </motion.div>);
}