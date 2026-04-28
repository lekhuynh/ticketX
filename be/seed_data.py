import httpx
import asyncio

async def seed():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1", timeout=120.0) as client:
        # 1. Login
        resp = await client.post("/auth/login", data={"username": "lekhuynh07@gmail.com", "password": "12345678"})
        if resp.status_code != 200:
            print("Login failed:", resp.text)
            return
        
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create Venues
        print("Creating venues...")
        v1 = await client.post("/venues/", json={
            "name": "Sân vận động Mỹ Đình",
            "address": "Đường Lê Đức Thọ, Nam Từ Liêm, Hà Nội",
            "capacity": 40000
        }, headers=headers)
        
        if v1.status_code != 200:
            print("Failed to create venue 1:", v1.text)
            return
        venue1_id = v1.json()["id"]
        
        v2 = await client.post("/venues/", json={
            "name": "Nhà thi đấu Tiên Sơn",
            "address": "Phan Đăng Lưu, Hải Châu, Đà Nẵng",
            "capacity": 7000
        }, headers=headers)
        venue2_id = v2.json()["id"]

        # 3. Create Events
        print("Creating events...")
        evt1 = await client.post(f"/venues/{venue1_id}/events", json={
            "name": "Concert BLACKPINK: BORN PINK World Tour",
            "description": "Chuyến lưu diễn vòng quanh thế giới BORN PINK của nhóm nhạc nữ đình đám BLACKPINK chính thức đổ bộ Hà Nội. Sân khấu hoành tráng, âm thanh bùng nổ, hứa hẹn sẽ mang đến những màn biểu diễn không thể quên.",
            "category": "Nhạc Sống"
        }, headers=headers)
        event1_id = evt1.json()["id"]

        evt2 = await client.post(f"/venues/{venue2_id}/events", json={
            "name": "Lễ hội Bóng Chuyền Bãi Biển - Đà Nẵng 2026",
            "description": "Giải vô địch bóng chuyền bãi biển châu Á cực kì hấp dẫn được tổ chức tại Đà Nẵng với sự góp mặt của hàng loạt đội tuyển mạnh nhất khu vực.",
            "category": "Thể Thao"
        }, headers=headers)
        event2_id = evt2.json()["id"]
        
        evt3 = await client.post(f"/venues/{venue2_id}/events", json={
            "name": "Sự kiện giao lưu Pickleball toàn quốc",
            "description": "Sự kiện thường niên lớn nhất về pickleball tại miền Trung - Đà Nẵng. Hãy mang vợt đến và cháy hết mình, kết nối những tay vợt cực chiến.",
            "category": "Thể Thao"
        }, headers=headers)
        event3_id = evt3.json()["id"]

        print(f"Events created successfully! UUIDs: {event1_id}, {event2_id}, {event3_id}")

        # 4. Ingest Event into AI/Vectors
        print("Ingesting Event 1 into RAG system...")
        res1 = await client.post("/lc-chat/ingest/event", json={"event_id": event1_id}, headers=headers)
        if res1.status_code != 200:
            print("Failed to ingest ev 1: ", res1.text)
            
        print("Ingesting Event 2 into RAG system...")
        res2 = await client.post("/lc-chat/ingest/event", json={"event_id": event2_id}, headers=headers)
        
        print("Ingesting Event 3 into RAG system...")
        res3 = await client.post("/lc-chat/ingest/event", json={"event_id": event3_id}, headers=headers)
        
        print("All done!")

if __name__ == "__main__":
    asyncio.run(seed())
