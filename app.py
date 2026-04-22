import streamlit as st
import google.generativeai as genai

# 1. API 키 설정
GOOGLE_API_KEY = "AIzaSyAap3o5GkNo6NRvHkDWOo_P2K_Hpc5O_wQ"
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="열일이 - 더존 사내 가이드", page_icon="🤖")

# 화면 레이아웃 꾸미기
st.title("🤖 더존의 든든한 일꾼, '열일이'")
st.markdown("### 안녕하세요 사내 운영에 대해 무엇이든 물어보세요.")
st.divider()

# 2. 예진님이 주신 상세 데이터를 몽땅 넣은 지식 베이스
KNOWLEDGE_BASE = """
[ATEC(11F) 세미나룸 안내]
- 용도: 대외 행사, 세미나, 고객 교육 및 미팅 공간. (내부 회의용 이용 일절 금지)
- 운영시간: 평일 09:00 ~ 18:00 (주말 및 공휴일 휴무)
- 예약방법: Amaranth 10 -> 자원 선택 -> ATEC 선택 -> 자원 예약 버튼 -> 담당자(김나연A 대리, 내선 4114) 승인 후 확정.
- 회의실 규모: 
  * 아인슈타인/에디슨: 12명 (삼성 플립 설치)
  * 데카콘: 17명 (와이드스크린, 컨트롤박스 필요)
  * 노벨/뉴턴: 16명 (와이드스크린+플립)
  * 갈릴레오: 18명 (와이드스크린, 일자형 구조)
  * 다빈치: 54명 (대형 행사용, 컨트롤박스 필요)
- 주의사항: 예약 시간 20분 경과 시 자동 취소. 리허설은 2시간 이내 제한. 퇴실 시 정리정돈 필수.

[셔틀버스 운행 안내 (을지타워 ↔ 강촌캠퍼스)]
- 시행일: 2024년 12월 9일부터
- 차량: 펠리세이드 (135무 9588)
- 시간표: 
  * 강촌 출발(13:10) -> 을지 도착(14:30) (강촌 베이커리 앞 대기)
  * 을지 출발(15:00) -> 강촌 도착(16:30) (을지 청계광장 앞 대기)
- 주의: 임직원 탑승 불가. 물품 배송 가능(발신자가 수신자에게 안내 필수).

[방문객 출입 방법 안내]
- 출입 구분: 
  * 사전 QR등록자: 직원 동행/신분증 보관 불필요.
  * 사전 미등록자: 1층 안내데스크 확인 및 직원 동행 필수, 신분증/명함 보관.
- 업무협조전 작성: 결재(상신자-Unit장), 합의(임희란 대리, 임태희 대리, 배윤화 과장, 명종현 차장, 오인환 부장). *ATEC 출입 시 김나연A 대리 합의 포함 필수.
- QR등록: Amaranth 10 확장기능 -> 방문객 등록 -> 종료시간 정확히 기입 -> 저장 시 알림톡 전송.

[구내식당 Guest Room (19F) 이용 안내]
- 장소: SUGAR, SALT, PEPPER 룸 (최대 6명, 홀딩도어 개방 시 확대 가능)
- 이용시간: 중식(11:30~13:00), 석식(17:00~20:00)
- 메뉴 구분: 
  * 일반배식: 중식 9,000원 (10명 이상은 3일 전 예약 필수)
  * 상차림: 일반 14,000원 / 중급 33,000원 (최소 4일 전 예약 필수)
- 붐비는 시간: 조식(08:20~08:30), 중식(12:05~12:15), 석식(18:10~18:25)
- 주의사항: 예약 인원보다 적게 먹어도 예약 인원만큼 정산됨. 정확한 인원 예약 필수.
- 담당: 임희란 대리(내선 2513), CJ프레시웨이 점장(02-3789-0941).
"""

# 대화 시스템 설정
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("예: 셔틀버스 시간 알려줘, 회의실 예약 어떻게 해?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # AI 모델 호출 (최신 flash 모델 사용)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 시스템 프롬프트: 열일이의 성격과 지식 주입
        system_instruction = f"""
        너는 더존의 사내 가이드 챗봇 '열일이'야. 
        사용자는 더존 임직원들이야. 아래 [사내 지식]에 있는 내용만을 바탕으로 답변해줘. 
        [사내 지식]에 없는 내용은 함부로 지어내지 말고, 담당자에게 문의하라고 친절하게 안내해.
        답변은 가독성 좋게 불렛포인트나 번호를 써서 정리해줘.

        [사내 지식]
        {KNOWLEDGE_BASE}
        """
        
        response = model.generate_content(system_instruction + "\n\n사용자 질문: " + prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
