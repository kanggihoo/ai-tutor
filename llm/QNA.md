# LLM 질문 기록

실습 중 물어본 것을 튜터가 답한 직후 주제별로 적습니다. `복습`이 붙은 항목은 세션 시작 복습 퀴즈에 나옵니다. 형식은 [AGENTS.md](AGENTS.md)의 "기록"을 보세요.

## 구조 (Attention · 위치 · KV Cache)

### Q. RoPE가 뭔가? 예전 sin/cos 위치 임베딩에서 바뀐 "회전 임베딩"인가?
- 2026-10-27 · W0 인터뷰 · 복습
- 답: RoPE(Rotary Position Embedding, RoFormer 2021)가 바로 그 회전 임베딩이다. 원 논문의 sin/cos 방식은 입력 임베딩에 위치 벡터를 한 번 **더한다**(절대 위치). RoPE는 **매 attention 층에서 Q와 K를 위치에 비례한 각도로 회전**시킨다. 그러면 Q(위치 m)와 K(위치 n)의 내적에 m−n만 남아서 상대 위치가 자연스럽게 들어간다. sin/cos 주파수는 회전 각도를 정하는 데 그대로 다시 쓰인다. 서빙에서는 긴 컨텍스트 확장(`rope_scaling`, YaRN)과 "KV Cache에는 회전이 적용된 K가 저장된다"는 점으로 보인다.
- 한 줄 요약: RoPE는 위치를 더하지 않고 Q와 K를 회전시켜서, 내적에 상대 거리만 남게 한다.

### Q. 요즘도 RoPE를 쓰나, 다른 방식으로 넘어가는 중인가?
- 2026-10-27 · W0 인터뷰
- 답: 여전히 사실상 표준이다(ALiBi는 경쟁에서 밀림). 다만 그대로 쓰기보다 조정하는 쪽이다. 회전 주파수 조정(`rope_theta`, YaRN), 층마다 다른 설정(Gemma 3의 local/global), 일부 층은 위치 인코딩 없이 두기(Llama 4 iRoPE), 차원 일부에만 적용(DeepSeek MLA), 멀티모달 확장(M-RoPE)이 있다. linear attention 층은 RoPE를 쓰지 않는다(hybrid 모델). Qwen3.5와 Gemma 4의 실제 설정은 W2에서 `config.json`으로 확인한다.
- 한 줄 요약: RoPE는 교체되지 않았고, 조정·부분 적용·NoPE 혼합으로 변형되는 중이다.

### Q. KV Cache 메모리는 왜 그 계산식이 되나? (가중치와는 뭐가 다른가)
- 2026-10-27 · W1 · 복습
- 답: 층마다 attention이 따로 있으므로 토큰 하나가 층마다 K와 V를 남긴다. 한 층의 K 크기는 KV head 수 × head 크기이고, V도 같다. 그래서 토큰당 KV = 2 × 층 수 × KV head 수 × head 크기 × 바이트다. Qwen3-1.7B(28층, KV 8 head, head_dim 128은 config.json에서 확인함, BF16)는 114,688B ≈ 112KB/토큰이다. 가중치는 고정 크기(1.7B × 2B ≈ 3.4GB)지만, KV는 토큰 수 × 동시 요청 수만큼 늘어나서 동시 처리 한도를 정한다.
- 한 줄 요약: 토큰당 KV = 2(K,V) × 층 × KV head × head 크기 × 바이트. 가중치는 고정, KV는 토큰 × 동시 요청만큼 늘어난다.

### Q. API 프롬프트 캐싱 할인도 KV Cache인가?
- 2026-10-27 · W1 · 복습
- 답: 둘 다 K와 V를 저장하지만 범위가 다르다. KV Cache는 요청 하나 안에서 토큰을 생성할 때 이전 토큰의 K와 V를 다시 계산하지 않으려고 쓴다. API 할인은 요청 사이에 같은 앞부분의 KV를 재사용하는 것으로, prefix caching(W3 vLLM, W5 SGLang RadixAttention)이다.
- 한 줄 요약: KV Cache는 요청 안의 재계산을 없애고, prefix caching은 요청 사이의 같은 prefill을 없앤다.

## 학습 (SFT · RLHF · LoRA · 증류)

## 양자화

## 서빙 엔진 (vLLM · SGLang · Triton · TensorRT-LLM)

## 배포·인프라 (Modal · K8s · 게이트웨이)

## 논문

## 기타

### Q. Function Calling은 Tool Calling을 말하는 건가?
- 2026-10-27 · W0 인터뷰
- 답: 같은 개념이다. OpenAI가 처음 "function calling"이라고 불렀고, 지금은 "tool calling / tool use"라는 이름이 더 일반적이다. 모델이 도구 이름과 인자를 JSON으로 내놓으면 애플리케이션이 실행해서 결과를 다시 넣어 준다. 서빙 쪽에서는 vLLM의 tool call parser 설정으로 보인다.
- 한 줄 요약: Function Calling = Tool Calling. 이름만 다르다.
