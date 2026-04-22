import streamlit as st
import google.generativeai as genai
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document

# --- 1. 환경 설정 ---
st.set_page_config(page_title="열일이 - 더존 사내 가이드", page_icon="🤖")

# API 키 설정 (Streamlit Secrets 사용)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Secrets에 GOOGLE_API_KEY가 설정되지 않았습니다.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. 지식 추출 함수 정의 ---

# PDF에서 텍스트 추출
def get_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except:
        return ""

# Word(.docx)에서 텍스트 추출
def get_text_from_docx(docx_file):
    try:
        doc = Document(docx_file)
        return "\n".join([para.text for para in doc.paragraphs])
    except:
        return ""

# 구글 시트에서 데이터 추출 (CSV 방식)
def get_text_from_sheet(sheet_id):
    try:
        # 시트 주소에서 추출한 ID를 통해 데이터를 가져옵니다.
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(url)
        knowledge = ""
        for _, row in df.iterrows():
            # 예진님이 만드신 헤더(대분류, 소분류, 상세내용)를 합칩니다.
            knowledge += f"[{row['대분류']} - {row['소분류']}]\n{row['상세내용']}\n\n"
        return knowledge
    except Exception as e:
        return f"시트 로드 실패: {e}"

# --- 3. UI 및 지식 통합 ---

st.title("🤖 우리의 든든한 일꾼, '열일이'")
st.markdown("안녕하세요! 무엇이든지 물어보십쇼.")

# 사이드바 설정
with st.sidebar:
    st.header("📚 지식 데이터 관리")
    
    st.subheader("🔗 구글 시트 연동")
    # 아래 큰따옴표 사이에 예진님의 실제 구글 시트 ID를 넣어주세요!
    # 예: "1AbC2_D3EfG4HiJkLmnOpqrStUvWxyZ"
    target_sheet_id = st.text_input("구글 시트 ID", value="10-vzW1ERnEbukhFBNSjbMPOy_dNbm4qWePv3bGAE-98")
    
    st.subheader("📄 사내 규정 파일 업로드")
    uploaded_files = st.file_uploader("PDF 또는 Word 파일을 선택하세요", type=["pdf", "docx"], accept_multiple_files=True)

# 모든 지식 합치기 (최종 프롬프트용)
total_knowledge = ""

# 1. 시트 지식 합치기
if target_sheet_id and "여기에" not in target_sheet_id:
    total_knowledge += "--- [구글 시트 실무 지식] ---\n"
    total_knowledge += get_text_from_sheet(target_sheet_id)

# 2. 파일 지식 합치기
if uploaded_files:
    total_knowledge += "\n--- [사내 규정 파일 지식] ---\n"
    for file in uploaded_files:
        if file.name.endswith('.pdf'):
            total_knowledge += f"\n<파일명: {file.name}>\n" + get_text_from_pdf(file)
        elif file.name.endswith('.docx'):
            total_knowledge += f"\n<파일명: {file.name}>\n" + get_text_from_docx(file)

# --- 4. 채팅 로직 ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 내용 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("궁금한 점을 물어보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # 최신 모델 사용
            model = genai.GenerativeModel('gemini-3-flash-preview')
            
            # AI에게 주는 최종 지침
            full_prompt = f"""
            당신은 더존비즈온의 사내 가이드 챗봇 '열일이'입니다.
            제공된 [지식 데이터]를 바탕으로 예진 매니저님의 질문에 친절하고 똑똑하게 답변하세요.
            데이터에 기반하여 답변하되, 예진 매니저님이 이해하기 쉽게 설명해주는 것이 중요합니다.

            [지식 데이터]
            {total_knowledge}

            질문: {prompt}
            """
            
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
