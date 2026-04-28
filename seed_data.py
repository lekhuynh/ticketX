import asyncio
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.models.event import Event
from app.db.models.venue import Venue
from app.db.models.showtime import Showtime
from app.db.models.seat import Seat
from app.db.models.showtime_seat import ShowtimeSeat
from app.db.models.enums import SeatStatus
from sqlalchemy import text

DATABASE_URL = settings.DATABASE_URL

async def seed():
    engine = create_async_engine(
        DATABASE_URL, 
        connect_args={"prepared_statement_cache_size": 0}
    )
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Create a venue with unique name
        suffix = str(uuid.uuid4())[:8]
        venue_id = uuid.uuid4()
        venue = Venue(
            id=venue_id,
            name=f'Nhà Hát Bến Thành {suffix}',
            address='6 Mạc Đĩnh Chi, Quận 1, TP. Hồ Chí Minh',
            capacity=1000
        )
        session.add(venue)
        
        # Create some seats for the venue
        seats = []
        for row in ['A', 'B', 'C']:
            for num in range(1, 9):
                seat = Seat(
                    id=uuid.uuid4(),
                    venue_id=venue_id,
                    row_label=row,
                    seat_number=num
                )
                session.add(seat)
                seats.append(seat)
        
        # Create an event
        event_id = uuid.uuid4()
        event = Event(
            id=event_id,
            venue_id=venue_id,
            name=f'Hài Kịch: Chuyện Lạ {suffix}',
            description='Một vở hài kịch đặc sắc hội tụ những nghệ sĩ gạo cội, hứa hẹn mang lại những giây phút sảng khoái.',
            image_url='https://images.unsplash.com/photo-1507676184212-d03ab07a01bf?auto=format&fit=crop&q=80&w=1600',
            category='Hài kịch',
            is_active=True
        )
        session.add(event)
        
        # Create a showtime
        start_time = datetime.now() + timedelta(days=5)
        end_time = start_time + timedelta(hours=3)
        showtime_id = uuid.uuid4()
        showtime = Showtime(
            id=showtime_id,
            event_id=event_id,
            start_time=start_time,
            end_time=end_time
        )
        session.add(showtime)
        
        # Create showtime seats
        for seat in seats:
            status = SeatStatus.AVAILABLE
            price = Decimal('300000.00')
            
            showtime_seat = ShowtimeSeat(
                id=uuid.uuid4(),
                showtime_id=showtime_id,
                seat_id=seat.id,
                price=price,
                status=status,
                created_at=datetime.now()
            )
            session.add(showtime_seat)
        
        await session.commit()
        print(f"Seed data created! Event: {event.name}")
        print(f"Showtime ID: {showtime_id}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
