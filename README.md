# AI 1:1 학습실

Claude Code와 대화하면서 한 문제씩 배웁니다. 과목마다 폴더가 있고, 진도는 각 폴더의 `PROGRESS.md`에 남습니다.

| 폴더 | 과목 | 시작 |
|---|---|---|
| [nvim/](nvim/) | LazyVim 키 익히기 (카페 프로젝트 미션) | `cd nvim && claude` |
| [rust/](rust/) | Rust 코드 읽기·판단·지휘 (이론 → 예측 퀴즈 → 실전) | `cd rust && claude` |
| [llm/](llm/) | LLM 개념·논문 → vLLM·SGLang·Triton 서빙·배포 (12주, 50분 슬롯) | `cd llm && claude` |
| [git/](git/) | lazygit 다루기 (CLI 아님) | `cd git && claude` |
| [zed/](zed/) | Zed 에디터 익히기 (내장 AI 제외) | `cd zed && claude` |
| [distsys/](distsys/) | 분산 이벤트 패턴 실습: outbox·inbox·CQRS (Python, Postgres, Redpanda) | `cd distsys && claude` |
| [gof/](gof/) | GoF 디자인 패턴: 23개 중 선별해 Java로 실습 ([무엇을, 왜](gof/README.md)) | `cd gof && claude` |

저장소 루트에서 `claude`를 실행하면 튜터가 오늘 할 과목을 먼저 묻습니다.

## Rust 복습할 때
- `rust/notes/`: 레슨별 1페이지 노트(이론 요약, 퀴즈와 정답, 틀린 것)
- `rust/QNA.md`: 실습 중 물어본 질문과 답(주제별)
- `rust/PROGRESS.md`: 약점 목록과 다음 단계
