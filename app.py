import streamlit as st
import google.generativeai as genai

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

st.set_page_config(page_title="열일이 - 더존 사내 가이드", page_icon="🤖")

st.title("🤖 우리의 든든한 일꾼, '열일이'")
st.markdown("### 안녕하세요 무엇이든 물어보세요.")
st.divider()

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

[셔틀버스 운행 안내]
- 시행일: 2024년 12월 9일부터 / 차량: 펠리세이드 (135무 9588)
- 강촌 출발(13:10) -> 을지 도착(14:30) 
- 을지 출발(15:00) -> 강촌 도착(16:30) 
- 주의: 임직원 탑승 불가. 물품 배송 가능.

[방문객 출입 및 구내식당]
- QR등록: Amaranth 10 확장기능에서 등록.
- 식당 Guest Room: 19F SUGAR, SALT, PEPPER (최대 6명).
- 식당 붐비는 시간: 중식(12:05~12:15), 석식(18:10~18:25).
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # v1beta 에러를 해결하기 위해 경로를 명시적으로 지정했습니다.
            model = genai.GenerativeModel('gemini-3-flash-preview')
            full_prompt = f"너는 사내 가이드 '열일이'야. 아래 지식만으로 답해줘.\n\n지식:\n{KNOWLEDGE_BASE}\n\n질문: {prompt}"
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
