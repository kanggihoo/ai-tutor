# 튜터 메모

- 2026-10-27: `/teach` 구조(MISSION, RESOURCES, lessons/, reference/, learning-records/, assets/)를 llm/에 도입했다. 기존 `PROGRESS.md`(진도, 약점), `QNA.md`(질문 기록)는 AGENTS.md 규칙대로 계속 쓴다. `notes/`에 두던 레슨 노트 역할은 `lessons/`와 `reference/`가 맡는다.
- 글로 된 설명(텍스트 벡터 모양 설명)은 이해가 안 된다고 했다. 모양, 크기 같은 건 **그림과 직접 만져 보는 위젯**으로 보여 준다.
- 암기를 싫어한다. 식이 나오면 각 항이 **왜** 있는지 이미 아는 것(Attention 논문 숫자)에서 출발해 설명한다.
- 한국어, 짧게.
- 공용 컴포넌트: `assets/lesson.css`, `assets/quiz.js`(객관식/숫자), `assets/decode-sim.js`(생성 스텝), `assets/kv-calc.js`(KV 계산기).
- 공용 컴포넌트 추가: `assets/attention-viz.js`(head별 attention 데모, 층×위치 의존 격자).
- KV Cache 레슨 순서(번호 = 배우는 순서): 0001 Q·K·V와 masked attention → 0002 왜 저장하나 → 0003 크기 → 0004 prefill/decode 병목 → 0005 PagedAttention과 prefix caching (W3 원문과 연결).
- 2026-10-27: Q·K·V 역할, multi-head, 과거 K·V 불변 이유를 "더 자세히" 원함 → 0001. 선수 레슨을 끼워 넣으면 **파일 번호를 배우는 순서대로 다시 매긴다**(사용자 요청, 만든 순서 아님).
