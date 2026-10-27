# Mission: LLM 개념과 서빙

## Why
LLM 엔지니어, MLOps, AI 인프라 쪽으로 취업할 때 포트폴리오로 설명할 수 있어야 한다. vLLM, SGLang, Triton으로 직접 서빙하고 측정한 결과를 "왜 그런 숫자가 나왔는지"까지 말할 수 있으면 된다. 세부 일정과 증거 기준은 [PROGRESS.md](PROGRESS.md)에 있다.

## Success looks like
- 모델 `config.json`만 보고 KV Cache 크기와 8GB GPU의 동시 요청 한도를 예측하고, vLLM 시작 로그로 맞춰 본다
- vLLM과 SGLang 벤치 결과(TTFT, TPOT, throughput, goodput)를 PagedAttention, continuous batching, prefix caching으로 설명한다
- 자기 LoRA 어댑터를 서빙하고, Modal 배포와 게이트웨이를 거친 정상·오류 데모를 공개 저장소 `llm-serving-lab`에 남긴다

## Constraints
- 한 슬롯은 약 50분, 주당 필수 8슬롯. 4070 대여 노트북은 11/30까지 쓸 수 있다
- 수식은 유도하지 않는다. 그림과 코드·설정 위치로 이해한다. 글로만 된 설명은 이해하기 어려워한다
- 클라우드 예산은 3~5만 원

## Out of scope
- 수식 유도와 논문 정독 (원문은 신규 5편만 핵심 부분 읽기)
- 대규모 사전학습, 멀티노드 학습
