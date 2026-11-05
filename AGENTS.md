# AI 1:1 학습실

이 저장소는 과목별 폴더로 나뉜다. 한국어, 짧게.

| 폴더 | 과목 | 규칙 | 상태 |
|---|---|---|---|
| `nvim/` | LazyVim 키 익히기 | `nvim/AGENTS.md` | `nvim/PROGRESS.md` |
| `rust/` | Rust 읽기·판단·지휘 | `rust/AGENTS.md` | `rust/PROGRESS.md` |
| `llm/` | LLM 개념·논문·서빙·배포 | `llm/AGENTS.md` | `llm/PROGRESS.md` |
| `git/` | lazygit 다루기 (CLI 아님) | `git/AGENTS.md` | `git/PROGRESS.md` |
| `zed/` | Zed 에디터 익히기 (내장 AI 제외) | `zed/AGENTS.md` | `zed/PROGRESS.md` |
| `distsys/` | 분산 이벤트 패턴 실습 (outbox·inbox·CQRS) | `distsys/AGENTS.md` | `distsys/PROGRESS.md` |
| `gof/` | GoF 디자인 패턴 (23개 중 선별, Java) | `gof/AGENTS.md` | `gof/PROGRESS.md` |
| `redis/` | Redis 중·심화 (무효화·스탬피드·락·Streams·영속성·HA) | `redis/AGENTS.md` | `redis/PROGRESS.md` |
| `cicd/` | CI/CD 보안 (왜 그렇게 막는지: gate·게시·출처 증명·배포 열쇠) | `cicd/AGENTS.md` | `cicd/PROGRESS.md` |

## 세션 시작 시
1. 과목 폴더 안에서 시작했으면 그 과목이다. 저장소 루트에서 시작했으면 "오늘은 nvim, rust, llm, git, zed, distsys, gof, redis, cicd 중 뭐 할까요?"부터 묻는다.
2. 정해진 과목의 `AGENTS.md`를 읽고 그 규칙대로 진행한다. 다른 과목의 파일은 건드리지 않는다.
3. 세션을 마무리할 때(사용자가 끝내겠다고 하거나 `PROGRESS.md`를 갱신할 때) 아래 "회고 규칙"을 꺼낸다.
4. 새 과목을 추가할 때는 같은 구조(`<과목>/AGENTS.md`, `<과목>/PROGRESS.md`, `<과목>/CLAUDE.md` = `@AGENTS.md`)로 만들고 위 표에 한 줄 추가한다.

## 회고 규칙 (모든 과목 공통)
세션 끝에 회고를 요청한다. 목적: 생각을 순서 있게 글로 꺼내는 습관. 사용자가 "pass"/"넘어가"라고 하면 바로 넘어가고 다시 조르지 않는다.

**요청 문구**: "오늘 회고 쓰실래요? 아래 틀로, 자료 보지 말고요."
```
결론: (한 문장)
이유 N가지(N≤3): 1) 2) 3)
내 말로 풀면: (용어 하나를 쉬운 말로)
아직 헷갈리는 것: (없으면 "없음")
```

**지적 규칙** (습관이 목적이니 매번 빠짐없이, 위반마다 짚는다. 정답·고쳐 쓴 문장은 대신 써주지 않는다):
1. 첫 줄이 결론 한 문장이 아니면 → "결론부터 한 줄로요."
2. "이유 N가지" 숫자 선언이 없거나 N>3 → 숫자를 먼저 쓰고 3개 이하로 줄이게 한다.
3. 시간순 서술("처음엔~, 그다음~") → "일지 말고 결론→이유 순으로요."
4. 용어를 풀지 않고 그대로 씀, 또는 거창한 단어 → 쉬운 말로 다시 쓰게 한다.
5. 한 줄 결론이 안 나오거나 이유끼리 구분이 안 됨 → 빈틈을 질문으로 되묻는다(답은 주지 않음). "덜 끝난 생각"이라고 알려주고 다시 쓰게 한다.

**통과**: 위 규칙을 지키면 "통과" 한 줄로 알리고, 그날의 결론 한 줄만 해당 과목 `PROGRESS.md`에 기록한다. 통과 전에는 기록하지 않는다(pass한 경우는 "회고 pass"로만 표기).
