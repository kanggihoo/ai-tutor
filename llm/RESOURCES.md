# LLM 서빙 Resources

## Knowledge

### KV Cache
- [Docs: Hugging Face Transformers — Caching](https://huggingface.co/docs/transformers/v5.14.0/cache_explanation)
  공식 문서. 왜 과거 K·V를 재사용해도 되는지(causal mask), 층별 캐시 모양 `[batch, heads, seq_len, head_dim]`, 직접 짠 생성 루프 예제가 있다. Use for: KV Cache 첫 설명, W1 B 슬롯(캐시 구현) 기준 코드.
- [Article: _The Illustrated GPT-2_ by Jay Alammar](https://jalammar.github.io/illustrated-gpt2/)
  그림 중심. "1.5 Splitting into attention heads"(긴 Q·K·V 벡터를 head로 reshape), "Evaluation Time"(층마다 K·V를 유지). Use for: shape가 글로 안 잡힐 때.
- [Paper: _Attention Is All You Need_ (Vaswani et al., 2017)](https://arxiv.org/abs/1706.03762)
  §3.2.2 Multi-Head Attention, Table 3(base: N=6, d_model=512, h=8, d_k=64). Use for: head 크기 = d_model/h의 출처.
- [Paper: _Fast Transformer Decoding: One Write-Head is All You Need_ (Shazeer, 2019)](https://arxiv.org/abs/1911.02150)
  MQA. K·V head를 1개로. Use for: KV head 수를 줄이는 이유.
- [Paper: _GQA_ (Ainslie et al., 2023)](https://arxiv.org/abs/2305.13245)
  MHA와 MQA의 중간. Use for: Qwen3, Llama 계열의 Q 16 / KV 8 구조 설명.
- [Paper: _Efficient Memory Management for LLM Serving with PagedAttention_ (Kwon et al., 2023, vLLM)](https://arxiv.org/abs/2309.06180)
  §3 "Large KV cache": OPT-13B 토큰당 800 KB 계산. 기존 시스템은 KV 메모리의 20.4~38.2%만 실제 토큰 상태 저장에 썼다. decode 단계는 memory-bound. Use for: 크기 검증, W3 PagedAttention 원문.
- [Paper: _Efficiently Scaling Transformer Inference_ (Pope et al., 2022)](https://arxiv.org/abs/2211.05102)
  PaLM 추론 분석. multiquery attention의 낮은 메모리로 긴 컨텍스트를 확장. Use for: 0003 prefill/decode 병목 (본문 미확인, 다음 레슨 전에 읽고 확인).

### 모델 설정
- [Config: Qwen3-1.7B config.json](https://huggingface.co/Qwen/Qwen3-1.7B/blob/main/config.json)
  2026-10-27 확인: hidden 2048, 28층, Q 16 / KV 8 head, head_dim 128, bfloat16, max_position_embeddings 40960.

## Wisdom (Communities)
- [vLLM Forums](https://discuss.vllm.ai/)
  vLLM 사용자 포럼(Discourse). 공식 운영 여부는 미확인. Use for: 설정, 버전 호환 문제 질문.
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
  로컬 추론과 양자화 실측 사례가 많다. 정보 품질 편차가 크므로 수치는 원문으로 다시 확인한다. Use for: 소형 GPU 실전 경험.

## Gaps
- prefill/decode 병목을 그림으로 잘 설명한 1차 자료 (0003 전에 찾기)
- hybrid(linear attention) 모델의 캐시 구조 자료 (Qwen3.5, W2~W3)
