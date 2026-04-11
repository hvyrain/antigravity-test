# Google Antigravity Test
1. 매우 훌륭하게 잘 동작함.
2. flights, iris 데이터 분석 코드 각각 생성
3. 두 파일을 통합하여 st.Navigate를 이용해 랜딩페이지 잘 작성함
4. 추가로 kosis.kr의 1인당 국민소득 csv 파일을 분석하는 계획 수립 및 코드 생성
5. 자동으로 gdp 파일을 랜딩페이지에 삽입해 줌
6. Mac mini의 gemma4:26b로 gdp 파일 분석한 결과 지도 추가 의견
7. gemini flash로 코드 생성 및 수정

## 소감
- VS Code에 비해 매끄럽게 동작함.
- 유의사항 : Token 소비에 신경을 쓰라는 Grok의 조언
- Roo 및 korean 확장도 잘 동작함.
- Git도 더 매끄럽게 동작

## 왜 Antigravity가 더 빠르고 매끄럽게 느껴질까?
- Google이 Antigravity를 위해 Gemini를 "IDE 전용"으로 튜닝했다.   
VS Code의 Gemini Code Assist나 Copilot은 범용 확장이라 중간 과정이 많지만, Antigravity는 Google이 처음부터 Agentic workflow를 가정하고 만들었기 때문에 불필요한 지연이 적습니다.
- Planning Mode + Fast Mode 분리   
Antigravity는 "먼저 계획 세우고 → 실행" 구조가 잘 되어 있어서, 큰 작업(예: Streamlit 페이지 이동 구현)에서 AI가 더 스마트하고 빠르게 움직입니다. VS Code는 보통 한 번에 모든 걸 처리하려다 보니 컨텍스트가 복잡해지면 느려집니다.
- 최적화 수준 차이   
Antigravity는 아직 신규 도구라 AI 관련 코드 경로를 매우 가볍고 빠르게 설계했습니다. 반대로 VS Code는 수많은 확장과 오랜 레거시를 안고 있어서, AI가 활성화되면 전체 에디터가 약간 무거워지는 경향이 있어요.

## 실제 사용자들의 공통 의견 (2026년 4월 기준)

Streamlit, 웹 앱 프로토타이핑, multi-file 리팩토링 같은 작업에서는 Antigravity가 확실히 빠르고 결과물도 좋다는 평가가 많습니다.   
반대로, 매우 큰 기존 프로젝트 유지보수나 안정성이 최우선일 때는 VS Code + Copilot/Gemini Code Assist가 더 안정적이라는 의견도 있습니다.   
AI 응답 속도에서 "2배 이상 차이"를 느끼는 사람은 꽤 많아요. 특히 Agent가 전체 작업을 맡을 때 그 차이가 극대화됩니다.   

## 당신에게 맞는 현실적인 사용법
- 빠른 프로토타이핑 / 새로운 기능 추가 / Streamlit multi-page → Antigravity 계속 사용 (지금처럼)
- 세밀한 디버깅, 대규모 리팩토링, 안정적 유지보수 → VS Code + Gemini Code Assist 또는 Roo + Gemma4 병행
- 최고의 생산성 → 하이브리드   
→ 큰 구조/기능 추가 = Antigravity Agent   
→ 작은 수정, 오류 잡기, Git 세밀 작업 = VS Code
