
import json
import os
from datetime import datetime
from config import DATA_FILE, ADMIN_ID
from colors import Colors

class AdminManager:
    def __init__(self):
        self.authorized_users = self._load_users()

    def _load_users(self):
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    # Migrate old format to new format
                    if "user_details" not in data:
                        data["user_details"] = {}
                        for user_id in data.get("users", []):
                            data["user_details"][str(user_id)] = {
                                "user_id": user_id,
                                "granted_date": "Unknown",
                                "granted_by": "System",
                                "status": "active"
                            }
                    return data
            return {
                "users": [], 
                "admin": ADMIN_ID,
                "user_details": {}
            }
        except Exception as e:
            print(f"{Colors.ERROR}[!] Lỗi khi tải dữ liệu người dùng: {e}{Colors.RESET}")
            return {
                "users": [], 
                "admin": ADMIN_ID,
                "user_details": {}
            }

    def _save_users(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.authorized_users, f, indent=4)
        except Exception as e:
            print(f"{Colors.ERROR}[!] Lỗi khi lưu dữ liệu người dùng: {e}{Colors.RESET}")

    def is_authorized(self, user_id):
        return user_id in self.authorized_users["users"] or user_id == self.authorized_users["admin"]

    def is_admin(self, user_id):
        return user_id == self.authorized_users["admin"]

    def add_user(self, user_id, granted_by_id=None):
        if user_id in self.authorized_users["users"]:
            return f"Người dùng {user_id} đã được cấp quyền!"
        
        # Thêm vào danh sách users
        self.authorized_users["users"].append(user_id)
        
        # Lưu thông tin chi tiết
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        granted_by = granted_by_id if granted_by_id else "Admin"
        
        self.authorized_users["user_details"][str(user_id)] = {
            "user_id": user_id,
            "granted_date": current_time,
            "granted_by": granted_by,
            "status": "active"
        }
        
        self._save_users()
        return f"✅ Đã cấp quyền cho người dùng {user_id}\n📅 Thời gian: {current_time}\n👤 Được cấp bởi: {granted_by}"

    def remove_user(self, user_id):
        if user_id not in self.authorized_users["users"]:
            return f"Người dùng {user_id} chưa được cấp quyền!"
        
        self.authorized_users["users"].remove(user_id)
        
        # Cập nhật status thay vì xóa hoàn toàn
        if str(user_id) in self.authorized_users["user_details"]:
            self.authorized_users["user_details"][str(user_id)]["status"] = "revoked"
            self.authorized_users["user_details"][str(user_id)]["revoked_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self._save_users()
        return f"❌ Đã xóa quyền của người dùng {user_id}\n📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    def get_all_users(self):
        return self.authorized_users["users"] + [self.authorized_users["admin"]]

    def get_user_count(self):
        return len(self.authorized_users["users"])
    
    def get_user_details(self, user_id=None):
        """Lấy thông tin chi tiết của người dùng"""
        if user_id:
            return self.authorized_users["user_details"].get(str(user_id))
        return self.authorized_users["user_details"]
    
    def get_user_info_formatted(self):
        """Lấy thông tin người dùng định dạng đẹp"""
        details = self.authorized_users["user_details"]
        if not details:
            return "Chưa có người dùng nào được cấp quyền."
        
        result = "📋 **DANH SÁCH NGƯỜI DÙNG CHI TIẾT:**\n\n"
        for user_id, info in details.items():
            status_emoji = "✅" if info["status"] == "active" else "❌"
            result += f"{status_emoji} **User ID:** {info['user_id']}\n"
            result += f"📅 **Cấp quyền:** {info['granted_date']}\n"
            result += f"👤 **Cấp bởi:** {info['granted_by']}\n"
            result += f"🔵 **Trạng thái:** {info['status'].upper()}\n"
            if info.get("revoked_date"):
                result += f"❌ **Thu hồi:** {info['revoked_date']}\n"
            result += "─────────────────\n"
        
        return result
