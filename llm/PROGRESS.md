# LLM 진행 현황 (튜터가 매 슬롯 후 갱신 · Mac/Windows 공통)

튜터 규칙은 [AGENTS.md](AGENTS.md), 질문 기록은 [QNA.md](QNA.md), 레슨 노트는 `notes/`에 있습니다. 주차 구성의 근거는 [docs/roadmap-decisions.md](docs/roadmap-decisions.md)에 있습니다.

## 프로필 (2026-10-27 인터뷰)
- 목표: 취업 포트폴리오(LLM 엔지니어 / MLOps / AI 인프라) + "이걸 모르면 안 될 것 같아서".
- 강함: Python, NumPy, FastAPI·Spring, Docker 실전(Hostinger VPS에서 nginx, Jenkins, Postgres, Redis, Grafana·Alloy·Prometheus·Loki·Tempo 운영). 대학에서 AI 부전공을 했고 대학원 준비로 1년 공부함(2~3년 전). ML/DL 기초는 모두 알고, PyTorch로 CNN을 작성해 봄. "Attention Is All You Need"를 읽었고 GPT-3(2022)까지 앎.
- 써 봄: LLM API, RAG, LangChain, LangGraph, agent/tool calling.
- 공백: 2022년 이후 흐름(SFT/RLHF/DPO, 추론 모델), KV Cache(자주 들었지만 잘 모름), 서빙 전반, K8s(안 써 봄), `docker run --gpus`. LoRA와 양자화는 개념만 앎.
- 수학: MoE, KV Cache, 증류, LoRA, RL은 수식 없이 직관으로. 논문은 "무엇을 말하는지" 수준.
- 비유 기준: 백엔드(커넥션 풀, 캐시, 로드밸런서), Docker Compose, Grafana 지표.

## 모델
| 역할 | 모델 | 비고 |
|---|---|---|
| 교과서 기준선 | Qwen3-1.7B | 순수 GQA, 28층, Q 16 / KV 8 head, Apache 2.0 (config 문서 확인). W2 첫 vLLM 기동과 W3 KV 예측용 |
| 주력 | Qwen3.5-4B (fallback 2B) | **hybrid: 32층 중 24층이 linear attention**. 비전 내장이라 `--language-model-only` 사용(vLLM 문서 확인, 4070 실측은 미확인). 4B BF16은 8GB에 KV 여유가 없음 |
| spec decoding | Gemma 4 E4B + MTP 버전 | 4070 구동 여부 미확인. 안 되면 지원되는 소형 구성으로 대체 |
| MoE (선택) | Gemma 4 26B-A4B | 클라우드에서 최대 1시간, W10, 필수 정산 뒤에만 |

## 커리큘럼 (12주, 슬롯 = 약 50분, 필수 최대 8 + 복구 2)
| 주 | 날짜 | 주제 | 필수 슬롯 | 원문 (카드) | 완료 증거 | 상태 |
|---|---|---|---|---|---|---|
| W1 | 10/27~11/2 | Transformer 복습 + **KV Cache** | 환경 2(지원 확인표는 문서 확인만, 이미지 pull 시작) · nanoGPT A 2(짧은 학습, Attention 논문과 대응) · B 3(캐시 없는 생성 → 캐시 구현 → logits 일치 검증 후 지연 측정) · 기록 1 | Attention 복습 (GPT-2, GPT-3) | `env/support.md`, `nanogpt/kv_cache/` | ⬜ |
| W2 | 11/3~11/9 | 2022 이후 구조 + 샘플링·양자화 | C 3(RMSNorm → RoPE → GQA, **별도 분기**, 변형마다 cache on/off 일치 확인) · D 2(GPT-2 호환 경로로 샘플링, INT8) · F 1(FastAPI로 직접 짠 서빙, 동시 요청) · vLLM 단일 요청 1(Qwen3-1.7B) · 기록 1 | (RoFormer, GQA, Llama, hybrid cache) | `nanogpt/variants/`, `naive_serve/` | ⬜ |
| W3 | 11/10~16 | **vLLM** (PagedAttention, continuous batching) | vLLM 원문 2 · base 서빙 + 하네스 v0 2 · Grafana 1 · sweep 1(Qwen3-1.7B로 KV 예측 확인 → Qwen3.5 관찰) · 기록 1 · 복구 1 | **vLLM** (Orca) | `bench/`, `results/vllm-4070/`, `dashboards/` | ⬜ |
| W4 | 11/17~23 | LoRA·QLoRA + Triton | SFT 최소 개념 1 · LoRA 원문 1 · QLoRA 2(**호환성 관문**: 짧게 학습 → 저장 → 재로드 → vLLM 서빙) · 어댑터 서빙 1 · Triton+vLLM 2 · 기록 1 | **LoRA** | `finetune/`, `triton/` | ⬜ |
| W5 | 11/24~30 | SGLang + spec decoding + **반납 체크아웃** | SGLang 2 · spec decoding 2(같은 target on/off, 동시성 1과 중간값) · 체크아웃 1 · 기록 1 · 복구 2 (하네스 v1: prefix 2세트) | (SGLang, Speculative Decoding, EAGLE) | `results/sglang-4070/`, `CHECKOUT.md` | ⬜ |
| W6 | 12/1~7 | 학습 흐름 (SFT → RLHF → DPO → GRPO) | InstructGPT 2 · R1 2 · DPO·증류·MoE 카드 1 · Mac 기본 추론 1 · 비교 설명 1 · 기록 1 | **InstructGPT**, **DeepSeek-R1** | `notes/` | ⬜ |
| W7 | 12/8~14 | 클라우드 배포 | Modal 배포(가중치는 Volume에) · cold start 분해 · 같은 하네스로 재측정 · 비용 기록 | – | `deploy/modal/`, `results/modal-*/`, `COSTS.md` | ⬜ |
| W8 | 12/15~21 | 커널 최적화 + TensorRT-LLM | FlashAttention 2 · 지원 확인·변환·빌드 2 · Triton 배치 1 · 벤치 1 · Dynamo 카드 1 · 기록 1 | **FlashAttention** (Megatron) | `trtllm/` | ⬜ |
| W9 | 12/22~28 | K8s 맛보기 | kind 1 · llama.cpp 서버 + probe 2(startupProbe vs readiness) · PVC + initContainer 1 · 롤링 업데이트·롤백 1 · Helm 1 · production-stack GPU chart 읽기 1 · 기록 1 | – | `deploy/k8s/` | ⬜ |
| W10 | 12/29~1/4 | 캡스톤 리포트 | 실험표 정리 2 · 해석 2 · 재현 README 2 · 선택 MoE 1 · 기록 1 (하네스 v2: goodput) | – | `REPORT.md` | ⬜ |
| W11 | 1/5~11 | 최종 게이트웨이 | 경로 1 · 프록시 1 · streaming 1 · 인증·요청 제한 1 · cold start·timeout 1 · 관측 1 · 통합 확인 1 · 기록 1 | – | `gateway/` | ⬜ |
| W12 | 1/12~18 | 복구 + 마무리 | 미완료 복구(최대 4) · 데모 2 · 최종 문서 1 · 회고 1 | – | `REPORT.md`, 이 파일 | ⬜ |

- 원문 = 신규 5편(굵게) + W1 Attention 복습. 괄호 안은 카드로만 다룬다.
- 완료 증거의 경로는 `llm-serving-lab` 기준이다. W6 노트만 이 폴더에 둔다.
- 상태: ⬜ 안 함 · 🔄 진행 중 · ✅ / 🔁 / 📖 / ⏭ / ❌ ([AGENTS.md](AGENTS.md)의 완료 범례)

### 주차별 필수 기준
- **W1 지원 확인표**: 엔진(vLLM, SGLang, Triton) × 모델(Qwen3-1.7B, Qwen3.5-2B/4B, Gemma 4 E4B) × 정밀도 × 기능(LoRA, prefix caching, spec, `--language-model-only`)을 표로 만든다. 각 칸에 문서 확인 / 실측 성공 / 미검증을 표시한다. 실측은 각 엔진 주에 채운다. LoRA는 full attention·MLP 범주라는 것만 보고 지원된다고 가정하지 않는다. W4 관문을 통과한 실제 모듈 경로만 쓴다.
- **W4**: 관문이 실패하면 공개된 호환 어댑터로 서빙 경로만 먼저 확인한다. 이때 QLoRA는 ✅가 아니라 미완료로 남긴다.
- **W7/W8**: 클라우드 단가는 그 주 첫 슬롯에 공식 가격표로 다시 확인한다(2026-10-27 기준 Modal GPU: L4 $0.80/h, L40S $1.95/h, A100 80GB $2.50/h, CPU·RAM은 별도). TP=2는 MoE보다 우선순위가 낮다.
- **W11**: 응답을 시작하기 전 실패는 HTTP 503 등으로, 시작한 뒤 실패는 stream 오류 이벤트로 처리한다(SSE를 시작하면 상태 코드를 바꿀 수 없음). 생성 중인 요청을 자동으로 재시도하지 않는다. 정상 warm 요청 1번과 실패 경로 3개(cold 지연, 응답 전 timeout, stream 중단)를 재현하고, 클라이언트 결과와 게이트웨이 로그를 맞춰 본다. nginx `proxy_buffering`을 확인한다.

### 체크 질문 (주당 3개, 자기 실행 결과와 조건을 붙여 답하면 통과)
- **W1**: 캐시가 없으면 t번째 토큰에서 무엇을 다시 계산하나 / 왜 K와 V만 캐시하고 Q는 안 하나 / prefill과 decode는 각각 무엇이 병목인가(입력 길이, batch, 하드웨어 조건 포함)
- **W2**: KV head를 32에서 8로 줄이면(GQA) KV 메모리는 어떻게 되나 / 회전된 K를 캐시해도 되는 이유 / INT8로 줄어드는 것과 위험한 것
- **W3**: PagedAttention이 없앤 KV 메모리 낭비는 무엇인가 / continuous batching이 static batching보다 나은 이유 / 동시성이 오르면 TTFT와 throughput은 어떻게 변하나(조건 포함)
- **W4**: rank r과 학습 파라미터 수의 관계 / QLoRA에서 4bit인 것과 아닌 것 / Triton+vLLM backend에서 batching은 누가 하나
- **W5**: SGLang RadixAttention과 vLLM prefix caching은 무엇이 다른가 / spec decoding이 오히려 느려지는 조건 / acceptance rate는 무엇을 뜻하나
- **W6**: InstructGPT 3단계 / DPO가 RLHF에서 없앤 것 / R1-Zero(RL만 사용)의 문제와 R1의 처방
- **W7**: cold start를 다운로드, 컨테이너 기동, 모델 로딩, 첫 생성으로 어떻게 나눴나 / scale-to-zero가 비용과 첫 요청에 주는 영향 / 4070과 클라우드 결과의 차이를 GPU 차이와 설정 차이로 나눌 수 있나
- **W8**: FlashAttention은 무엇의 이동을 줄이고 결과에서 무엇을 보존하나 / TensorRT-LLM 비교에서 모델, 정밀도, backend가 다르면 결론을 어떻게 제한해야 하나 / Triton, TensorRT-LLM, Dynamo는 각각 무엇을 담당하나
- **W9**: startup, readiness, liveness probe가 실패하면 각각 무슨 일이 일어나나 / Pod를 다시 만들 때 PVC 캐시와 initContainer는 무엇을 바꾸나 / CPU 실습으로 확인한 것과 GPU chart를 읽기만 한 것은 무엇인가
- **W10**: 가장 믿을 만한 비교표 하나의 통제 조건과 한계 / 최대 throughput과 goodput이 다른 이유 / MoE의 활성 파라미터 수가 전체 가중치 메모리와 같지 않은 이유
- **W11**: 응답 시작 전과 후의 오류를 어떻게 다르게 전달했나 / nginx buffering과 timeout이 토큰 도착에 준 영향 / 인증, 요청 제한, 관측은 VPS와 Modal 사이 어디에 있나
- **W12**: 새 환경에서 재현하는 최소 명령 / 실패한 실험 하나의 원인과 다음 검증 / 이 서비스의 비용, 성능, 지원 범위를 면접에서 어떻게 설명하나

### 로드맵 완료 기준
"약점 0"이 아니라 목표별 증거로 판단한다. 공개 저장소에 다음이 있으면 완료다.
- 실행 명령, 고정 버전, 원자료, 비교표, 한계
- 게이트웨이를 거친 정상·오류 데모
- 체크 질문 설명
- 비용 정산과 남은 약점 목록

필수 실습을 📖로 남겼다면 "기록 정리 완료, 필수 실습 미완료"로 함께 표시한다.

## 약점 (Weak spots)
- (아직 없음. 인터뷰 기준 공백은 프로필 참고)

## 확인한 진도
| 주 | 항목 | 상태 | 증거 |
|---|---|---|---|

## 비용
| 날짜 | 플랫폼 | GPU | 시간 | 금액 | 용도 |
|---|---|---|---|---|---|

## 세션 로그
- 2026-10-27 (Windows): 인터뷰로 수준 파악, Claude와 Codex(GPT-6.1-Sol)가 20턴 토론으로 주차안 확정, 과목 폴더 생성. 레슨 진행은 아직 안 함.

## 다음 단계
1. **W1 환경 슬롯 ①**: WSL2에서 `nvidia-smi` 확인, Docker `--gpus all` 테스트, vLLM·SGLang·Triton 이미지 pull을 백그라운드로 시작, HF와 Modal 가입.
2. W1 지원 확인표(문서 확인)를 `~/Desktop/llm-serving-lab/env/support.md`에 채운다. 저장소는 README와 .gitignore만 있는 상태다(2026-10-27 생성, Mac에서는 clone 필요).
