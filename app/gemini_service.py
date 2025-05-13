import google.generativeai as genai
from app.config import Config
import os

class GeminiService:
    def __init__(self):
        # Cấu hình API key
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # Sử dụng model Gemini Pro
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
    def get_consultation(self, problem_features, topic_id):
        """Lấy tư vấn từ Gemini dựa trên đặc điểm của vấn đề"""
        
        # Ánh xạ topic_id với chủ đề
        topic_map = {
            1: "hợp đồng lao động",
            2: "thay đổi mức lương, lương làm thêm giờ và phụ cấp",
            3: "bảo hiểm xã hội và chế độ bảo hiểm"
        }
        
        topic = topic_map.get(topic_id, "luật lao động")
        
        # Chuyển đổi problem_features thành văn bản cho prompt
        features_text = self._format_features(problem_features)
        
        # Tạo prompt cho Gemini
        prompt = f"""
        Hãy đưa ra lời tư vấn chi tiết về {topic} cho một người lao động có các đặc điểm sau:
        
        {features_text}
        
        Lời tư vấn cần:
        1. Dựa trên Bộ luật Lao động Việt Nam 2019 và các quy định pháp luật hiện hành
        2. Cung cấp thông tin chính xác và trích dẫn điều luật cụ thể khi cần thiết
        3. Trình bày rõ ràng, dễ hiểu, phù hợp với trường hợp cụ thể
        4. Đưa ra hướng dẫn cụ thể về quyền lợi và nghĩa vụ của người lao động
        5. Độ dài khoảng 150-200 từ, đầy đủ nhưng súc tích
        """
        
        # Gọi API Gemini
        response = self.model.generate_content(prompt)
        
        # Lấy nội dung trả lời
        return response.text
    
    def _format_features(self, problem_features):
        """Chuyển đổi problem_features thành văn bản dễ đọc"""
        from app.models import Database
        
        db = Database()
        features_text = ""
        
        for feature in problem_features:
            dac_diem_id = feature['dac_diem_id']
            gia_tri = feature['gia_tri']
            
            # Lấy tên đặc điểm
            query = "SELECT ten_dac_diem FROM dac_diem WHERE id = %s"
            db.cursor.execute(query, (dac_diem_id,))
            result = db.cursor.fetchone()
            ten_dac_diem = result['ten_dac_diem'] if result else f"Đặc điểm {dac_diem_id}"
            
            # Lấy mô tả giá trị
            query = "SELECT mo_ta FROM chi_tiet_dac_diem WHERE dac_diem_id = %s AND gia_tri = %s"
            db.cursor.execute(query, (dac_diem_id, gia_tri))
            result = db.cursor.fetchone()
            mo_ta = result['mo_ta'] if result else gia_tri
            
            features_text += f"- {ten_dac_diem}: {mo_ta}\n"
        
        return features_text
