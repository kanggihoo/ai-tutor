# 진행 현황 (튜터가 매 과제/퀴즈 후 갱신)

튜터 규칙·레슨 구성·실습 환경 재생성 절차는 [AGENTS.md](AGENTS.md)를 보세요.

## 프로필
- git CLI 기본은 알고 있음(2026-10-29 본인 확인) → **CLI 명령어는 가르치지 않는다.** lazygit UI 조작만.
- 용도: Claude Code가 만든 변경을 검토·선별해서 커밋. SSAFY 팀 프로젝트(Jira S15P31A302)도 하므로 협업 git 수요가 실재.
- 선호: 세션당 20~30분, 대화로 한 문제씩. 쉬운 건 빠르게. "이걸 쓸 일이 있나"를 자주 물음 → 쓰임새를 한 줄로.
- 환경: Mac lazygit 0.61.1 (Homebrew). Windows(SSAFY) lazygit 0.63.1 (winget), tig 있음, `pull.rebase` 미설정 (2026-10-29 확인).
- **배우고 싶은 것(2026-10-29 본인 요청)**: 로컬 커밋 생성·삭제·수정·압축 / 원격에서 가져오는 여러 옵션 /
  커밋 그래프 깊게 읽기(HEAD 위치, 분기점, 협업 히스토리). 그래프는 설정·외부 도구를 추가해서라도 깊게.
- **브랜치·rebase 실제 경험은 미확인.** J1 시작 전에 상황으로 묻는다:
  "팀 프로젝트에서 내 브랜치 작업 중에 다른 사람이 올린 걸 가져와야 했던 적 있어요? 그때 뭘 했어요?"

## 커리큘럼
| # | 레슨 | 상태 | 시작 tip 해시 | 메모 |
|---|------|------|------|------|
| J1 | 파일 단위 stage·커밋 | ⬜ | | ai-tutor 저장소에서. `Space g g` 복습 |
| J2 | hunk·줄 단위 부분 stage | ⬜ | | ai-tutor 저장소에서 |
| J3 | branch | ⬜ | | ai-tutor 저장소에서 |
| J4 | stash | ⬜ | | ai-tutor 저장소에서 |
| J5 | 그래프 1: 위치 파악 (HEAD·분기점) | ⬜ | | 여기부터 ~/lazygit-practice. 이후 매 회 전후 그래프 읽기 |
| J6 | 커밋 수정 (reword·amend·soft reset) | ⬜ | | feature 브랜치(미공개) |
| J7 | 커밋 삭제·순서 (drop·이동·revert) | ⬜ | | |
| J8 | 커밋 압축 (squash·fixup) | ⬜ | | |
| J9 | 원격 가져오기 옵션 (fetch·ff·pull·merge·rebase) | ⬜ | | upstream은 fixture에 선설정 |
| J10 | rebase | ⬜ | | 미공개 개인 브랜치 조건 |
| J11 | cherry-pick | ⬜ | | |
| J12 | 충돌 (abort → 해결 → continue) | ⬜ | | |
| J13 | 그래프 2: 협업 히스토리 + 그래프 확장 | ⬜ | | 설정(`allBranchesLogCmds` 등)·tig는 사용자 동의 후 직접 |

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
- 2026-10-29: 사용자 요청 반영해 13회로 개편 — 커밋 수정(J6)·삭제(J7)·압축(J8), 원격 가져오기 옵션(J9),
  그래프 2회(J5·J13) + J5 이후 매 회 전후 그래프 읽기 루틴. 키는 Windows v0.63.1 `lazygit --config`로 확인, fixture는 스크래치에서 실행 확인.

## 다음 단계
1. **J1 시작**: 저장소가 깨끗하면(2026-10-29 기준 clean) 그날 생긴 실제 변경이나 `git/` 안 연습 메모 파일 3개로 실습한다.
   터미널에서 `lazygit` → Files에서 `Space`로 하나만 담아 `c`로 커밋.
   J1~J4가 이미 익숙하면 빠르게 확인만 하고 J5(그래프 1)로 넘어간다 — 사용자의 관심은 J5 이후에 몰려 있다.
2. J3 시작 전에 상황 질문으로 브랜치 경험 진단:
   "팀 프로젝트에서 내 브랜치 작업 중에 다른 사람이 올린 걸 가져와야 했던 적 있어요? 그때 뭘 했어요?"
