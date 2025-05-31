
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import main bot class
from main import ZyahBot
from config import BOT_TOKEN

if __name__ == "__main__":
    try:
        print("🚀 Đang khởi động Zyah King👽...")
        
        # Kiểm tra BOT_TOKEN
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            print("❌ Vui lòng cấu hình BOT_TOKEN trong config.py")
            sys.exit(1)
            
        # Khởi động bot
        bot = ZyahBot(BOT_TOKEN)
        print("✅ Bot đã được khởi tạo thành công")
        bot.run()
        
    except KeyboardInterrupt:
        print("\n[👋] Bot đã được tắt bởi người dùng")
    except Exception as e:
        print(f"[💥] Lỗi nghiêm trọng: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("[👋] Zyah King👽 đã tắt an toàn")
