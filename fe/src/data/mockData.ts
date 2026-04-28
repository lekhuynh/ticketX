import {
  Venue,
  Event,
  Showtime,
  Seat,
  ShowtimeSeat,
  PopulatedEvent } from
'../types';

export const venues: Venue[] = [
{
  id: 'v1',
  name: 'Nhà Hát Lớn Hà Nội',
  address: '01 Tràng Tiền, Hoàn Kiếm, Hà Nội',
  capacity: 600
},
{
  id: 'v2',
  name: 'Nhà Văn Hóa Thanh Niên TP.HCM',
  address: '4 Phạm Ngọc Thạch, Bến Nghé, Quận 1, TP.HCM',
  capacity: 1200
},
{
  id: 'v3',
  name: 'Gem Center',
  address: '8 Nguyễn Bỉnh Khiêm, Đa Kao, Quận 1, TP.HCM',
  capacity: 1500
}];


export const events: Event[] = [
{
  id: 'e1',
  venue_id: 'v1',
  name: 'Đêm Nhạc Trịnh - Nhớ Mùa Thu Hà Nội',
  description:
  'Một đêm nhạc tưởng nhớ cố nhạc sĩ Trịnh Công Sơn với những tình khúc vượt thời gian, được thể hiện bởi các giọng ca hàng đầu Việt Nam trong không gian sang trọng của Nhà Hát Lớn.',
  image_url:
  'https://images.unsplash.com/photo-1460723237483-7a6dc9d0b212?auto=format&fit=crop&q=80&w=1600',
  category: 'Âm nhạc',
  is_active: true
},
{
  id: 'e2',
  venue_id: 'v2',
  name: 'Liveshow Mỹ Tâm - Tri Âm',
  description:
  'Liveshow hoành tráng nhất năm của họa mi tóc nâu Mỹ Tâm, đánh dấu chặng đường 20 năm ca hát với những bản hit đình đám được phối mới hoàn toàn.',
  image_url:
  'https://images.unsplash.com/photo-1540039155732-d674d40af4e0?auto=format&fit=crop&q=80&w=1600',
  category: 'Concert',
  is_active: true
},
{
  id: 'e3',
  venue_id: 'v1',
  name: 'Vở Kịch Tấm Cám - Chuyện Chưa Kể',
  description:
  'Góc nhìn mới lạ về câu chuyện cổ tích quen thuộc qua lăng kính đương đại, với sự tham gia của dàn diễn viên gạo cội.',
  image_url:
  'https://images.unsplash.com/photo-1507676184212-d0330a15233c?auto=format&fit=crop&q=80&w=1600',
  category: 'Kịch nói',
  is_active: true
},
{
  id: 'e4',
  venue_id: 'v3',
  name: 'Hòa Nhạc Giao Hưởng Mùa Đông',
  description:
  'Đêm nhạc giao hưởng đẳng cấp quốc tế với sự tham gia của nhạc trưởng người Ý và dàn nhạc giao hưởng quốc gia.',
  image_url:
  'https://images.unsplash.com/photo-1514320291840-2e0a9bf2a9ae?auto=format&fit=crop&q=80&w=1600',
  category: 'Hòa nhạc',
  is_active: true
}];


export const showtimes: Showtime[] = [
{ id: 'st1', event_id: 'e1', start_time: '2025-10-15T20:00:00Z' },
{ id: 'st2', event_id: 'e1', start_time: '2025-10-16T20:00:00Z' },
{ id: 'st3', event_id: 'e2', start_time: '2025-11-20T19:30:00Z' },
{ id: 'st4', event_id: 'e3', start_time: '2025-09-05T20:00:00Z' },
{ id: 'st5', event_id: 'e4', start_time: '2025-12-24T20:30:00Z' }];


// Generate seats and showtime_seats dynamically
export const seats: Seat[] = [];
export const showtimeSeats: ShowtimeSeat[] = [];

const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
const seatsPerRow = 14;

venues.forEach((venue) => {
  rows.forEach((rowLabel, rowIndex) => {
    for (let i = 1; i <= seatsPerRow; i++) {
      const seatId = `seat-${venue.id}-${rowLabel}-${i}`;
      seats.push({
        id: seatId,
        venue_id: venue.id,
        row_label: rowLabel,
        seat_number: i
      });

      // For each seat, create a showtime_seat for all showtimes at this venue
      const venueShowtimes = showtimes.filter(
        (st) => events.find((e) => e.id === st.event_id)?.venue_id === venue.id
      );

      venueShowtimes.forEach((st) => {
        // VIP rows A-C are more expensive
        const price = rowIndex < 3 ? 2500000 : 1500000;

        // Randomize status to make it look realistic
        const rand = Math.random();
        let status: 'AVAILABLE' | 'HOLDING' | 'BOOKED' = 'AVAILABLE';
        if (rand > 0.85) status = 'BOOKED';else
        if (rand > 0.75) status = 'HOLDING';

        showtimeSeats.push({
          id: `sts-${st.id}-${seatId}`,
          showtime_id: st.id,
          seat_id: seatId,
          price,
          status
        });
      });
    }
  });
});

// Helper to get populated events for the UI
export const getPopulatedEvents = (): PopulatedEvent[] => {
  return events.map((event) => {
    const venue = venues.find((v) => v.id === event.venue_id)!;
    const eventShowtimes = showtimes.filter((st) => st.event_id === event.id);

    // Find min price for this event
    const eventShowtimeIds = eventShowtimes.map((st) => st.id);
    const relevantSeats = showtimeSeats.filter((sts) =>
    eventShowtimeIds.includes(sts.showtime_id)
    );
    const minPrice =
    relevantSeats.length > 0 ?
    Math.min(...relevantSeats.map((s) => s.price)) :
    0;

    return {
      ...event,
      venue,
      showtimes: eventShowtimes,
      minPrice
    };
  });
};

export const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(amount);
};

export const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};