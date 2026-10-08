import json
import re
import urllib.parse
import requests
import streamlit as st

st.set_page_config(
    page_title="맞춤 개념 단권화 & 실전 문제 풀이", page_icon="🧠", layout="wide"
)

st.title("🧠 입력 내용 기반 심화 마인드맵 & 문제집 실전 문제/풀이")
st.caption(
    "알맹이 없는 템플릿 문구는 전면 삭제되었습니다. 입력하신 내용을 바탕으로 **세부 지식 가지치기 마인드맵 + 대표 문제집 실전 문제 + 단계별 정답 풀이**를 생성합니다."
)

st.markdown("---")

# 입력 영역 (완전 동적)
col1, col2 = st.columns([1, 1])
with col1:
    main_concept = st.text_input(
        "📍 [공부한 중심 개념]",
        placeholder="예: 중세국어, 광합성, 피타고라스 정리, 프랑스 혁명 등",
    )
with col2:
    basic_def = st.text_area(
        "📝 [내가 이해한 기본 내용 / 핵심 메모]",
        placeholder="예: 모음조화가 잘 지켜짐, 중세 때는 ㄹㅇ형인데 현대는 ㄹㄹ형 등 배운 내용을 적으세요.",
        height=100,
    )

generate_btn = st.button(
    "🚀 내 내용 기반 마인드맵 & 실전 문제/풀이 생성",
    type="primary",
    use_container_width=True,
)


# AI 응답에서 JSON 껍데기 및 불필요 시스템 코드 제거
def clean_response(text):
    if not text:
        return ""
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            text = parsed.get("content", parsed.get("reasoning", str(parsed)))
    except Exception:
        pass
    text = re.sub(r'^\{"role":.*?"content":"', "", text, flags=re.DOTALL)
    text = re.sub(r'^\{"role":.*?"reasoning":"', "", text, flags=re.DOTALL)
    return text.strip()


# AI 호출 (가짜 템플릿 문구 금지, 입력 내용 살붙이기 강제)
def generate_study_note(concept, definition):
    prompt = f"""
[사용자 입력 정보]
- 중심 개념: {concept}
- 사용자가 적은 기본 내용: {definition}

[엄격 작성 지침 - 위반 시 감점]
1. "~의 학문적 확장", "~의 심화 스펙트럼", "0. 요약" 같은 껍데기 목차 문구는 절대 쓰지 마라.
2. 사용자가 적은 [{definition}] 내용에 진짜 전공/학술 지식으로 살을 붙여라.
3. 마인드맵(Graphviz) 노드 구성:
   - 중심 노드: [{concept}]
   - 1차 가지: 사용자가 적은 기본 내용 [{definition}]의 세부 키워드
   - 2차 가지: AI가 살을 붙인 구체적 심화 원리/공식/문법 법칙/세부 예시
   - 3차 가지: 출제되는 실전 문제 포인트 및 정답 핵심 논리
4. 마크다운 노트 구성:
   - 📌 [입력 내용 정리 & 심화 살붙이기]: 입력 내용을 바탕으로 전공 수준의 세부 메커니즘/수식/문법 원리 확장
   - 📘 [대표 문제집/시험지 스타일 실전 문제 1개]: 실제로 수능/내신/자격증 시험지에 출제되는 완성된 문제 (구체적 지문, 조건, 수치 또는 보기 포함)
   - ⚡ [단계별 상세 정답 풀이]: Step 1 (조건/원리 분석) -> Step 2 (풀이/적용 과정) -> Step 3 (최종 정답)

출력 형식 (아래 구분자를 반드시 엄수할 것):
===GRAPHVIZ===
digraph Mindmap {{
    rankdir=LR;
    node [fontname="Malgun Gothic", shape=box, style="filled,rounded", color="#2B3A42", fillcolor="#E8F1F5"];
    edge [color="#3F51B5", arrowhead=vee];
    // [{concept}]와 [{definition}]의 세부 키워드로 가지치기한 구체적 Graphviz 코드 작성
}}
===MARKDOWN===
(입력 정리 & 심화 살붙이기 / 📘 대표 문제집 실전 문제 / ⚡ 단계별 상세 정답 풀이)
"""

    url = "https://text.pollinations.ai/"
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "You are a top-tier exam author and tutor. Output exact problem with real data and concrete mindmap branches.",
            },
            {"role": "user", "content": prompt},
        ],
        "model": "openai",
    }

    try:
        res = requests.post(url, json=payload, timeout=30)
        if res.status_code == 200:
            return clean_response(res.text)
    except Exception:
        pass

    try:
        encoded = urllib.parse.quote(prompt)
        res = requests.get(
            f"https://text.pollinations.ai/{encoded}?model=openai", timeout=30
        )
        if res.status_code == 200:
            return clean_response(res.text)
    except Exception:
        pass

    return None


# 실행 및 출력 영역
if generate_btn:
    if not main_concept.strip():
        st.warning("⚠️ [공부한 중심 개념]을 입력해 주세요!")
    else:
        st.markdown("---")
        with st.spinner(
            f"'{main_concept}' 내용을 바탕으로 마인드맵과 실전 문제/풀이를 생성 중입니다..."
        ):
            raw_output = generate_study_note(main_concept, basic_def)

            if raw_output:
                dot_match = re.search(
                    r"===GRAPHVIZ===\s*(.*?)\s*===MARKDOWN===",
                    raw_output,
                    re.DOTALL,
                )
                md_match = re.search(
                    r"===MARKDOWN===\s*(.*)", raw_output, re.DOTALL
                )

                col_res1, col_res2 = st.columns([1, 1])

                if dot_match and md_match:
                    dot_code = dot_match.group(1).strip()
                    dot_code = re.sub(r"```dot|```graphviz|```", "", dot_code)
                    markdown_text = md_match.group(1).strip()

                    with col_res1:
                        st.subheader("📌 입력 내용 기반 살붙이기 마인드맵")
                        try:
                            st.graphviz_chart(
                                dot_code, use_container_width=True
                            )
                        except Exception:
                            st.info(
                                "마인드맵 다이어그램은 오른쪽 상세 노트를 참고해 주세요."
                            )

                    with col_res2:
                        st.subheader(
                            "📚 맞춤 단권화 노트 & 실전 문제/단계별 풀이"
                        )
                        st.markdown(markdown_text)
                else:
                    with col_res2:
                        st.subheader(
                            "📚 맞춤 단권화 노트 & 실전 문제/단계별 풀이"
                        )
                        st.markdown(raw_output)
            else:
                st.error(
                    "❌ AI 서버 통신이 지연되었습니다. 버튼을 다시 한 번 눌러주세요!"
                )