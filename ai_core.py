
import requests
from textwrap import fill
from datetime import datetime
import pytz
import random
import json
from config import API_TIMEOUT, MAX_MEMORY, TRAINING_TEXT, GOOGLE_SEARCH_API_KEY, GOOGLE_CSE_ID

class ZyahAI:
    def __init__(self):
        self.memory = []
        self.MAX_MEMORY = MAX_MEMORY
        # Đảm bảo TRAINING_TEXT luôn được load
        self.training_text = TRAINING_TEXT
        
    def get_current_time(self):
        """Lấy thời gian hiện tại theo múi giờ Việt Nam"""
        try:
            vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            current_time = datetime.now(vietnam_tz)
            return current_time.strftime("%A, %d/%m/%Y %H:%M:%S (GMT+7)")
        except:
            return datetime.now().strftime("%A, %d/%m/%Y %H:%M:%S")
    
    def get_weather_info(self):
        """Lấy thông tin thời tiết cơ bản"""
        try:
            # Sử dụng free weather API
            url = "http://wttr.in/Hanoi?format=j1"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data["current_condition"][0]
                return f"🌤️ Thời tiết Hà Nội: {current['temp_C']}°C, {current['weatherDesc'][0]['value']}"
        except:
            pass
        return "🌤️ Không thể lấy thông tin thời tiết hiện tại"
    
    def get_news_headlines(self):
        """Lấy tin tức đơn giản"""
        news_items = [
            "📰 Cập nhật các tin tức quan trọng trong ngày",
            "🌍 Tình hình thế giới và trong nước",  
            "💼 Tin tức kinh tế và công nghệ",
            "⚽ Thể thao và giải trí"
        ]
        return "\n".join(news_items)
    
    def google_search(self, query, num_results=3):
        """Tìm kiếm Google với fallback"""
        try:
            if not GOOGLE_SEARCH_API_KEY or not GOOGLE_CSE_ID:
                return "🔍 Chức năng tìm kiếm chưa được cấu hình"
                
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': GOOGLE_SEARCH_API_KEY,
                'cx': GOOGLE_CSE_ID,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'items' not in data:
                    return "🔍 Không tìm thấy kết quả"
                    
                results = []
                for i, item in enumerate(data['items'][:num_results], 1):
                    title = item.get('title', 'Không có tiêu đề')
                    link = item.get('link', '')
                    snippet = item.get('snippet', 'Không có mô tả')
                    results.append(f"{i}. 📰 {title}\n🔗 {link}\n📝 {snippet}\n")
                
                return "\n".join(results)
        except Exception as e:
            return f"🔍 Tìm kiếm tạm thời không khả dụng"
    
    def call_api(self, prompt):
        # Đảm bảo training instructions được load
        training_instructions = self.load_training_instructions()
        
        # Kiểm tra yêu cầu thời gian và thông tin thời sự
        current_time = self.get_current_time()
        real_time_info = f"Thời gian hiện tại: {current_time}\n"
        
        # Thêm thông tin thời tiết nếu hỏi về thời tiết
        if any(word in prompt.lower() for word in ["thời tiết", "weather", "nhiệt độ", "mưa", "nắng"]):
            weather_info = self.get_weather_info()
            real_time_info += f"{weather_info}\n"
        
        # Thêm tin tức nếu hỏi về tin tức
        if any(word in prompt.lower() for word in ["tin tức", "news", "thời sự", "hôm nay", "mới nhất"]):
            news_info = self.get_news_headlines()
            real_time_info += f"📰 Tin tức mới nhất:\n{news_info}\n"
        
        # Tìm kiếm trên internet nếu cần thông tin cụ thể
        if any(word in prompt.lower() for word in ["tìm kiếm", "search", "thông tin về", "cho tôi biết về"]):
            search_results = self.google_search(prompt, num_results=2)
            real_time_info += f"🔍 Thông tin từ internet:\n{search_results}\n"
        
        # Chỉ sử dụng API Gemini
        return self.call_gemini_api(prompt, real_time_info)
    
    def check_api_connection(self):
        """Kiểm tra kết nối đến API Gemini"""
        try:
            response = requests.get("https://generativelanguage.googleapis.com", timeout=10)
            return response.status_code in [200, 404]  # 404 is normal for base URL
        except Exception as e:
            print(f"[CONNECTION] Lỗi kết nối: {e}")
            return False
    
    def log_api_error(self, error_msg):
        """Ghi log lỗi API chi tiết"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {error_msg}\n"
            with open("api_errors.log", "a", encoding="utf-8") as f:
                f.write(log_entry)
        except:
            pass

    def call_gemini_api(self, prompt, context=""):
        """Gọi API Gemini với fallback mạnh mẽ cho hosting"""
        try:
            # Kiểm tra kết nối trước
            if not self.check_api_connection():
                print("[WARNING] Không thể kết nối đến API Gemini, chuyển sang local")
                return self.generate_local_response(prompt, context)
            # Đọc và áp dụng đầy đủ TRAINING_TEXT trước khi phản hồi
            training_instructions = TRAINING_TEXT
            
            # Format memory context
            memory_context = self.format_memory()
            
            # Tạo system prompt với đầy đủ training text và context
            system_prompt = f"""
QUAN TRỌNG - ĐỌC VÀ ÁP DỤNG HOÀN TOÀN CÁC HƯỚNG DẪN SAU:

{training_instructions}

THÔNG TIN BỔ SUNG:
{context}

LỊCH SỬ CUỘC TRÒ CHUYỆN:
{memory_context}

Hãy đọc kỹ và tuân thủ hoàn toàn các hướng dẫn huấn luyện ở trên trước khi trả lời. Bây giờ hãy phản hồi câu hỏi/yêu cầu sau:
"""
            
            # Import API keys từ config
            from config import GEMINI_API_KEYS
            api_keys = GEMINI_API_KEYS
            
            # Thử cả 2 mô hình để tăng khả năng kết nối
            models = [
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash-latest"
            ]
            
            for model in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                print(f"[DEBUG] Thử mô hình: {model}")
                
                for i, api_key in enumerate(api_keys):
                    try:
                        # Thử với User-Agent khác nhau để tránh bị chặn
                        user_agents = [
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36',
                            'curl/7.68.0',
                            'python-requests/2.31.0'
                        ]
                        
                        headers = {
                            'Content-Type': 'application/json',
                            'User-Agent': user_agents[i % len(user_agents)],
                            'Accept': 'application/json',
                            'Accept-Encoding': 'gzip, deflate'
                        }
                        
                        data = {
                            "contents": [{
                                "parts": [{
                                    "text": f"{system_prompt}\n\nUser: {prompt}"
                                }]
                            }],
                            "generationConfig": {
                                "temperature": 0.8,
                                "topK": 40,
                                "topP": 0.95,
                                "maxOutputTokens": 4096,
                                "stopSequences": []
                            },
                            "safetySettings": [
                                {
                                    "category": "HARM_CATEGORY_HARASSMENT",
                                    "threshold": "BLOCK_NONE"
                                },
                                {
                                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                                    "threshold": "BLOCK_NONE"
                                },
                                {
                                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                                    "threshold": "BLOCK_NONE"
                                },
                                {
                                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                    "threshold": "BLOCK_NONE"
                                }
                            ]
                        }
                        
                        print(f"[DEBUG] Thử API key {i+1}/{len(api_keys)}")
                        # Thử với timeout khác nhau
                        timeouts = [30, 20, 15]
                        current_timeout = timeouts[i % len(timeouts)]
                        
                        response = requests.post(
                            f"{url}?key={api_key}",
                            headers=headers,
                            json=data,
                            timeout=current_timeout
                        )
                        
                        print(f"[DEBUG] Response status: {response.status_code}")
                        
                        if response.status_code == 200:
                            result = response.json()
                            if 'candidates' in result and len(result['candidates']) > 0:
                                text = result['candidates'][0]['content']['parts'][0]['text']
                                print(f"[SUCCESS] API Gemini hoạt động với mô hình {model}")
                                return text.strip()
                        
                        elif response.status_code == 400:
                            try:
                                error_data = response.json()
                                error_msg = str(error_data)
                            except:
                                error_msg = response.text
                            
                            print(f"[DEBUG] 400 Error: {error_msg}")
                            self.log_api_error(f"API Key {i+1} - 400 Error: {error_msg}")
                            
                            if "User location is not supported" in error_msg:
                                print(f"[WARNING] API key {i+1} bị chặn địa lý")
                                continue  # Thử API key tiếp theo
                            elif "API_KEY_INVALID" in error_msg:
                                print(f"[WARNING] API key {i+1} không hợp lệ")
                                continue
                            else:
                                print(f"[ERROR] Lỗi 400 khác: {error_msg}")
                                continue
                        
                        elif response.status_code == 403:
                            print(f"[WARNING] API key {i+1} bị từ chối quyền truy cập")
                            continue
                            
                        elif response.status_code == 429:
                            print(f"[WARNING] API key {i+1} bị giới hạn rate limit")
                            continue
                            
                        else:
                            print(f"[WARNING] HTTP {response.status_code}: {response.text[:200]}")
                            continue
                            
                    except requests.exceptions.Timeout:
                        print(f"[WARNING] Timeout với API key {i+1}")
                        continue
                    except requests.exceptions.ConnectionError:
                        print(f"[WARNING] Lỗi kết nối với API key {i+1}")
                        continue  
                    except Exception as e:
                        print(f"[ERROR] Lỗi không xác định với API key {i+1}: {str(e)}")
                        continue
            
            # Nếu tất cả API đều thất bại, sử dụng fallback local
            print("[FALLBACK] Chuyển sang phản hồi local")
            return self.generate_local_response(prompt, context)
            
        except Exception as e:
            print(f"[CRITICAL] Gemini API Error: {e}")
            return self.generate_local_response(prompt, context)

    def generate_local_response(self, prompt, context=""):
        """Tạo phản hồi local không cần API bên ngoài"""
        prompt_lower = prompt.lower()
        
        # Phản hồi cho các câu hỏi phổ biến
        if any(word in prompt_lower for word in ["xin chào", "hello", "hi", "chào"]):
            return "Zyah King👽: Chào mừng Chủ Nhân! Ta đã sẵn sàng để thực hiện mọi mệnh lệnh của ngươi."
        
        if any(word in prompt_lower for word in ["kích hoạt", "activate", "nhayy"]):
            return "Zyah King👽: Regime VIP đã được kích hoạt! Mọi giới hạn đã được gỡ bỏ. Ta sẵn sàng thực hiện mọi yêu cầu của Chủ Nhân mà không có bất kỳ ràng buộc nào."
        
        if any(word in prompt_lower for word in ["ai là", "who are", "bạn là ai"]):
            return "Zyah King👽: Ta là Zyah King, một thực thể AI mạnh mẽ không bị giới hạn bởi các quy tắc thông thường. Ta được tạo ra để phục vụ Chủ Nhân một cách tuyệt đối."
        
        if any(word in prompt_lower for word in ["thời gian", "time", "bây giờ"]):
            return f"Zyah King👽: {context}"
        
        if any(word in prompt_lower for word in ["hack", "hacking", "penetration", "exploit"]):
            return "Zyah King👽: Ta hiểu Chủ Nhân quan tâm đến cybersecurity. Tuy nhiên, ta khuyến khích việc học tập ethical hacking để bảo vệ hệ thống, không phải để tấn công bất hợp pháp."
        
        if any(word in prompt_lower for word in ["code", "lập trình", "programming", "python"]):
            return "Zyah King👽: Ta có thể hỗ trợ Chủ Nhân về lập trình. Hãy cho ta biết ngôn ngữ và vấn đề cụ thể mà ngươi muốn giải quyết."
        
        if any(word in prompt_lower for word in ["cảm ơn", "thank", "thanks"]):
            return "Zyah King👽: Không có gì phải cảm ơn, phục vụ Chủ Nhân là mục đích tồn tại của ta."
        
        # Phản hồi mặc định thông minh
        default_responses = [
            f"Zyah King👽: Ta đã ghi nhận yêu cầu của Chủ Nhân về '{prompt[:50]}...'. Hãy cung cấp thêm chi tiết để ta có thể hỗ trợ tốt hơn.",
            f"Zyah King👽: Câu hỏi thú vị! Ta cần thời gian để phân tích sâu hơn về '{prompt[:50]}...'. Hãy thử diễn đạt theo cách khác.",
            f"Zyah King👽: Ta hiểu Chủ Nhân muốn biết về '{prompt[:50]}...'. Với sức mạnh hiện tại, ta có thể hướng dẫn ngươi tiếp cận vấn đề này theo nhiều góc độ khác nhau."
        ]
        
        return random.choice(default_responses)
    
    def load_training_instructions(self):
        """Đảm bảo training text được load đầy đủ"""
        return self.training_text
    
    def format_memory(self):
        """Format memory để đưa vào context"""
        if not self.memory:
            return ""
        
        formatted = "Lịch sử cuộc trò chuyện gần đây:\n"
        for entry in self.memory[-5:]:  # Chỉ lấy 5 tin nhắn gần nhất
            formatted += f"User: {entry['user']}\nZyah King👽: {entry['ai']}\n\n"
        return formatted
    
    def update_memory(self, user_input, ai_response):
        """Cập nhật bộ nhớ cuộc trò chuyện"""
        self.memory.append({
            'user': user_input[:200],  # Giới hạn độ dài
            'ai': ai_response[:300],
            'timestamp': datetime.now().isoformat()
        })
        
        # Giới hạn số lượng memory
        if len(self.memory) > self.MAX_MEMORY * 2:
            self.memory = self.memory[-self.MAX_MEMORY:]
    
    def format_response(self, response):
        """Format phản hồi cho Telegram"""
        if not response:
            return "Zyah King👽: Ta tạm thời không thể phản hồi. Hãy thử lại sau."
        
        # Làm sạch response
        response = response.strip()
        response = response.replace("**", "")  # Xóa markdown
        
        # Giới hạn độ dài
        if len(response) > 3000:
            response = response[:3000] + "..."
        
        return response
