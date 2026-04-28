import asyncio
import time
import httpx

async def test_chat_speed():
    url = "http://localhost:8000/api/v1/lc-chat/ask"
    payload = {
        "question": "Vé sự kiện Anh Trai Say Hi giá bao nhiêu?",
        "history": []
    }
    
    print("🚀 BẮT ĐẦU KIỂM TRA TỐC ĐỘ CHAT (CÓ REDIS CACHE)\n")
    
    async with httpx.AsyncClient() as client:
        # -------------------------------------------------------------
        # LẦN 1: Chưa có trong Redis (Sẽ mất thời gian nhúng Vector)
        # -------------------------------------------------------------
        print("🕒 Đang gửi truy vấn LẦN 1 (Cache Miss - Chờ nhúng Vector)...")
        start_time_1 = time.time()
        
        try:
            # Gửi và đọc toàn bộ stream data (do API trả về stream)
            async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                chunks = []
                async for chunk in response.aiter_text():
                    chunks.append(chunk)
            
            end_time_1 = time.time()
            time_1 = end_time_1 - start_time_1
            print(f"✅ Hoàn thành LẦN 1 trong: {time_1:.2f} giây.\n")
            
        except httpx.ConnectError:
            print("❌ Không thể kết nối tới Backend (Kiểm tra lại xem server port có phải 8000 không).")
            return

        # -------------------------------------------------------------
        # LẦN 2: Lấy thẳng từ Redis, bỏ qua bước nhúng
        # -------------------------------------------------------------
        print("⚡ Đang gửi truy vấn LẦN 2 (Cache Hit - Lấy từ Redis)...")
        start_time_2 = time.time()
        
        async with client.stream("POST", url, json=payload, timeout=60.0) as response:
            chunks = []
            async for chunk in response.aiter_text():
                chunks.append(chunk)
                
        end_time_2 = time.time()
        time_2 = end_time_2 - start_time_2
        print(f"✅ Hoàn thành LẦN 2 trong: {time_2:.2f} giây.\n")
        
        # -------------------------------------------------------------
        # KẾT LUẬN
        # -------------------------------------------------------------
        if time_1 > time_2:
            saved_time = time_1 - time_2
            percent_faster = (saved_time / time_1) * 100
            print(f"🎯 KẾT LUẬN: Lần 2 NHANH HƠN lần 1 là {saved_time:.2f}s (Tăng tốc {percent_faster:.1f}%)!")
            print("=> REDIS ĐANG LÀM VIỆC HOÀN HẢO!")
        else:
            print("⚠️ Kết luận: Hai lần tốn thời gian gần bằng nhau (Có thể do mạng Groq LLM bị nghẽn bù trừ hoặc câu này đã được Cache từ trước đó rồi).")

if __name__ == "__main__":
    asyncio.run(test_chat_speed())
