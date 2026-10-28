# 진행 현황 (튜터가 매 과제/퀴즈 후 갱신)

튜터 규칙·레슨 구성·실습 환경 재생성 절차는 [AGENTS.md](AGENTS.md)를 보세요.

## 프로필
- git CLI 기본은 알고 있음(2026-10-29 본인 확인) → **CLI 명령어는 가르치지 않는다.** lazygit UI 조작만.
- 용도: Claude Code가 만든 변경을 검토·선별해서 커밋. SSAFY 팀 프로젝트(Jira S15P31A302)도 하므로 협업 git 수요가 실재.
- 선호: 세션당 20~30분, 대화로 한 문제씩. 쉬운 건 빠르게. "이걸 쓸 일이 있나"를 자주 물음 → 쓰임새를 한 줄로.
- 환경: lazygit 0.61.1 (Homebrew, Mac). Windows(SSAFY) 미확인.
- **브랜치·rebase 실제 경험은 미확인.** J1 시작 전에 상황으로 묻는다:
  "팀 프로젝트에서 내 브랜치 작업 중에 다른 사람이 올린 걸 가져와야 했던 적 있어요? 그때 뭘 했어요?"

## 커리큘럼
| # | 레슨 | 상태 | 시작 tip 해시 | 메모 |
|---|------|------|------|------|
| J1 | 파일 단위 stage·커밋 | ⬜ | | ai-tutor 저장소에서. `Space g g` 복습 |
| J2 | hunk·줄 단위 부분 stage | ⬜ | | ai-tutor 저장소에서 |
| J3 | branch | ⬜ | | ai-tutor 저장소에서 |
| J4 | stash | ⬜ | | ai-tutor 저장소에서 |
| J5 | reset (soft) | ⬜ | | 여기부터 ~/lazygit-practice |
| J6 | 원격 (fetch/pull/push) | ⬜ | | upstream은 fixture에 선설정 |
| J7 | rebase | ⬜ | | 미공개 개인 브랜치 조건 |
| J8 | cherry-pick | ⬜ | | |
| J9 | 충돌 (abort → 해결 → continue) | ⬜ | | |

**선행 없음.** lazygit 레슨은 전부 여기 있다(2026-10-29에 nvim 과목에서 옮겨옴).
nvim 과목에는 Snacks Picker/Explorer만 남는다. → `../nvim/PROGRESS.md`

## 약점 (Weak spots)
- `Space g g`(nvim에서 lazygit 열기): 2026-10-28 퀴즈에서 모름. nvim 과목 약점이지만 여기 복습 퀴즈 ③에도 포함.
- `]h`(gitsigns 다음 hunk): 2026-10-28 퀴즈에서 `n`/`N`과 혼동. 같이 복습.

## 다루지 않는 것
- **git CLI 명령어** — 본인이 기본은 안다고 함.
- **실습 없이 판단·시연만**: force push, 공유 커밋 재작성, hard reset.
- **설명만**: 첫 push의 upstream 설정(`u`), `b`(양쪽 담기), `z`/`Z`(undo/redo — 복구 범위가 좁아 기댈 수 없음).

## 세션 로그
- 2026-10-29: 과목 신설. Claude↔Codex 토론으로 7회 구성 합의
  (`.herdr-discuss/20261028-2303-git-scope/summary.md`). 아직 레슨 미시작.

## 다음 단계
1. **J1 시작**: 마침 이 저장소에 밀린 변경이 있으니 그걸로 실습한다
   (`rust/lab/src/bin/*.rs` 등). 터미널에서 `lazygit` → Files에서 `Space`로 하나만 담아 `c`로 커밋.
2. J3 시작 전에 상황 질문으로 브랜치 경험 진단:
   "팀 프로젝트에서 내 브랜치 작업 중에 다른 사람이 올린 걸 가져와야 했던 적 있어요? 그때 뭘 했어요?"
