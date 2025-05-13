import mysql.connector
from app.config import Config

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        self.cursor = self.conn.cursor(dictionary=True)
    
    def __del__(self):
        self.conn.close()
    
    def get_all_dac_diem(self):
        """Lấy tất cả các đặc điểm của người lao động"""
        query = "SELECT * FROM dac_diem"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_chi_tiet_dac_diem(self, dac_diem_id):
        """Lấy chi tiết của một đặc điểm"""
        query = "SELECT * FROM chi_tiet_dac_diem WHERE dac_diem_id = %s"
        self.cursor.execute(query, (dac_diem_id,))
        return self.cursor.fetchall()
    
    def get_all_truong_hop_tu_van(self):
        """Lấy tất cả các trường hợp tư vấn"""
        query = "SELECT * FROM truong_hop_tu_van"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_truong_hop_tu_van_by_id(self, id):
        """Lấy thông tin về một trường hợp tư vấn cụ thể"""
        query = "SELECT * FROM truong_hop_tu_van WHERE id = %s"
        self.cursor.execute(query, (id,))
        return self.cursor.fetchone()
    
    def get_do_tuong_dong(self, dac_diem_id, gia_tri_1, gia_tri_2):
        """Lấy độ tương đồng giữa hai giá trị đặc điểm"""
        query = """
        SELECT muc_do_tuong_dong FROM do_tuong_dong 
        WHERE dac_diem_id = %s AND gia_tri_1 = %s AND gia_tri_2 = %s
        """
        self.cursor.execute(query, (dac_diem_id, gia_tri_1, gia_tri_2))
        result = self.cursor.fetchone()
        if result:
            return result['muc_do_tuong_dong']
        return 0.0
    
    def get_cases(self):
        """Lấy tất cả các case trong hệ thống"""
        query = "SELECT * FROM cases"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_case_details(self, case_id):
        """Lấy chi tiết về một case cụ thể"""
        query = """
        SELECT ccd.dac_diem_id, d.ten_dac_diem, ccd.gia_tri 
        FROM case_chi_tiet ccd
        JOIN dac_diem d ON ccd.dac_diem_id = d.id
        WHERE ccd.case_id = %s
        """
        self.cursor.execute(query, (case_id,))
        return self.cursor.fetchall()
    
    def get_trong_so(self, truong_hop_tu_van_id, dac_diem_id):
        """Lấy trọng số của một đặc điểm đối với một trường hợp tư vấn"""
        query = """
        SELECT trong_so FROM trong_so 
        WHERE truong_hop_tu_van_id = %s AND dac_diem_id = %s
        """
        self.cursor.execute(query, (truong_hop_tu_van_id, dac_diem_id))
        result = self.cursor.fetchone()
        if result:
            return result['trong_so']
        return 0.0
    
    def get_case_by_id(self, case_id):
        """Lấy thông tin của một case cụ thể"""
        query = "SELECT * FROM cases WHERE id = %s"
        self.cursor.execute(query, (case_id,))
        return self.cursor.fetchone()
    
    def save_case(self, truong_hop_tu_van_id, dac_diem_data):
        """Lưu một case mới vào database"""
        # Thêm case mới
        query = "INSERT INTO cases (truong_hop_tu_van_id) VALUES (%s)"
        self.cursor.execute(query, (truong_hop_tu_van_id,))
        self.conn.commit()
        case_id = self.cursor.lastrowid
        
        # Thêm chi tiết của case
        for dac_diem_id, gia_tri in dac_diem_data.items():
            query = """
            INSERT INTO case_chi_tiet (case_id, dac_diem_id, gia_tri) 
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (case_id, dac_diem_id, gia_tri))
        
        self.conn.commit()
        return case_id
    # Thêm các phương thức mới vào lớp Database

    def save_chatgpt_consultation(self, topic_id, noi_dung_tu_van, ten_truong_hop):
        """Lưu tư vấn do ChatGPT tạo vào bảng truong_hop_tu_van"""
        query = """
        INSERT INTO truong_hop_tu_van (ten_truong_hop, noi_dung_tu_van, tao_boi_chatgpt) 
        VALUES (%s, %s, TRUE)
        """
        self.cursor.execute(query, (ten_truong_hop, noi_dung_tu_van))
        self.conn.commit()
        return self.cursor.lastrowid

    def save_case_with_chatgpt_advice(self, truong_hop_tu_van_id, problem_features):
        """Lưu case với tư vấn từ ChatGPT"""
        # Thêm case mới
        query = "INSERT INTO cases (truong_hop_tu_van_id) VALUES (%s)"
        self.cursor.execute(query, (truong_hop_tu_van_id,))
        self.conn.commit()
        case_id = self.cursor.lastrowid
        
        # Thêm chi tiết case
        for feature in problem_features:
            query = """
            INSERT INTO case_chi_tiet (case_id, dac_diem_id, gia_tri) 
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (case_id, feature['dac_diem_id'], feature['gia_tri']))
        
        self.conn.commit()
        return case_id

    def save_consultation_history(self, topic_id, truong_hop_tu_van_id, do_tuong_dong):
        """Lưu lịch sử tư vấn"""
        query = """
        INSERT INTO lich_su_tu_van (topic_id, truong_hop_tu_van_id, do_tuong_dong)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(query, (topic_id, truong_hop_tu_van_id, do_tuong_dong))
        self.conn.commit()
        return self.cursor.lastrowid

        
