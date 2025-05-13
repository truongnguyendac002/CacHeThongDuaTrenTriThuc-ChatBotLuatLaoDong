from app.models import Database
from app.config import Config
from app.gemini_service import GeminiService
import json

class CBR:
    def __init__(self):
        self.db = Database()
        self.gemini = GeminiService() 

    
    def tinh_do_tuong_dong(self, problem_case, stored_case):
        """Tính độ tương đồng giữa trường hợp mới và trường hợp đã lưu"""
        case_id = stored_case['id']
        truong_hop_tu_van_id = stored_case['truong_hop_tu_van_id']
        
        # Lấy chi tiết của case đã lưu
        case_details = self.db.get_case_details(case_id)
        
        # Chuyển đổi case_details thành dictionary
        case_data = {}
        for detail in case_details:
            case_data[detail['dac_diem_id']] = detail['gia_tri']
        
        tong_trong_so = 0
        tong_do_tuong_dong_co_trong_so = 0
        
        # Tính độ tương đồng cho từng đặc điểm
        for dac_diem_id, gia_tri_problem in problem_case.items():
            # Lấy trọng số của đặc điểm đối với trường hợp tư vấn
            trong_so = self.db.get_trong_so(truong_hop_tu_van_id, dac_diem_id)
            
            if trong_so > 0 and dac_diem_id in case_data:
                gia_tri_case = case_data[dac_diem_id]
                # Lấy độ tương đồng giữa hai giá trị
                do_tuong_dong = self.db.get_do_tuong_dong(dac_diem_id, gia_tri_problem, gia_tri_case)
                
                tong_do_tuong_dong_co_trong_so += do_tuong_dong * trong_so
                tong_trong_so += trong_so
        
        # Tính độ tương đồng trung bình có trọng số
        if tong_trong_so > 0:
            do_tuong_dong_trung_binh = tong_do_tuong_dong_co_trong_so / tong_trong_so
        else:
            do_tuong_dong_trung_binh = 0
        
        return do_tuong_dong_trung_binh
    
    def tim_case_tuong_dong_nhat(self, problem_case, topic_id):
        topic_map = {
            1: [1,2,3,4,5,6,7],      # Hợp đồng lao động
            2: [8,9,10],             # Lương, thưởng, phụ cấp
            3: [11,12,13,14]         # Bảo hiểm
        }
        allowed_ids = topic_map.get(topic_id, [])

        """Tìm case tương đồng nhất với trường hợp mới"""
        cases = [case for case in self.db.get_cases() if case['truong_hop_tu_van_id'] in allowed_ids]
        max_similarity = 0
        most_similar_case = None
        
        for case in cases:
            similarity = self.tinh_do_tuong_dong(problem_case, case)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_case = case
        
        # Nếu độ tương đồng vượt ngưỡng, trả về case tương đồng nhất
        if max_similarity >= Config.SIMILARITY_THRESHOLD and most_similar_case:
            truong_hop = self.db.get_truong_hop_tu_van_by_id(most_similar_case['truong_hop_tu_van_id'])
            return {
                'case': most_similar_case,
                'similarity': max_similarity,
                'truong_hop': truong_hop
            }
        
        return None
    
    def get_tu_van(self, problem_features, topic_id):
        """Lấy tư vấn cho trường hợp mới"""
        # Chuyển đổi problem_features thành dictionary theo dạng {dac_diem_id: gia_tri}
        problem_case = {}
        for feature in problem_features:
            problem_case[feature['dac_diem_id']] = feature['gia_tri']
        
        # Tìm case tương đồng nhất
        result = self.tim_case_tuong_dong_nhat(problem_case, topic_id)
        
        if result:
            similarity = result['similarity']
            self.db.save_consultation_history(topic_id, result['truong_hop']['id'], similarity)
            if similarity < Config.GEMINI_THRESHOLD:
                return self.get_chatgpt_consultation(problem_features, topic_id)
            
            return {
                'success': True,
                'similarity': result['similarity'],
                'truong_hop': result['truong_hop'],
                'noi_dung_tu_van': result['truong_hop']['noi_dung_tu_van']
            }
        else:
            return self.get_chatgpt_consultation(problem_features, topic_id)
        
        # return {
        #     'success': False,
        #     'message': 'Không tìm thấy trường hợp tương đồng'
        # }
    def get_chatgpt_consultation(self, problem_features, topic_id):
        """Lấy và lưu tư vấn từ ChatGPT"""
        try:
            # Lấy tư vấn từ ChatGPT
            noi_dung_tu_van = self.gemini.get_consultation(problem_features, topic_id)
            
            # Tạo tên trường hợp dựa trên topic_id
            topic_map = {
                1: "Tư vấn hợp đồng lao động",
                2: "Tư vấn về lương và phụ cấp",
                3: "Tư vấn về bảo hiểm"
            }
            ten_truong_hop = topic_map.get(topic_id, "Tư vấn luật lao động") 
            
            # Lưu tư vấn vào database
            truong_hop_tu_van_id = self.db.save_chatgpt_consultation(topic_id, noi_dung_tu_van, ten_truong_hop)
            
            # Lưu case với các đặc điểm và tư vấn từ ChatGPT
            self.db.save_case_with_chatgpt_advice(truong_hop_tu_van_id, problem_features)
            
            # Lấy thông tin trường hợp tư vấn vừa lưu
            truong_hop = self.db.get_truong_hop_tu_van_by_id(truong_hop_tu_van_id)
            
            return {
                'success': True,
                'similarity': 1.0,  # Độ tương đồng tối đa vì đây là case mới tạo
                'truong_hop': truong_hop,
                'noi_dung_tu_van': noi_dung_tu_van,
                'source': 'chatgpt'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Lỗi khi tạo tư vấn từ ChatGPT: {str(e)}'
            }

    
    def save_new_case(self, problem_features, truong_hop_tu_van_id):
        """Lưu trường hợp mới vào database"""
        # Chuyển đổi problem_features thành dictionary theo dạng {dac_diem_id: gia_tri}
        problem_case = {}
        for feature in problem_features:
            problem_case[feature['dac_diem_id']] = feature['gia_tri']
        
        # Lưu case mới
        case_id = self.db.save_case(truong_hop_tu_van_id, problem_case)
        
        return case_id
