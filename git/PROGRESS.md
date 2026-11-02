# 진행 현황 (튜터가 매 과제/퀴즈 후 갱신)

튜터 규칙·레슨 구성·실습 환경 재생성 절차는 [AGENTS.md](AGENTS.md)를 보세요.

## 프로필
- git CLI 기본은 알고 있음(2026-10-29 본인 확인) → **CLI 명령어는 가르치지 않는다.** lazygit UI 조작만.
- 용도: Claude Code가 만든 변경을 검토·선별해서 커밋. SSAFY 팀 프로젝트(Jira S15P31A302)도 하므로 협업 git 수요가 실재.
- 선호: 세션당 20~30분, 대화로 한 문제씩. 쉬운 건 빠르게. "이걸 쓸 일이 있나"를 자주 물음 → 쓰임새를 한 줄로.
- 환경: Mac lazygit 0.61.1 (Homebrew). Windows(SSAFY) lazygit 0.63.1 (winget), tig 있음, `pull.rebase` 미설정 (2026-10-29 확인).
- **배우고 싶은 것(2026-10-29 본인 요청)**: 로컬 커밋 생성·삭제·수정·압축 / 원격에서 가져오는 여러 옵션 /
  커밋 그래프 깊게 읽기(HEAD 위치, 분기점, 협업 히스토리). 그래프는 설정·외부 도구를 추가해서라도 깊게.
- **브랜치 경험(2026-10-29)**: main/develop으로 PR 올라간 것을 pull로 받아오는 경험은 있음. stash→pull→pop, 커밋 후 pull, merge vs rebase 선택 개념은 본인이 설명함(2026-10-29). 실제로 rebase로 받은 경험은 미확인. (원래 메모:) J1 시작 전에 상황으로 묻는다:
  "팀 프로젝트에서 내 브랜치 작업 중에 다른 사람이 올린 걸 가져와야 했던 적 있어요? 그때 뭘 했어요?"

## 커리큘럼
| # | 레슨 | 상태 | 시작 tip 해시 | 메모 |
|---|------|------|------|------|
| J1 | 파일 단위 stage·커밋 | ✅ b만 커밋 476a23f 확인, 퀴즈 완료(`Esc` 한 단계 뒤로는 몰랐음) | 6272df3 | ai-tutor 저장소에서. `Space g g` 복습 |
| J2 | hunk·줄 단위 부분 stage | ✅ 과제 3개 통과(hunk 담기·Tab으로 빼기·줄 1개), 퀴즈 완료(Tab·Enter→Tab→Space 정답) | 25d03f9 | ai-tutor 저장소에서 |
| J3 | branch | ✅ n·커밋·checkout·`-` 확인(reflog 475c090), 퀴즈 ①② 정답, ③ 패스 | 25d03f9 | ai-tutor 저장소에서 |
| J4 | stash | ✅ 최종 상태 확인(stash 비었고 변경 복원), 중간 화면은 사용자 보고 미수신. 퀴즈 3문항 정답 | 25d03f9 | ai-tutor 저장소에서 |
| J5 | 그래프 1: 위치 파악 (HEAD·분기점) | ✅ HEAD·tip·분기점 정답(merge-base edc2459 대조), detached HEAD→`-` 복귀 reflog 확인, 퀴즈 ①△(경로 `1`→`a`) ②△ ③패스 | feature 1dd8207, main 3777fb8, init edc2459 | 여기부터 ~/Desktop/lazygit-practice. 이후 매 회 전후 그래프 읽기 |
| J6 | 커밋 수정 (reword·amend·soft reset) | ✅ 퀴즈 ①②정답(③ 제외). 과제3개 완료(reword·`A` HEAD·`A` 옛커밋→충돌, 해결하며 `fix: 모카 가격` 커밋이 빈 커밋으로 skip됨 확인). soft reset·`e`는 설명만 | feature 1dd8207 → 현재 f781537 | feature 브랜치(미공개). 사라진 1148f76은 reflog에만 |
| J7 | 커밋 삭제·순서 (drop·이동·revert) | ⏭ 설명만(drop vs revert vs reset --soft/--hard 비교), 실습·퀴즈는 사용자 판단으로 건너뜀 | feature f781537 | |
| J8 | 커밋 압축 (squash·fixup) | 🔄 과제1 `f`(7f5da9c→8a6aa02), 과제2 `F`→`S`(→f2f892d, 모카 커밋에 americano 3600), 과제3 `s`(→396ddb1, 메시지 두 개가 이어 붙음) 완료·확인. 퀴즈: ① 정답 ② 결과는 맞음(`s`로 3개 합친 뒤 `f` — 돌아가지만 `f` 범위선택/`F`→`S`가 더 짧음) ③ `Esc`·`q` 정답(2회째) | feature 7f5da9c → 현재 396ddb1(3커밋: WIP 디버그 / feat: 모카 추가 / init) | 그래프 보기는 `+`로 확대(기본은 패널이 좁아 짤림). 범위 선택(`v`)은 화면 확인 필요 |
| J9 | 원격 가져오기 옵션 (fetch·ff·pull·merge·rebase) | 🔄 fetch·`↓1↑1` 읽기·그래프 읽기·`f` 실패(갈라져서 ff 불가) 확인. `p`→`P` 실행됨(merge 커밋 6a03f26, origin/main도 6a03f26). **`p`/`P`부터 다시 하려면 아래 "J9 되돌리기"** | a: main 3777fb8(ahead 1), feature 396ddb1, origin/main 76f0728 | upstream은 fixture에 선설정. 이 환경 `pull.rebase=false`(merge 방식) 확인 |
| J10 | rebase | ✅ feature에 origin/develop 반영, 해시 변경 확인 | 396ddb1 → 00f62be | 미공개 커밋, 충돌 없음 |
| J11 | cherry-pick | ✅ C→4→V 실습 및 원본 유지 퀴즈 통과 | 00f62be → 66f059b | 로그인 수정만 적용 |
| J12 | 충돌 (abort → 해결 → continue) | ✅ 충돌 해결·merge 완료 및 별도 abort 실습 확인 | merge a0d075f, abort 시작·복귀 115985f | 작업 트리 깨끗함 |
| J13 | 그래프 2: 협업 히스토리 + 그래프 확장 | 🔄 부모 관계·merge/rebase 비교·보기 5개 설정 완료 | feature 115985f, origin/develop dff7b00 | 독립 그래프 판독 확인은 남음 |

**선행 없음.** lazygit 레슨은 전부 여기 있다(2026-10-29에 nvim 과목에서 옮겨옴).
nvim 과목에는 Snacks Picker/Explorer만 남는다. → `../nvim/PROGRESS.md`

## 약점 (Weak spots)
- 부분 unstage 경로(`Enter`→`Tab`→`Space`): J2에서 한 번 정답. J3·J5·J6 퀴즈에서 세 번 패스, 2026-10-29 사용자가 복습에서 제외 요청 → **미졸업, 미확인**으로만 남김(졸업 처리 아님).
- 졸업(힌트 없는 정답 2회): `Esc`(한 단계 뒤로, `q`는 전체 종료, J8 퀴즈에서도 정답), `Space g g`(2026-10-29, J2·J4 퀴즈).
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
- 2026-10-29 (Windows): J1~J6 완료, J7은 설명만(실습 건너뜀). 실습 저장소를 `~/Desktop/lazygit-practice/`로 생성(레포 밖).
  J6에서 옛 커밋 `A` → 충돌 → 한쪽 선택으로 풀다가 `fix: 모카 가격` 커밋이 빈 커밋이 되어 skip됨(reflog 1148f76). 졸업: `Esc`, `Space g g`.
  사용자는 안 쓸 주제 추천에 민감하다 → 쓰임새를 솔직히 말하고 핵심만, 실습은 먼저 묻는다.
- 2026-10-30 (Windows): J8 완료(`f`·`F`→`S`·`s` 모두 확인, 퀴즈 ①③ 정답 ② 결과만 맞음). J9 시작 — fetch·ahead/behind·`f` 실패까지 확인, `p`→`P`로 merge 방식 가져오기 실행(`6a03f26`).
  사용자가 `origin/main` 위치를 못 찾아 짜증냄 → 새 화면은 키 경로를 먼저 정확히 알려 줄 것. 튜터 오류 정정: Commits `4`는 현재 브랜치만 보임, `s`는 입력창 없이 메시지를 바로 이어 붙임.
  사용자 요청으로 `p`/`P` 단계부터 재실습할 수 있게 되돌리기 절차를 기록(미실행).

## 다음 단계
1. **J9 이어서 — `p`/`P` 단계부터 다시**. 먼저 아래 "J9 되돌리기"로 갈라진 상태(`main` `↑1↓1`)를 복원한다.
   그 뒤 사용자가 `p`(merge 방식, `pull.rebase=false`) → 그래프·Command log 읽기 → `P`.
   그다음 한 번 더 되돌려 **rebase 방식**(Branches 원격 탭 → `origin` `Enter` → `origin/main` 선택 → `r`)으로 받고 그래프를 비교한다.
   `origin/main`은 **Branches `3`의 "원격" 탭(`]`)에서 `origin`→`Enter`** 안에 있다(사용자가 못 찾아 헤맸음, 처음부터 위치를 말해 줄 것).
2. J9에서 확인한 것: fetch 후 `↓1↑1`의 의미(추적 중인 upstream 대비), Commits `4`는 **현재 브랜치 조상만** 보이고 전체 갈라짐은 Status `1`→`a`,
   `f`(ff)는 갈라지면 막힘. 사용자 질문 "브랜치 그래프 볼 일이 있나" → 평소엔 Branches의 `↑↓` 숫자면 충분, `↓↑` 둘 다 양수일 때만 전체 그래프를 연다고 답함.
3. J9 전 상황 질문 "내 브랜치에 커밋이 있는 상태에서 develop을 rebase로 받은 적 있어요?"는 아직 답을 못 받음.
4. 미졸업 약점: 부분 unstage 경로(`Enter`→`Tab`→`Space`) — 사용자가 복습 제외 요청, 필요해질 때만.

### J9 되돌리기 (튜터가 Git Bash로 실행, 연습 저장소 전용 — 공유/실제 저장소에는 쓰지 않는다)
`b`(`76f0728`)는 건드리지 않는다. lazygit이 켜져 있으면 닫고 한다. 임시 복사본에서 결과 확인함(`main ↑1↓1`).
```bash
cd ~/Desktop/lazygit-practice
git -C origin.git update-ref refs/heads/main 76f0728     # 원격 main을 pull 전으로
git -C a switch -q main && git -C a reset -q --hard 3777fb8   # 로컬 main을 pull 전으로
git -C a update-ref refs/remotes/origin/main 76f0728     # a가 아는 origin/main도 맞춤
git -C a branch -vv                                      # main [origin/main: ahead 1, behind 1] 여야 함
```
기준 해시: `main` `3777fb8`, `origin/main` `76f0728`, `feature` `396ddb1`, `init` `edc2459`. merge 커밋 `6a03f26`은 되돌린 뒤 reflog에만 남는다.

- 2026-11-02 (Windows): J9 복습 — ↑1↓1은 로컬·원격 각각 고유 커밋 1개라는 설명 정답. 갈라진 상태에서 fast-forward 불가 정답. 실습 a는 main...origin/main 동일 상태, 작업 트리 깨끗함. 되돌리기 미실행.
- 2026-11-02 이력 재확인: a reflog에 6a03f26 pull --no-edit merge 기록, bare 원격 main도 6a03f26 확인. 이전 p→P 실습 완료가 실제 이력과 일치함. 재실습을 필수처럼 안내한 것은 정정. 다음은 merge 결과 확인 후 원격 변경을 rebase로 받는 방식 비교(미실습). 저장소 복원은 아직 하지 않음.
- 2026-11-02 J9 rebase 비교 준비 완료: 사용자 lazygit 꺼짐 확인 후 b를 ff로 갱신, 원격 커밋 42e68a4와 a 미공개 로컬 커밋 dd323b1 생성. a main ↑1↓1, 공통 부모 6a03f26, 작업 트리 깨끗함. 과거 이력 reset 없이 새 상황 구성. rebase 전 시작 tip dd323b1. 다음: a에서 lazygit 열기 → 1,a 그래프 확인 → 원격 origin/main 대상 rebase. 진행 중 탈출은 m→a.
- 2026-11-02 사용자 요청: b에서 develop 생성, develop-notice.txt 커밋 후 실습 bare 원격에 push, a fetch 완료. a의 checkout 및 upstream 변경 없음. 다음 실습 후보: upstream이 아닌 origin/develop을 직접 선택해 현재 브랜치에 반영.
- 2026-11-02 J9/J10 rebase 실습 성공 확인: feature checkout → 원격 origin/develop 선택 → r → s. reflog finish 확인, 충돌 없음·작업 트리 깨끗함. origin/develop 45dec35 뒤에 feature 커밋 4843e71(모카), 00f62be(WIP)가 재작성됨(이전 58a9bb6,396ddb1). push 미실행. upstream 아닌 원격 브랜치 직접 지정, fetch+rebase와 pull rebase 관계 설명. 다음: 사용자에게 전후 해시 및 HEAD 위치 읽기 확인. J9 원래 main의 dd323b1 rebase는 실행하지 않음.
- 2026-11-02 J10 기본 rebase 실습 완료 및 사용자 이해 확인: feature에 origin/develop 반영, before/after 그래프로 merge와 rebase 차이 설명. p는 upstream, 명시적 pull origin develop은 현재 feature에 develop 반영이며 upstream 연결 변경 없음 이해. J9 upstream 아닌 대상 지정·merge/rebase 선택 개념 확인. J9 원래 main 재실습은 미실행, J10 abort 실습은 J12에 남음. 다음 단계는 J11 cherry-pick: 다른 브랜치에서 필요한 커밋 하나만 가져오기.
- 2026-11-02 J11 실습 준비: b develop에 fix: login timeout(login-fix.txt), feat: unrelated feature(new-feature.txt) 두 독립 커밋 생성·실습 원격 push·a fetch 완료. a feature 작업 트리 깨끗함. 목표는 origin/develop의 login timeout 커밋만 C로 복사 후 4,V로 적용. 아직 cherry-pick 미실행. 복구 경로 진행 중 m→a, 시작 feature tip 00f62be.
- 2026-11-02 J11 cherry-pick 실습 성공 확인: feature HEAD 66f059b fix: login timeout, reflog cherry-pick 확인. 원본 develop 6cfd16f와 다른 해시의 새 커밋 생성. login-fix.txt 포함, unrelated feature의 new-feature.txt 없음. 작업 트리 깨끗함, push 미실행. C→4→V 결과 확인 완료, 복습 퀴즈는 아직.
- 2026-11-02 J11 퀴즈 정답: cherry-pick 후 원본 develop 커밋은 그대로 남는다고 답함. J11 기본 실습·개념 확인 완료. 다음은 J12 충돌: abort로 원상복귀 → 재시도 → 해결 → continue.
- 2026-11-02 J12 준비: a feature develop-notice.txt를 notice_mode=local로 커밋, b develop 동일 줄을 notice_mode=team으로 커밋·push, a fetch 완료. 두 작업 트리 깨끗한 상태에서 시작. 목표는 merge 충돌 → m,a abort → 재시도 → team 값만 채택 → continue. merge는 아직 미실행. 양쪽 모두 담기는 이 설정값 충돌의 정답 아님.
- 2026-11-02 J12 실제 상태 확인: 사용자 merge 충돌 해결 및 완료, feature HEAD a0d075f Merge remote-tracking branch origin/develop into feature. develop-notice.txt는 notice_mode=team만 남음, 작업 트리 clean. 충돌 해결·merge 완료 성공. abort 연습은 미확인/미실행으로 남김. 앞으로 확인 가능한 상태는 사용자에게 재질문하지 말고 직접 조회.
- 2026-11-02 J13 사용자 명시 요청으로 lazygit config.yml에 allBranchesLogCmds 4개 등록: 전체 oneline / simplify-by-decoration / main first-parent / 전체 medium. 기존 파일 비어 있음 확인 후 작성. 실제 화면 비교는 다음. 설정 경로 C:/Users/SSAFY/AppData/Local/lazygit/config.yml.
- 검증 정정: lazygit --config는 기본 설정 출력이며 사용자 설정 읽기 검증이 아님. 이후 사용자 화면에서 등록한 그래프 보기 확인.
- 2026-11-02 요청으로 a/.git/lazygit.yml 생성: 기존 그래프 4개 유지 + 5번 HEAD...origin/develop --left-right 추가. 명령 실행 검증: feature 쪽 5개, develop 쪽 고유 커밋 없음(이미 merge 완료). 전역 설정 변경 없음. 재시작 후 1,a 순환으로 화면 확인 필요.
- 2026-11-02 abort 실습 준비: a feature는 notice_mode=local-abort, b develop은 notice_mode=team-abort로 각각 커밋. b push 및 a fetch 완료 후 사용자가 merge 충돌과 abort 실습 진행.
- 2026-11-02 J12 abort 실습 완료: Auto-merge failed 창에서 a로 취소. 직접 검증: feature HEAD 115985f 유지, develop-notice.txt=notice_mode=local-abort 복원, MERGE_HEAD 없음, 작업 트리 clean. git merge --abort와 동일 동작 이해. J12 충돌 해결·merge 완료 및 abort 실습 모두 완료. J13 그래프 위치·부모·보기 설정 및 차이 보기 학습 완료, 독립 그래프 판독 퀴즈는 미완료. 다음은 실제 작업 적용 또는 필요시 그래프 판독 복습.

## 다음 세션 기준 (2026-11-02 갱신)
- J9 원격 대상 지정·upstream·merge/rebase 차이 이해 확인. main 재실습은 반복하지 않아도 됨.
- J10·J11·J12 주요 실습 완료. J13은 보기 설정과 설명까지 진행, 독립 판독 확인만 남음.
- 선택할 다음 학습: J7 삭제·순서 변경 실습(당시 건너뜀) 또는 J13 그래프 판독 확인.
- 위의 이전 다음 단계와 되돌리기 절차는 과거 기록이며 현재 실행 지시가 아님.
