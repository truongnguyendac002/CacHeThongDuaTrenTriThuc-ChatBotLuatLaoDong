document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    
    // State variables
    let currentStep = 'initial';
    let selectedTopic = null;

    let userResponses = {};
    let problemFeatures = [];
    let allDacDiem = [];
    let currentQuestionsFlow = [];
    
    let currentQuestionIndex = 0;

    // Add event listeners
    if (sendBtn && userInput) {
        sendBtn.addEventListener('click', handleUserInput);
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleUserInput();
            }
        });
        
        // Fetch đặc điểm when chat page loads
        fetchDacDiem();
    }
    
    function handleUserInput() {
        const message = userInput.value.trim();
        if (message === '') return;
        
        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input
        userInput.value = '';
        
        // Process message based on current step
        processUserInput(message);
    }
    
    function processUserInput(message) {
        if (currentStep === 'initial') {
            // User selects topic
            const topic = parseInt(message);
            if (topic >= 1 && topic <= 3) {
                selectedTopic = topic;
                currentStep = 'asking_questions';
                
                // Set up questions based on selected topic
                setupQuestionsFlow(topic);
                
                // Ask first question
                askNextQuestion();
            } else {
                addMessage('Vui lòng chọn một trong các chủ đề (nhập số 1, 2 hoặc 3):', 'bot');
            }
        } else if (currentStep === 'asking_questions') {
            // Save user's answer
            const questionObj = currentQuestionsFlow[currentQuestionIndex - 1];
            
            // Validate input
            const validOptions = questionObj.options.map(opt => opt.value);
            if (!validOptions.includes(message)) {
                addMessage(`Vui lòng chọn một trong các lựa chọn sau: ${validOptions.join(', ')}`, 'bot');
                return;
            }
            
            // Save user response
            userResponses[questionObj.dacDiemId] = message;
            
            problemFeatures.push({
                dac_diem_id: questionObj.dacDiemId,
                gia_tri: message
            });

            if (currentQuestionIndex < currentQuestionsFlow.length) {
                askNextQuestion();
            } else {
                currentStep = 'showing_result';
                getTuVan();
            }

        } else if (currentStep === 'showing_result') {
            // Reset conversation
            resetConversation();
            addMessage('Bạn có thể bắt đầu một cuộc tư vấn mới.  Bạn muốn được tư vấn về vấn đề nào? (Nhập số 1 - Tư vấn về hợp đồng lao động, 2 - Tư vấn về thay đổi mức lương, lương làm thêm giờ và phụ cấp hoặc 3 - Tư vấn về bảo hiểm)', 'bot');
        }
    }
    
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.innerHTML = message;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function setupQuestionsFlow(topic) {
        currentQuestionsFlow = [];
    
        if (topic === 1) {
            // Tư vấn về hợp đồng lao động
            currentQuestionsFlow = [
                {
                    question: 'Bạn đang làm việc theo loại hợp đồng nào?',
                    dacDiemId: 1,
                    options: [
                        { text: 'Hợp đồng thử việc', value: 'hop_dong_thu_viec' },
                        { text: 'Hợp đồng chính thức (có thời hạn hoặc không thời hạn)', value: 'hop_dong_chinh_thuc' }
                    ]
                },
                {
                    question: 'Tình trạng hợp đồng hiện tại của bạn là gì?',
                    dacDiemId: 2,
                    options: [
                        { text: 'Chưa ký hợp đồng', value: 'chua_ky' },
                        { text: 'Đã ký hợp đồng', value: 'da_ky' }
                    ]
                },
                {
                    question: 'Bạn có đang muốn nghỉ việc không?',
                    dacDiemId: 3,
                    options: [
                        { text: 'Có', value: 'co' },
                        { text: 'Không', value: 'khong' }
                    ]
                },
                {
                    question: 'Tình trạng sức khỏe của bạn hiện tại như thế nào?',
                    dacDiemId: 10,
                    options: [
                        { text: 'Bình thường, không có vấn đề sức khỏe', value: 'tot' },
                        { text: 'Không tốt, có vấn đề sức khỏe hoặc tai nạn lao động', value: 'khong_tot' }
                    ]
                },
                {
                    question: 'Bạn đã nhận đủ tiền lương cho công việc đã làm chưa?',
                    dacDiemId: 9,
                    options: [
                        { text: 'Chưa nhận đủ lương', value: 'chua_nhan' },
                        { text: 'Đã nhận đủ lương', value: 'da_nhan' }
                    ]
                },
                {
                    question: 'Bạn có bị ngược đãi, quấy rối hoặc phân biệt đối xử tại nơi làm việc không?',
                    dacDiemId: 11,
                    options: [
                        { text: 'Có', value: 'co' },
                        { text: 'Không', value: 'khong' }
                    ]
                },
                {
                    question: 'Bạn đã đóng bảo hiểm xã hội tại công ty được bao lâu?',
                    dacDiemId: 7,
                    options: [
                        { text: 'Dưới 12 tháng', value: 'duoi_12_thang' },
                        { text: 'Từ 12 tháng trở lên', value: 'tu_12_thang_tro_len' }
                    ]
                }
            ];
        } else if (topic === 2) {
            // Tư vấn về thay đổi mức lương, lương làm thêm giờ và phụ cấp
            currentQuestionsFlow = [
                {
                    question: 'Bạn đang làm việc theo loại hợp đồng nào?',
                    dacDiemId: 1,
                    options: [
                        { text: 'Hợp đồng thử việc', value: 'hop_dong_thu_viec' },
                        { text: 'Hợp đồng chính thức (có thời hạn hoặc không thời hạn)', value: 'hop_dong_chinh_thuc' }
                    ]
                },
                {
                    question: 'Gần đây mức lương cơ bản của bạn có bị thay đổi không? (Tăng, giảm, hoặc điều chỉnh bởi công ty)',
                    dacDiemId: 4,
                    options: [
                        { text: 'Có thay đổi', value: 'co' },
                        { text: 'Không thay đổi', value: 'khong' }
                    ]
                },
                {
                    question: 'Hiện tại bạn còn làm việc tại công ty không?',
                    dacDiemId: 3,
                    options: [
                        { text: 'Đã nghỉ việc', value: 'khong_lam_viec' },
                        { text: 'Đang làm việc', value: 'dang_lam_viec' }
                    ]
                },
                {
                    question: 'Bạn làm việc theo hình thức nào?',
                    dacDiemId: 6,
                    options: [
                        { text: 'Chỉ làm giờ hành chính (không tăng ca)', value: 'chi_lam_gio_hanh_chinh' },
                        { text: 'Có làm thêm giờ (tăng ca, làm thêm ngày nghỉ/lễ)', value: 'co_lam_them_gio' }
                    ]
                },
                {
                    question: 'Bạn có nghỉ phép vượt quá số ngày quy định của công ty không?',
                    dacDiemId: 5,
                    options: [
                        { text: 'Không nghỉ quá phép', value: 'nghi_du_phep' },
                        { text: 'Có nghỉ quá phép', value: 'nghi_qua_phep' }
                    ]
                },
                {
                    question: 'Bạn đã đóng bảo hiểm xã hội tại công ty được bao lâu?',
                    dacDiemId: 7,
                    options: [
                        { text: 'Dưới 12 tháng', value: 'duoi_12_thang' },
                        { text: 'Từ 12 tháng trở lên', value: 'tu_12_thang_tro_len' }
                    ]
                }
            ];
        } else if (topic === 3) {
            // Tư vấn về bảo hiểm
            currentQuestionsFlow = [
                {
                    question: 'Bạn đang làm việc theo loại hợp đồng nào?',
                    dacDiemId: 1,
                    options: [
                        { text: 'Hợp đồng thử việc', value: 'hop_dong_thu_viec' },
                        { text: 'Hợp đồng chính thức (có thời hạn hoặc không thời hạn)', value: 'hop_dong_chinh_thuc' }
                    ]
                },
                {
                    question: 'Tình trạng hợp đồng hiện tại của bạn là gì?',
                    dacDiemId: 2,
                    options: [
                        { text: 'Chưa ký hợp đồng', value: 'chua_ky' },
                        { text: 'Đã ký hợp đồng', value: 'da_ky' }
                    ]
                },
                {
                    question: 'Hiện tại bạn còn làm việc tại công ty không?',
                    dacDiemId: 3,
                    options: [
                        { text: 'Đã nghỉ việc', value: 'khong_lam_viec' },
                        { text: 'Đang làm việc', value: 'dang_lam_viec' }
                    ]
                },
                {
                    question: 'Bạn có đang mang thai hoặc trong thời gian nghỉ thai sản không?',
                    dacDiemId: 8,
                    options: [
                        { text: 'Không mang thai', value: 'khong_mang_thai' },
                        { text: 'Đang mang thai hoặc nghỉ thai sản', value: 'dang_mang_thai' }
                    ]
                },
                {
                    question: 'Tình trạng sức khỏe của bạn hiện tại như thế nào?',
                    dacDiemId: 10,
                    options: [
                        { text: 'Bình thường, không có vấn đề sức khỏe', value: 'tot' },
                        { text: 'Không tốt, có vấn đề sức khỏe hoặc tai nạn lao động', value: 'khong_tot' }
                    ]
                },
                {
                    question: 'Bạn đã đóng bảo hiểm xã hội tại công ty được bao lâu?',
                    dacDiemId: 7,
                    options: [
                        { text: 'Dưới 12 tháng', value: 'duoi_12_thang' },
                        { text: 'Từ 12 tháng trở lên', value: 'tu_12_thang_tro_len' }
                    ]
                }
            ];
        }
    
        currentQuestionIndex = 0;
    }
    
    
    function askNextQuestion() {
        if (currentQuestionIndex < currentQuestionsFlow.length) {
            const question = currentQuestionsFlow[currentQuestionIndex];
            let messageText = question.question + '<br>';
            question.options.forEach((option, index) => {
                messageText += `${index + 1}: ${option.text} (Nhập "${option.value}")<br>`;
            });
            addMessage(messageText, 'bot');
            currentQuestionIndex++; // Tăng index sau khi hiển thị câu hỏi
        }
    }
    
    async function getTuVan() {
        addMessage('Đang xử lý thông tin của bạn...', 'bot');
        
        try {
            const response = await fetch('/api/tu-van', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    problem_features: problemFeatures,
                    topic_id: selectedTopic // selectedTopic là số 1, 2, 3
                })
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `Lỗi HTTP: ${response.status}`);
            }
    
            const data = await response.json();
            
            if (data.success) {
                const similarity = Math.round(data.similarity * 100);
                
                let messageText = `<strong>Kết quả tư vấn (Độ tương đồng: ${similarity}%)</strong><br><br>`;
                messageText += `<strong>Trường hợp: ${data.truong_hop.ten_truong_hop}</strong><br><br>`;

                const source = data.source || 'database'; // hoặc 'gemini' nếu bạn dùng Gemini
                if (source === 'chatgpt') {
                    messageText += '<em>(Tư vấn được tạo bởi AI dựa trên thông tin bạn cung cấp)</em><br><br>';
                }
                messageText += data.noi_dung_tu_van.replace(/\n/g, '<br>');
                messageText += '<br><br>Bạn có thể nhắn tin để bắt đầu cuộc tư vấn mới.';

                addMessage(messageText, 'bot');
            } else {
                addMessage('Không thể tạo tư vấn: ' + data.message, 'bot');
                // addMessage('Không tìm thấy trường hợp tương đồng. Vui lòng cung cấp thêm thông tin hoặc liên hệ với chuyên gia tư vấn.', 'bot');
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('Đã xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau: \n' +error, 'bot');
        }
    }
    
    async function fetchDacDiem() {
        try {
            const response = await fetch('/api/dac-diem');
            const data = await response.json();
            
            if (data.success) {
                allDacDiem = data.data;
            }
        } catch (error) {
            console.error('Error fetching dac diem:', error);
        }
    }
    
    function resetConversation() {
        currentStep = 'initial';
        selectedTopic = null;
        currentQuestion = 0;
        userResponses = {};
        problemFeatures = [];
        currentQuestionsFlow = [];
    }
});
