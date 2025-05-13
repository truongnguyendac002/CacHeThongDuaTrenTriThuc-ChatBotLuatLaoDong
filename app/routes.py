from flask import Blueprint, jsonify, request, render_template
from app.cbr import CBR
from app.models import Database
import logging

main = Blueprint('main', __name__)
cbr = CBR()
db = Database()
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    """Trang chủ của ứng dụng"""
    return render_template('index.html')

@main.route('/chat')
def chat():
    """Trang chat với chatbot"""
    return render_template('chat.html')

@main.route('/api/dac-diem', methods=['GET'])
def get_dac_diem():
    """API lấy tất cả các đặc điểm"""
    dac_diem_list = db.get_all_dac_diem()
    result = []
    
    for dac_diem in dac_diem_list:
        chi_tiet = db.get_chi_tiet_dac_diem(dac_diem['id'])
        dac_diem['chi_tiet'] = chi_tiet
        result.append(dac_diem)
    
    return jsonify({
        'success': True,
        'data': result
    })

@main.route('/api/truong-hop-tu-van', methods=['GET'])
def get_truong_hop_tu_van():
    """API lấy tất cả các trường hợp tư vấn"""
    truong_hop_list = db.get_all_truong_hop_tu_van()
    
    return jsonify({
        'success': True,
        'data': truong_hop_list
    })

@main.route('/api/tu-van', methods=['POST'])
def tu_van():
    try:
        data = request.get_json()  # Sửa thành get_json() thay vì request.json
        if not data:
            return jsonify({
                'success': False,
                'message': 'Thiếu dữ liệu JSON'
            }), 400

        problem_features = data.get('problem_features', [])
        topic_id = data.get('topic_id', 1)  # Mặc định là 1 nếu không truyền lên

        if not problem_features:
            return jsonify({
                'success': False,
                'message': 'Danh sách đặc điểm trống'
            }), 400

        # Gọi logic CBR
        cbr = CBR()
        result = cbr.get_tu_van(problem_features, topic_id)
        
        return jsonify(result)

    except Exception as e:
        logger.error(f"Lỗi khi xử lý yêu cầu: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Lỗi server: {str(e)}'
        }), 500



@main.route('/api/save-case', methods=['POST'])
def save_case():
    """API lưu một case mới"""
    data = request.json
    problem_features = data.get('problem_features', [])
    truong_hop_tu_van_id = data.get('truong_hop_tu_van_id')
    
    if not problem_features or not truong_hop_tu_van_id:
        return jsonify({
            'success': False,
            'message': 'Thiếu thông tin cần thiết'
        }), 400
    
    case_id = cbr.save_new_case(problem_features, truong_hop_tu_van_id)
    
    return jsonify({
        'success': True,
        'case_id': case_id
    })
