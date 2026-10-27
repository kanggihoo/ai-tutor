# KV Cache 출발점: Q·K·V는 알지만 재사용 원리와 모양은 모름

Attention 논문을 읽어서 Q, K, V가 있다는 건 안다. 하지만 왜 K·V만 저장해도 되는지(causal mask), K가 "head 수 × head 크기"인 이유(한 벡터를 조각낸 것)는 몰랐다. 또 KV Cache를 API 프롬프트 캐싱 할인(요청 사이 prefix caching)과 같은 것으로 알고 있었다. 이 혼동은 0001에서 바로잡았고, W3·W5 prefix caching 수업에서 다시 확인해야 한다.

**Evidence**: 2026-10-27 세션 시작 복습 퀴즈 답변. "1.7B × 2바이트"로 가중치 크기는 스스로 계산했다.

**Implications**: 모양이나 크기 설명은 원 논문 숫자(512 = 8 × 64)에서 출발해 그림으로 보여 준다. prefix caching을 다룰 때 "요청 안과 요청 사이"를 먼저 구분하게 한다.
