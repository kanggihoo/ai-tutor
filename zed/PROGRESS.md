# 진행 현황 (튜터가 매 과제/퀴즈 후 갱신)

튜터 규칙·레슨 구성은 [AGENTS.md](AGENTS.md)를 보세요.
지금까지 나온 단축키는 [keymap.md](keymap.md)에 정리했습니다.

## 프로필
- 목표: Zed에 빠르게 익숙해지기. 용도 무관, 어디서든 사용(2026-10-30).
- Zed 내장 AI는 안 씀 → Claude Code·Codex를 쓴다. AI 기능은 커리큘럼에서 뺌.
- LazyVim 학습 중(`../nvim/PROGRESS.md`), lazygit 학습 중(`../git/PROGRESS.md`). Zed는 vim 모드 → vim 기본기는 생략.
- 선호(다른 과목에서 확인): 세션당 20~30분, 한 문제씩, 쉬운 건 빠르게, "이걸 쓸 일이 있나" → 쓰임새 한 줄.
- 참고 문서: `https://zed.dev/docs/llms.txt` (공식 문서 색인).

## 커리큘럼
| # | 레슨 | 상태 | 메모 |
|---|------|------|------|
| Z1 | 열기·명령 팔레트·파일 찾기 | ✅ (퀴즈 3문항 전부 패스) `zed .` 실행 확인(창 앞으로 가져옴). 과제2 팔레트 `toggle left dock` 사용자 "확인했어"(단축키 답은 미수신, 정답 `Cmd+B`). 과제3 `] b`/`[ b` 사용자 확인("LazyVim과 동일"), `Ctrl+1~9` 탭 번호 이동 안내(LazyVim엔 기본 매핑 없음, 소스 grep 확인). Zed 용어(window/pane/tab/dock) 설명. 과제4 `:ls` 사용자 "오케이". `Space Space` 원함 → keymap.json 스니펫 안내 → 사용자가 Z7로 미룸 | |
| Z2 | 패널·탭·분할 | ✅ 과제1 분할 사용자 "오케이"(`Ctrl+w o` 후 탭 남는지 답 미수신). LazyVim과 분할 키 차이 설명. 과제2 프로젝트 패널(`%`·`d`·`Shift+R`·`Shift+D`, LazyVim `d`=삭제와 반대) **설명만**, 사용자 건너뜀(파일 생성 없음 확인). 과제3 `Cmd+W`·`Alt+Cmd+T`·`Cmd+Shift+T`·`Cmd+J` 안내, 사용자 "다음" | |
| Z3 | 코드 탐색 (LSP) | ✅ (퀴즈 미실시) 과제1 에러 수정 확인(22행 `total(&mocha, 3)`, cargo run 합계 24000). 저장 시 rustfmt가 구조체 리터럴을 여러 줄로 바꿈(format on save). 과제2 확인: `g r n`으로 `price_of` 5곳(정의1+호출4) 변경, 빌드 통과(처음엔 저장 안 함 → `:w` 후 확인). LazyVim 호환 키 비교 설명(LazyVim `gr`은 nowait라 `grn`/`grr` 못 씀, 소스 확인). 과제3 `g s` 설명(LazyVim `Space s s`는 LSP 붙은 버퍼에서만 보임), `g .`→Generate `new`로 `impl Cafe { fn new }` 생성 확인(미사용 경고) | `zed/practice/`(cargo new). 시작 상태: `src/main.rs` 16행(포맷 후 22행) `total(&mocha, "3")` E0308 일부러 넣음, 구조체 `Cafe`·함수 `total` 3회 호출 |
| Z4 | 멀티커서·전체 검색·멀티버퍼 | ✅ 과제1 `g a`→`c`로 `mocha`→`tea` 5곳(변수4+문자열1) 확인, 빌드 통과. 과제2 `g l`/`g >` **설명만**(사용자 건너뜀, 파일 미변경 확인). 프로젝트 열기·폴더 추가·`Cmd+Shift+E`/`Esc` 패널 이동 설명. 과제3 `g /` 멀티버퍼에서 `menu.md`만 `latte`→`coffee` 2곳 확인, `main.rs` 그대로 | |
| Z5 | 터미널·tasks | ⏭ 터미널은 `:te`만 알기로, task(`Cmd+Shift+R`/`Cmd+Alt+R`)는 설명만 — 사용자: 쓸 일 적음 | |
| Z6 | git | ⏭ 사용자 요청으로 생략 | AI가 커밋까지 하므로 변경 탐색·stage·커밋 실습 불필요(2026-11-02). 실습 변경은 그대로 보존. 이전 실습 저장소 init `269878d` |
| Z7 | 설정·키맵·확장 | 🔄 일부 설정만 진행 | Mac과 Windows에 LazyVim 공통 키 등록. Windows 동작 확인 대기. 확장 확인은 미진행 |
| Z8 | 원격 개발 (선택) | ⬜ | 쓸 서버가 있을 때만 |

## 약점 (Weak spots)
- 미확인(Z1 퀴즈 패스): 명령 팔레트 `Cmd+Shift+P`, 다음 탭 `] b`, 분할 영역 이름 pane. 복습 퀴즈에 넣는다.
- 설명만(Z2): 프로젝트 패널 새 파일 `%`, 새 폴더 `d`(LazyVim은 `d`=삭제).
- 설명만(Z4): `g l` 하나 추가, `g >` 건너뛰기.

## 세션 로그
- 2026-11-03: Windows 프로젝트 패널에 LazyVim 대응 `o` 시스템 앱 열기, `y` 경로 복사, `a` 생성, `r` 이름 변경, `d` 확인 후 휴지통 이동 등록. 기존 키맵 백업·JSON 검증 완료, 실제 화면 동작 확인 대기.
- 2026-11-03: Windows에서 프로젝트 전체 심볼 검색 `Space s S`를 Vim 편집기 및 편집기·터미널·메뉴 밖에 추가. 백업·JSON 검증 완료, 화면 동작 확인 대기. 분할 pane 크기 조절 기본 키 안내.
- 2026-11-03: 사용자 확인으로 빈 화면 `Space Space` 동작 확인. 요청에 따라 같은 문맥에 `Space e` 추가, 백업·JSON 검증 완료. 실제 동작 확인 대기.
- 2026-11-03: 빈 화면에서 `Space Space`가 동작하지 않는다는 사용자 보고로 편집기·터미널·메뉴 밖 문맥에 파일 찾기 매핑 추가. 설정 백업·JSON 검증 완료, 실제 동작 확인 대기.
- 2026-11-03: Windows 키맵을 백업하고 Mac 기록에 맞춰 단독 `Space` 해제, `Ctrl+h/j/k/l` pane 이동, `Space |`/`Space -` 분할 추가. 기존 세 Space 매핑과 which-key 설정 유지. 파일 검증 완료, 화면 동작 확인 대기.
- 2026-11-02: 사용자 '했어'로 `Cmd+,` 설정 화면 열기 확인 완료. `Space /` 검색창 동작은 별도 확인 미수신. 다음 Z7 과제: 확장 화면에서 설치된 언어 지원 확인.
- 2026-11-02: 사용자 '반영' 요청으로 Mac 키맵 백업 후 기존 일반 모드 문맥에 `Space /` → `pane::DeploySearch` 추가. 기존 매핑 보존, 파일 등록 확인. 검색창 동작 확인 대기.
- 2026-11-02: 사용자 '확인했어'로 단독 Space 해제 후 which-key 안내 유지 동작 확인 완료. 다음 Z7 과제: LazyVim과 같은 `Space /` 프로젝트 전체 검색 등록.
- 2026-11-02: 사용자 요청: LazyVim처럼 Space 안내를 다음 키 선택까지 유지. v1.26.2 `space` → `vim::WrappingRight` 기본 단독 매핑 확인. Mac 키맵 백업 후 기존 일반 모드 문맥에 `"space": null` 추가해 단독 동작 해제, 조합 키 보존. which-key 지연 300ms 유지. 실제 팝업 유지 여부는 사용자 확인 대기.
- 2026-11-02: 사용자 요청으로 Mac 키맵 백업 후 기존 일반 모드 문맥에 `Space e` → `project_panel::ToggleFocus` 추가. 기본 키 `Cmd+Shift+E`, dock 토글 `Cmd+B` 설명. 파일 등록 확인, 동작 확인 대기.
- 2026-11-02: 사용자 명시 요청으로 Mac `~/.config/zed/keymap.json` 백업 후 기존 `Space Space`와 같은 일반 모드 문맥에 `Ctrl+h/j/k/l` pane 이동, `Space |` 좌우 분할, `Space -` 위아래 분할 추가. v1.26.2 기본 키맵에서 분할 action 확인. 파일 등록 확인, 화면 동작 확인 대기.
- 2026-11-02: Z7 Mac `Space Space` 파일 찾기 등록 방법 안내, 사용자 동작 확인은 미수신. 키맵 목록의 `Space f`는 `!Editor && !Terminal` 또는 Helix 전용 문맥임을 설명. 사용자 '다음'으로 pane 이동 `Ctrl+h/l` 등록 안내로 진행.
- 2026-11-02: 사용자 요청으로 설명 원칙 변경: LazyVim과 공통으로 쓰는 키·명령 우선, 공통 키가 없으면 차이부터 설명. 목적·동작을 설명한 뒤 입력 안내. Z6 diff 펼치기는 사용자 결과 확인 전으로 완료 처리하지 않음.
- 2026-11-02: 사용자 요청으로 `keymap.md`에 기존 학습 기록의 단축키를 정리. Mac 기본 키·Windows 사용자 키맵·미적용 후보·설명만인 항목을 구분함. 명령 팔레트 복습은 미응답 상태로 유지.
- 2026-11-02: Mac 세션 Z6 재개 전 복습. 다음 탭 키를 처음에는 모름 → `]`와 buffer 힌트 후 `]b` 정답. 힌트 없는 정답 횟수는 올리지 않음, 약점 유지.
- 2026-11-02: Windows `C:\Users\SSAFY\Desktop\ai-tutor\zed\practice`가 없음을 확인. 사용자 요청: Windows 실습은 pass, 다음 Mac 세션에서 Z6 과제1부터 재개. 실습 폴더를 새로 만들거나 Git 실습을 수행하지 않음. Java 확장·JDK 요구사항과 Windows pane 확대 `Shift+Esc`는 설명만(설치·동작 미확인). 다음 탭 복습 문제는 미응답으로 정답 횟수 변경 없음.
- 2026-11-02: 사용자 요청으로 Windows `%APPDATA%/Zed/settings.json`에 `which_key: {enabled: true, delay_ms: 300}` 추가, 기존 설정 백업·보존 확인. 새 `keymap.json`에 `VimControl && !menu` 문맥으로 `Space Space` 파일 찾기, `Space e` 프로젝트 패널, `Space /` 전체 검색 등록(JSON 검증). 팝업 표시·동작은 사용자 확인 대기.
- 2026-11-02: Windows 사용 확인. 설치된 Zed 1.26.2, 사용자 설정 `vim_mode: true`, `base_keymap: VSCode`, `disable_ai: true` 확인. Z6 재개 전 복습 시작.
- 2026-10-30: 과목 생성. Mac Zed 1.26.2 설정 확인, v1.26.2 키맵으로 레슨 키 확인.

## 다음 단계
**Z7 진행: LazyVim 공통 키를 Mac Zed에 등록하는 실습.** Mac `keymap.json`은 주석만 있고 사용자 매핑 없음 확인(2026-11-02). 사용자가 직접 편집하고 동작을 확인한다. 아래 Z6 절차는 생략 결정 이전 기록이며 재개하지 않는다.
1. Mac 저장소 위치를 확인해 `zed/practice/`의 실제 절대 경로를 안내한다. Windows 경로를 사용하거나 Mac 경로를 추측하지 않는다. `.git`·`git status`·diff를 읽어 실습 상태부터 확인한다(기록상 init `269878d`, `main.rs` latte 4500→4800, `menu.md` mocha 줄 추가). 폴더가 없으면 그때 최소 실습 환경을 준비한다.
2. 설치된 Mac Zed 버전과 해당 키맵을 확인한 뒤, Z6 과제1을 하나씩 진행: `] c` hunk 이동 → `d o` diff 보기 → `d p`로 main.rs 변경 되돌리기 → Git 패널에서 menu.md만 stage → 커밋. 위 키와 패널·커밋 키는 실습 직전 재검증한다. 아직 아무 단계도 완료 처리하지 않는다.
3. 결과는 main.rs·menu.md 양쪽 diff와 stage 상태·커밋으로 확인하고 매 과제 후 기록한다.
which-key: Mac은 사용자 요청으로 튜터가 `~/.config/zed/settings.json`에 `which_key: {enabled: true, delay_ms: 300}` 추가한 기록 있음(2026-11-01), 팝업 표시 확인 대기. Windows Space 키맵은 Mac에 자동 적용되지 않으므로 혼동하지 않는다.
Z7 후보(사용자 미결정): `jk`→Esc, `default_mode: insert`, `Ctrl+S` 저장. 입력 진입은 `ciw`/`ci"`/`A`/`o` 권장 설명함.
