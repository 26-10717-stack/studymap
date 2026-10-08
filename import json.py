import re
import urllib.parse
import requests
import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="개념 단권화: 심화 이론 & 문제집 실전 문제/풀이",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 [실전 문제집 스타일] 개념 심화 & 정답 풀이 단권화기")
st.caption(
    "알맹이 없는 껍데기 문구는 일절 출력하지 않습니다. 사용자가 입력한 어떤 개념이든 **[1. 핵심 요약] ➔ [2. 전공 심화 반응식/공식] ➔ [3. 진짜 문제집 실전 문제 1개] ➔ [4. 단계별 정답 풀이]**를 생성합니다."
)

st.markdown("---")

# 사이드바: 더 안정적인 AI 생성을 위한 API 키 입력 (선택 사항)
st.sidebar.header("⚙️ 설정")
user_gemini_key = st.sidebar.text_input(
    "Gemini API Key (선택)",
    type="password",
    help="키를 넣으시면 서버 지연 없이 100% 빠른 속도로 고품질 문제가 생성됩니다. 없으면 무료 백엔드로 작동합니다.",
)

# 1단계: 사용자 입력 영역 (고정된 예시 없는 빈 칸)
st.subheader("1️⃣ 공부한 개념 입력")

col1, col2 = st.columns([1, 1])

with col1:
    main_concept = st.text_input(
        "📍 [중심 개념]",
        placeholder="어떤 학문이든 작성 가능 (예: 광합성, 산화 환원, 피타고라스 정리, 미분, 오옴의 법칙 등)",
    )

with col2:
    basic_def = st.text_area(
        "📝 [내가 이해한 기본 정의 / 핵심 공식]",
        placeholder="오늘 공부한 기본적인 정의나 기억나는 핵심 내용을 작성하세요.",
        height=100,
    )

generate_btn = st.button(
    "🚀 실전 문제집 문제 & 정답 풀이 생성하기",
    type="primary",
    use_container_width=True,
)


# 프롬프트: 깡통 템플릿 문구 절대 금지 및 진짜 문제/풀이 강제
def build_prompt(concept, definition):
    return f"""
[사용자 입력 정보]
- 중심 개념: {concept}
- 작성한 기본 정의/메모: {definition}

[엄격한 작성 지침 - 위반 시 감점]
너는 대한민국 최고의 수능/전공 출제위원이자 튜터다.
"~의 학문적 체계", "~의 심화 해석" 같은 껍데기 템플릿 문구나 추상적인 개요글은 단 한 줄도 쓰지 마라!
사용자가 적은 입력값을 앵무새처럼 그대로 복사해서 되풀이하는 짓도 절대 하지 마라!

반드시 사용자가 입력한 [{concept}] 주제 하나에만 집중하여 아래 4가지를 진짜 알맹이 지식으로 작성해라:

1. [0. 사용자 작성 내용 핵심 요약]:
   - 입력한 정의를 명확하게 정리.

2. [1. 전공 수준 심화 이론 & 세부 메커니즘/공식]:
   - 화학/생명: 구체적 화학 반응식(예: 6CO2 + 6H2O -> C6H12O6 + 6O2), 명반응/암반응, 틸라코이드/스트로마 등 세부 메커니즘 서술
   - 수학/물리: LaTeX 수식, 관련 법칙 및 변형 공식 서술
   - 인문/사회: 핵심 구조 및 학술적 개념 정리

3. [2. 📘 대표 문제집/시험지 스타일 실전 문제 1개]:
   - 실제로 문제집이나 수능/내신 시험지에 출제되는 완벽한 지문 형태의 문제 1개 출제.
   - 구체적 숫자, 보기 조건, 실험 상황, 반응식 등이 완성되어 포함된 진짜 문제를 출제할 것.

4. [3. ⚡ 단계별 상세 정답 풀이 & 최종 정답]:
   - Step 1 (문제 조건 및 적용 공식/원리) -> Step 2 (상세 계산 및 논리 풀이 과정) -> Step 3 (최종 정답 및 주의할 점) 작성.

출력 형식 (반드시 아래 두 구분자를 엄격히 사용해라):
===GRAPHVIZ===
digraph Mindmap {{
    rankdir=LR;
    node [fontname="Malgun Gothic, sans-serif", shape=box, style="filled,rounded", color="#2B3A42", fillcolor="#E8F1F5", fontsize=11];
    edge [color="#3F51B5", arrowhead=vee];
    // [{concept}] -> [0. 요약] -> [1. 세부 메커니즘/공식] -> [2. 실전 문제] -> [3. 정답 풀이] 구조로 연결된 Graphviz 코드 작성 (라벨에 구체적 내용 포함)
}}
===MARKDOWN===
(0. 핵심 요약 / 1. 전공 심화 이론 & 반응식/공식 / 2. 📘 대표 문제집 실전 문제 / 3. ⚡ 단계별 상세 정답 풀이)
"""


# AI 호출 함수 (Gemini API 우선, 실패 시 오픈 백엔드 연결)
def call_ai_engine(concept, definition, api_key):
    prompt_text = build_prompt(concept, definition)

    # 1. 사용자가 Gemini 키를 입력한 경우 (가장 빠르고 정확함)
    if api_key:
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            res = model.generate_content(prompt_text)
            if res and res.text:
                return res.text
        except Exception as e:
            st.error(f"Gemini API 호출 중 오류가 발생했습니다: {e}")

    # 2. 키가 없을 경우 무료 AI 백엔드 연결
    url = "https://text.pollinations.ai/"
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are an expert exam maker. You strictly output real exam questions with exact numbers, chemical equations, and step-by-step solutions without any placeholder text.",
            },
            {"role": "user", "content": prompt_text},
        ],
        "model": "openai",
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200 and len(response.text.strip()) > 100:
            return response.text
    except Exception:
        pass

    try:
        encoded_prompt = urllib.parse.quote(prompt_text)
        get_url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai"
        response = requests.get(get_url, timeout=30)
        if response.status_code == 200 and len(response.text.strip()) > 100:
            return response.text
    except Exception:
        pass

    return None


# 2단계: 결과 처리 및 화면 출력
if generate_btn:
    if not main_concept.strip() or not basic_def.strip():
        st.warning(
            "⚠️ [중심 개념]과 [내가 이해한 기본 정의 / 핵심 공식]을 입력해 주세요!"
        )
    else:
        st.markdown("---")
        st.subheader(
            f"2️⃣ '{main_concept}' 전공 심화 & 문제집 실전 문제/풀이 결과"
        )

        with st.spinner(
            f"'{main_concept}' 관련 세부 메커니즘, 실전 문제 및 정답 풀이를 생성 중입니다..."
        ):
            raw_output = call_ai_engine(
                main_concept, basic_def, user_gemini_key
            )

            if raw_output:
                dot_match = re.search(
                    r"===GRAPHVIZ===\s*(.*?)\s*===MARKDOWN===",
                    raw_output,
                    re.DOTALL,
                )
                md_match = re.search(
                    r"===MARKDOWN===\s*(.*)", raw_output, re.DOTALL
                )

                if dot_match and md_match:
                    dot_code = dot_match.group(1).strip()
                    dot_code = re.sub(r"```dot|```graphviz|```", "", dot_code)
                    markdown_text = md_match.group(1).strip()

                    col_res1, col_res2 = st.columns([1, 1])
                    with col_res1:
                        st.subheader(
                            "📌 [개념 ➔ 심화메커니즘 ➔ 문제 ➔ 풀이] 마인드맵"
                        )
                        try:
                            st.graphviz_chart(
                                dot_code, use_container_width=True
                            )
                        except Exception:
                            st.info(
                                "마인드맵 다이어그램은 오른쪽 상세 노트/풀이를 참고해 주세요."
                            )

                    with col_res2:
                        st.subheader(
                            "📚 단권화 노트 (심화 메커니즘 + 실전 문제 + 풀이)"
                        )
                        st.markdown(markdown_text)
                else:
                    st.markdown(raw_output)
            else:
                st.error(
                    "❌ AI 서버 통신이 지연되었습니다. 버튼을 다시 한번 누르시거나, 왼쪽 사이드바에 무료 Gemini API 키를 넣으시면 100% 즉시 생성됩니다!"
                )