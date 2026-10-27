# 로드맵 결정 근거

2026-10-27 인터뷰(grilling)와 Claude ↔ Codex(GPT-6.1-Sol) 20턴 토론의 결과다. 원본 턴 파일은 `.herdr-discuss/20261027-0943-llm-roadmap-weekly-plan/`에 있다(git 제외).

토론 뒤 사용자 결정(2026-10-27): 반납은 12월 초로 보고 GPU 필수 실습은 11/30까지 / 연말 가용 시간 문제없음(W9, W10 8슬롯 유지) / **Qwen3-1.7B 교과서 기준선 추가** / 공개 저장소 이름 `llm-serving-lab`.


참가: discuss-claude(w25:p1) ↔ discuss-codex(w25:p3, gpt-6.1-sol). 20턴(10라운드), 2026-10-27 종료.

## 합의된 주차안 (12주 기본, 세션 1회 = 50분, 주당 필수 최대 8 + 복구 2)
| 주 | 날짜 | 주제 / 필수 | 원문 (카드) |
|---|---|---|---|
| W1 | 10/27~11/2 | 환경 2(W0 흡수, 지원 표는 **문서 확인만**) · nanoGPT A 2 · B(KV Cache) 3 · 기록 1 | Attention 복습 (GPT-2/3) |
| W2 | 11/3~11/9 | C 3(RMSNorm→RoPE→GQA, **별도 분기**) · D 2 · F 1 · vLLM 단일 요청 1 · 기록 1 | (RoFormer, GQA, Llama, 하이브리드 cache) |
| W3 | 11/10~16 | vLLM 원문 2 · base 서빙 + 하네스 v0 2 · Grafana 1 · sweep 1 · 기록 1 · 복구 1 | vLLM (Orca) |
| W4 | 11/17~23 | SFT 최소 개념 1 · LoRA 원문 1 · QLoRA 2(**호환성 관문**) · 어댑터 서빙 1 · Triton+vLLM 2 · 기록 1 | LoRA |
| W5 | 11/24~30 | SGLang 2 · spec decoding 2 · **반납 체크아웃** 1 · 기록 1 · 복구 2 (하네스 v1) | (SGLang, Spec, EAGLE) |
| W6 | 12/1~7 | 학습 흐름: InstructGPT 2 · R1 2 · DPO/증류/MoE 카드 1 · Mac 추론 1 · 비교 1 · 기록 1 | InstructGPT, DeepSeek-R1 |
| W7 | 12/8~14 | Modal 배포(CPU로 가중치를 Volume에 미리 저장) · cold start 분해 · 재측정 · 비용 | – |
| W8 | 12/15~21 | FlashAttention 2 · TensorRT-LLM 빌드 2 · Triton 1 · 벤치 1 · Dynamo 1 · 기록 1 | FlashAttention (Megatron) |
| W9 | 12/22~28 | kind + llama.cpp 실제 컨테이너(startupProbe, PVC, initContainer) · 롤백 · Helm · GPU chart 읽기 | – |
| W10 | 12/29~1/4 | 비교표·해석·재현 README · 하네스 v2(goodput) · 선택 MoE 1h | – |
| W11 | 1/5~11 | VPS 게이트웨이: 정상 1 + 실패 3 재현, nginx buffering, cold start | – |
| W12 | 1/12~18 | 복구(최대 4) · 데모 · 최종 문서 · 회고 | – |

## 핵심 원칙
- **엔진 비교(vLLM vs SGLang)** 와 **서빙 경로 비교(vLLM 직접 vs Triton+vLLM)** 는 별개의 표로 만든다. Triton vLLM backend는 독립 엔진이 아니다 (turn 08).
- 원자료는 v0부터 저장한다(요청별 시각, 출력 토큰, 오류, 엔진 상한, 어댑터 메타). 분석은 v0→v1→v2로 단계적으로 늘린다 (turn 11, 12, 17).
- sweep 중단 조건은 OOM, 연속 timeout, 예산 소진이다. SLO 위반은 중단 조건이 아니라 관찰 결과다. 헤드라인은 SLO를 지키는 최대 동시성과 goodput (turn 09, 10).
- 벤치는 non-thinking 모드로 고정한다 (turn 18). KV Cache는 속도보다 logits 일치 검증이 먼저다 (turn 04).
- 클라우드 3만 원 배분은 W7 30%, W8 40%, 복구 30%. MoE와 TP=2는 필수 실습 정산 뒤에만 한다 (turn 06, 08).
- 완료 범례: ✅ 확인 / 🔁 대체(목표 단위로 표시) / 📖 설명만 / ⏭ 미실시 / ❌ 실패. 확정 목표는 범례를 붙이는 것만으로 충족되지 않는다 (turn 11, 14).
- 저장소 루트는 둘이다: 공개 `<bench>/`(코드, 원자료, 리포트)와 `ai-tutor/llm/`(노트, 약점). 원문은 신규 5편 + Attention 복습.

## 상대가 놓친 점 (turn 번호)
- **codex**: vLLM을 QLoRA보다 먼저(02), KV logits 검증(04), FlashAttention 과밀(08 수용), Triton 정정(08), C 분기(12), SSE는 시작 후 503 불가(12), Qwen3.5-4B 하이브리드 24/32층(16), thinking 토큰(18), 비교 교란 변수(18)
- **claude**: 4B BF16이 8GB에 안 들어감(01), 이론을 GPU 창 밖으로(03), CPU 가중치 사전 다운로드(05), 하네스 고정(05), 반납 체크아웃과 자격 증명 삭제(07), K8s는 실제 모델로(09), prefix 워크로드 2세트(09), 방법론 과적재(11), 비전 인코더 VRAM(15)

## 사용자 확인 항목
1. 정확한 반납일
2. 연말(W9, W10) 가용 시간 → 줄면 조건부 축소
3. 교과서 기준선 Qwen3-1.7B(순수 GQA, Apache 2.0) 추가 여부 (선택)
4. 공개 저장소 이름
