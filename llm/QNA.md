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
