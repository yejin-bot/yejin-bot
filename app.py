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

# [중요] 구글 시트 ID를 여기에 고정합니다 (예진님의 시트 ID로 교체하세요)
FIXED_SHEET_ID = "10-vzW1ERnEbukhFBNSjbMPOy_dNbm4qWePv3bGAE-98"

# --- 2. 지식 추출 함수 정의 ---

def get_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        return "".join([page.extract_text() for page in reader.pages])
    except: return ""

def get_text_from_docx(docx_file):
    try:
        doc = Document(docx_file)
        return "\n".join([para.text for para in doc.paragraphs])
    except: return ""

def get_text_from_sheet(sheet_id):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        df = pd.read_csv(url)
        knowledge = ""
        for _, row in df.iterrows():
            knowledge += f"[{row['대분류']} - {row['소분류']}]\n{row['상세내용']}\n\n"
        return knowledge
    except: return "시트 지식을 불러올 수 없습니다. ID와 공유 설정을 확인해주세요."

# --- 3. UI 및 지식 통합 ---

# 메인 타이틀 및 인사말
st.title("🤖 우리의 든든한 일꾼, '열일이'")
st.info(f"""
**안녕하세요! 저는 열일이입니다.** 모든 답변은 '열일이 지식베이스'를 기반으로 생성되며, 추가로 학습시키고 싶은 정보가 있다면  
좌측에 파일을 업로드해 주세요. 열일이가 최적의 답변을 제안해 드릴게요!
""")

# 사이드바 설정 (디테일 수정)
with st.sidebar:
    st.header("📄 지식베이스")
    st.write("---")
    
    # 구글 시트는 백그라운드에서 자동 연동됨
    st.success("✅ 구글 시트 실무 지식 연동 완료")
    
    # 파일 업로드 (UI 문구 수정)
    st.subheader("📁 로컬 파일 업로드")
    uploaded_files = st.file_uploader(
        "추가 정보를 학습시키려면 PDF 또는 Word 파일을 선택하세요.", 
        type=["pdf", "docx"], 
        accept_multiple_files=True
    )

# 모든 지식 합치기
total_knowledge = ""
total_knowledge += "--- [기본 지식베이스(구글 시트)] ---\n" + get_text_from_sheet(FIXED_SHEET_ID)

if uploaded_files:
    total_knowledge += "\n--- [추가 학습 데이터(사용자 업로드)] ---\n"
    for file in uploaded_files:
        if file.name.endswith('.pdf'):
            total_knowledge += f"\n<파일명: {file.name}>\n" + get_text_from_pdf(file)
        elif file.name.endswith('.docx'):
            total_knowledge += f"\n<파일명: {file.name}>\n" + get_text_from_docx(file)

# --- 4. 채팅 로직 ---

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("원하는 내용을 입력하거나 파일을 업로드하여 답변에 활용하세요."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('열일이가 지식베이스를 기반으로 답변을 생성하고 있습니다...'):
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
            
                full_prompt = f"""
                당신은 더존비즈온의 전문적인 사내 가이드 챗봇 '열일이'입니다.
                제공된 [지식 데이터]를 바탕으로 선생님께 신뢰감 있고 친절하게 답변하세요.

                [지식 데이터]
                {total_knowledge}

                질문: {prompt}
                """
            
                response = model.generate_content(full_prompt)
                # [질문 기록 추가] 이 코드가 질문 내용을 대시보드 뒷단에 기록합니다.
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[LOG] {now} | 질문 내용: {prompt}")
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
