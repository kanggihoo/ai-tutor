
asdsd
# LazyVim 실습실 — 작은 카페의 하루

파일 찾기, 전체 검색, 버퍼 전환, 창 분할을 실제 프로젝트에서 연습합니다.
프로젝트는 연습용 자료이며 설치나 실행이 필요하지 않습니다.

## 실습 이어가기

사용자는 대화로 한 문제씩 안내받으며 실습합니다. 다음 세션 담당자는 [HANDOFF.md](HANDOFF.md)의 다음 시작점을 확인하세요. 진행 요약은 [PROGRESS.md](PROGRESS.md), 복습 키와 풀이는 [ANSWERS.md](ANSWERS.md), 전체 초기 계획은 [MISSIONS.md](MISSIONS.md)에 있습니다.

## 시작하기

터미널에서 이 폴더를 작업 디렉터리로 열어 주세요. 아래는 셸 명령이며 nvim 안의 명령이 아닙니다.

PowerShell:

    cd ~/Desktop/lazyvim-practice
    nvim README.md

WSL에서 Windows 바탕화면 자료를 열 경우:

    cd /mnt/c/Users/SSAFY/Desktop/lazyvim-practice
    nvim README.md

Linux 홈의 Desktop에 자료를 복사했다면 그 경로로 이동하세요.

이후 실습에서는 콜론 명령과 마우스를 쓰지 않습니다.
일반 모드에서 Space를 누르고 잠깐 기다리면 키 안내가 나옵니다.
키 안내에서 파일 찾기를 찾아 MISSIONS.md를 열어 시작하세요.
막히면 HINTS.md → ANSWERS.md 순서로 확인하세요.

## 읽는 순서

- MISSIONS.md: 목표와 성공 조건. 하루 3문제씩 권장.
- HINTS.md: 찾아야 할 메뉴 이름만 안내.
- ANSWERS.md: 실제 키 조합과 풀이.
- PROGRESS.md: 성공 여부와 사용한 키를 기록.
- src/: 카페 설정과 주문 코드.
- docs/: 카페 운영 문서.

## 규칙

- Esc로 일반 모드에 돌아온 다음 단축키를 누르세요.
- Space f f는 동시에 누르지 않고 Space → f → f 순서로 누릅니다.
- Ctrl+h는 Ctrl을 누른 채 h를 누릅니다.
- 처음에는 키 안내를 봐도 됩니다. 두 번째에는 기억해서 해보세요.
- 문제마다 성공 조건을 확인하세요. 속도나 최소 타수보다 완주가 먼저입니다.
- 아직 배우지 않은 텍스트 편집은 방향키와 i, Esc를 써도 됩니다.
- 수정 미션은 원본 값을 안내하므로 직접 복원하며 반복할 수 있습니다.

## 환경이 다를 때

기본 Space 리더 키를 사용하는 LazyVim 기준입니다. 개인 키 설정이 있으면 화면의 키 안내가 우선입니다.
파일 찾기/검색에 다른 프로젝트가 나오면 cwd 버전의 메뉴를 사용하세요. ANSWERS.md 앞부분에 안내가 있습니다.
문제와 정답도 검색되므로 실제 조사 결과는 src/ 또는 docs/ 경로의 파일에서 확인하세요.
코드 정의 이동과 진단은 언어 서버가 필요한 보너스로만 제공합니다.
파일 검색이 비거나 오류가 나면 검색창을 닫고 안내 메시지를 확인하세요. grep 기능은 ripgrep(rg)이 필요합니다.

단축키 참고: https://www.lazyvim.org/keymaps
확인일: 2026-10-23
