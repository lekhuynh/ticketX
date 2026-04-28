export interface Venue {
  id: string;
  name: string;
  address: string;
  capacity: number;
}

export interface Event {
  id: string;
  venue_id: string;
  name: string;
  description: string;
  image_url: string;
  category: string;
  is_active: boolean;
}

export interface Showtime {
  id: string;
  event_id: string;
  start_time: string; // ISO string
}

export interface Seat {
  id: string;
  venue_id: string;
  row_label: string;
  seat_number: number;
}

export interface ShowtimeSeat {
  id: string;
  showtime_id: string;
  seat_id: string;
  price: number;
  status: 'AVAILABLE' | 'HOLDING' | 'BOOKED';
}

// Combined types for easier UI rendering
export interface PopulatedEvent extends Event {
  venue: Venue;
  showtimes: Showtime[];
  minPrice: number;
}

export interface PopulatedShowtimeSeat extends ShowtimeSeat {
  seat: Seat;
}