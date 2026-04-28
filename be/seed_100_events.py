import asyncio
import uuid
import random
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import from app
from app.core.config import settings
from app.db.models.event import Event
from app.db.models.venue import Venue
from app.db.models.showtime import Showtime
from app.db.models.seat import Seat
from app.db.models.showtime_seat import ShowtimeSeat
from app.db.models.enums import SeatStatus
from app.langchain.ingest_service import refresh_ai_docs_for_event

DATABASE_URL = settings.DATABASE_URL

ADJECTIVES = ["Hấp dẫn", "Đặc biệt", "Mới lạ", "Chấn động", "Kinh điển", "Hài hước", "Lãng mạn", "Bùng nổ", "Tuyệt đỉnh", "Sâu lắng"]
NOUNS = ["Đại nhạc hội", "Concert", "Hài kịch", "Kịch nói", "Triển lãm", "Hội thảo", "Giao lưu", "Biểu diễn", "Liveshow", "Talkshow"]
ARTISTS = ["Sơn Tùng", "Mỹ Tâm", "Đen Vâu", "Hoài Linh", "Trấn Thành", "Hồ Ngọc Hà", "Bằng Kiều", "Lệ Quyên", "Hà Anh Tuấn", "Vũ Cát Tường", "Amee", "Karik"]
CATEGORIES = ["Âm nhạc", "Hài kịch", "Hội thảo", "Nghệ thuật", "Thể thao", "Giao lưu"]

async def seed():
    engine = create_async_engine(
        DATABASE_URL, 
        connect_args={"prepared_statement_cache_size": 0}
    )
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # 1. Create a venue
        suffix = str(uuid.uuid4())[:8]
        venue_id = uuid.uuid4()
        venue = Venue(
            id=venue_id,
            name=f'Trung tâm Sự kiện Grand Palace {suffix}',
            address='142/18 Cộng Hòa, Phường 4, Tân Bình, TP Hồ Chí Minh',
            capacity=1000
        )
        session.add(venue)
        
        # Create some seats for the venue
        seats = []
        for row in ['A', 'B', 'C']:
            for num in range(1, 9):
                seat_id = uuid.uuid4()
                seat = Seat(
                    id=seat_id,
                    venue_id=venue_id,
                    row_label=row,
                    seat_number=num
                )
                session.add(seat)
                seats.append(seat)

        await session.commit()
        await session.refresh(venue)

        print(f"Đã tạo xong Venue: {venue.name}")

        # 2. Create 100 events
        print("Bắt đầu tạo 100 kiện và sinh vector...")
        event_ids = []
        for i in range(1, 101):
            event_id = uuid.uuid4()
            adj = random.choice(ADJECTIVES)
            noun = random.choice(NOUNS)
            artist = random.choice(ARTISTS)
            name = f"{noun} {adj}: Đêm của {artist} - #{i}"
            desc = f"Một chương trình {noun.lower()} mang phong cách {adj.lower()} chưa từng có. Hãy đến và tận hưởng những màn biểu diễn bùng nổ cùng {artist}. Đây là sự kiện không thể bỏ lỡ dành cho những người yêu mến nghệ thuật thực thụ."
            
            event = Event(
                id=event_id,
                venue_id=venue_id,
                name=name,
                description=desc,
                image_url=f'https://source.unsplash.com/random/800x600/?concert,event&sig={i}',
                category=random.choice(CATEGORIES),
                is_active=True
            )
            session.add(event)
            event_ids.append(event_id)

            # Create a showtime for this event
            start_time = datetime.now() + timedelta(days=random.randint(2, 60))
            end_time = start_time + timedelta(hours=random.randint(2, 4))
            showtime_id = uuid.uuid4()
            showtime = Showtime(
                id=showtime_id,
                event_id=event_id,
                start_time=start_time,
                end_time=end_time
            )
            session.add(showtime)

        await session.commit() 
        print("Đã lưu 100 sự kiện vào cơ sở dữ liệu. Bắt đầu build vector (có thể mất khoảng 1-2 phút). HÃY KIÊN NHẪN CHỜ ĐỢI...")

        # 3. Generate Embeddings to ai_docs
        for idx, e_id in enumerate(event_ids, 1):
            await refresh_ai_docs_for_event(session, str(e_id))
            if idx % 10 == 0:
                print(f" - Đã nạp xong vector cho {idx}/100 sự kiện...")

        print("Hoàn tất! Cả 100 sự kiện đã được lưu thành công vào ai_docs.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed())
