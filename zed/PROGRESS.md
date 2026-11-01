# 진행 현황 (튜터가 매 과제/퀴즈 후 갱신)

튜터 규칙·레슨 구성은 [AGENTS.md](AGENTS.md)를 보세요.

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
| Z6 | git | 🔄 | lazygit과 비교. `practice/`를 독립 git 저장소로 만듦(init 269878d, ai-tutor는 `zed/.gitignore`로 무시). 시작 변경: `main.rs` latte 4500→4800, `menu.md` mocha 줄 추가 |
| Z7 | 설정·키맵·확장 | ⬜ | 사용자가 직접 수정. **`space space` → `file_finder::Toggle` 추가하기로 함**(context `VimControl && !menu`). **LazyVim과 헷갈리는 키 전부 맞추기**: `Ctrl+h/j/k/l` pane 이동, `Space \|`/`Space -` 분할 등 |
| Z8 | 원격 개발 (선택) | ⬜ | 쓸 서버가 있을 때만 |

## 약점 (Weak spots)
- 미확인(Z1 퀴즈 패스): 명령 팔레트 `Cmd+Shift+P`, 다음 탭 `] b`, 분할 영역 이름 pane. 복습 퀴즈에 넣는다.
- 설명만(Z2): 프로젝트 패널 새 파일 `%`, 새 폴더 `d`(LazyVim은 `d`=삭제).
- 설명만(Z4): `g l` 하나 추가, `g >` 건너뛰기.

## 세션 로그
- 2026-10-30: 과목 생성. Mac Zed 1.26.2 설정 확인, v1.26.2 키맵으로 레슨 키 확인.

## 다음 단계
Z6 과제1: `] c` hunk 이동·`d o` diff 보기·`d p` 되돌리기(main.rs) → `Ctrl+Shift+G` 패널에서 `x` stage → 커밋 `Cmd+Enter`.
which-key: 사용자 요청으로 튜터가 `~/.config/zed/settings.json`에 `which_key: {enabled: true, delay_ms: 300}` 추가(2026-11-01). 팝업 뜨는지 사용자 확인 대기.
Z7 후보(사용자 미결정): `jk`→Esc, `default_mode: insert`, `Ctrl+S` 저장. 입력 진입은 `ciw`/`ci"`/`A`/`o` 권장 설명함.
