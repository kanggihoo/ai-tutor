# 정답과 풀이

Space = 기본 leader. 표의 키는 일반 모드에서 순서대로 누릅니다.
Ctrl 조합만 동시에 누릅니다. |는 보통 Shift+역슬래시로 입력합니다.
사용자 설정과 플러그인에 따라 화면의 키 안내가 다르면 그 안내를 따르세요.

## 검색 범위부터 확인
Space f f / Space / 는 프로젝트 루트 기준입니다.
다른 폴더가 보이면 Space f F / Space s G로 현재 작업 디렉터리(cwd)를 사용하세요.
시작할 때 터미널에서 이 실습 폴더로 이동한 뒤 nvim을 열어야 cwd가 맞습니다.

## 01. 파일 찾기
Space f f → config.js 입력 → 결과 선택 → Enter.
대안: Space를 두 번 누르기.
초기 배송비 3000, 무료배송 기준 20000입니다.

## 02. 전체 검색
Space / → COUPON_EXPIRED 입력 → src/services/orders.js 결과 선택 → Enter.
대안: Space s g.
validateCoupon 함수에서 expired가 참이면 해당 문자열을 반환합니다.
학습 문서에도 검색어가 있으므로 실제 코드 경로를 선택하세요.

## 03. 탐색기
Space e → docs 선택 → Enter로 펼치기 → shipping.md → Enter.
Space e로 다시 토글할 수 있습니다. 제주 추가 배송비는 3000원입니다.
Snacks/Neo-tree 등 탐색기마다 상세 동작은 다를 수 있습니다.

## 04. 버퍼
파일은 Space f f로 차례로 엽니다.
Space b b: 직전에 사용한 버퍼로 이동.
Space ,: 열린 버퍼 목록. main.js를 선택하고 Enter.
Space b d: 현재 버퍼 닫기. 디스크의 파일을 지우는 기능은 아닙니다.
Shift+h / Shift+l로 이전/다음 버퍼로 이동할 수도 있습니다.

## 05. 좌우 창
config.js → Space | → 오른쪽 창에서 Space f f → shipping.md.
Ctrl+h: 왼쪽 창. Ctrl+l: 오른쪽 창.
오른쪽 창에서 Space w d: 해당 창만 닫기.
초기 문서와 설정 모두 배송비 3000, 무료배송 기준 20000입니다.

## 06. 위아래 창과 확대
Space -: 아래로 분할.
Ctrl+j: 아래 창. Ctrl+k: 위 창.
Space w m: 현재 창 확대/복원. 두 번 실행하면 원래 배치로 돌아옵니다.
아래 창에서 Space w d로 닫습니다.

## 07. 수정, 저장, 실행 취소
storeName의 문자열 위로 이동 → i로 입력 모드 → 수정 → Esc.
Ctrl+s: 저장. u: 실행 취소. Ctrl+r: 재실행. Ctrl+s로 최종 저장.
실행 취소는 편집 단위로 적용되므로 한 번으로 안 돌아오면 내용을 보며 반복하세요.
문자열 안에 커서가 있다면 ci" → My Cafe 입력 → Esc로 한 번에 바꿀 수도 있습니다.
Ctrl+s가 터미널에 가로채이면 Space를 눌러 키 안내에서 저장 기능을 찾아보세요.

## 08. 주석
대상 console.log 줄에서 g c c로 줄 주석 토글. 다시 g c c로 해제.
각 상태에서 Ctrl+s로 저장하세요.
현재 줄 주석은 기본 Vim/Neovim 계열 조작이며 Space로 시작하지 않습니다.

## 09. 현재 파일 줄 검색
faq.md를 연 상태에서 Space s b → 환불 입력 → 해당 결과에서 Enter.
대안으로 /환불 → Enter → n 또는 N도 가능하며 콜론 명령은 아닙니다.

## 10. 터미널
Space f t로 프로젝트 터미널 열기.
일반적인 기본 설정에서는 Ctrl+/로 토글할 수 있습니다.
터미널이 Ctrl+/를 구분하지 못하면 Esc를 두 번 눌러 터미널 일반 모드로 나온 뒤
Ctrl+h/j/k/l로 편집 창에 이동하세요. 터미널 창을 닫을 때는 Space w d를 사용할 수 있습니다.
프로세스를 실행 중인 터미널에는 닫기보다 토글을 사용하세요.

## 11. 종합 결과
- src/config.js: shippingFee: 2500
- docs/shipping.md: 기본 배송비: 2,500원
- src/data/menu.json: id가 latte인 항목의 price: 4800
파일마다 Ctrl+s로 저장. 메뉴 데이터 창에서 Space b d로 버퍼 닫기.
분할 창 닫기는 Space w d, 버퍼 닫기는 Space b d입니다.

## 12. 복습
예시 흐름: Space f f → Space / → Space | → Ctrl+h/l → Space w d → Space ,.
정해진 한 가지 풀이보다 기능을 스스로 꺼내 쓸 수 있는지가 기준입니다.

## 보너스
언어 서버가 연결되면 calculateTotal 호출에서 g d로 정의 이동, K로 설명 확인,
Ctrl+o로 이전 이동 위치로 돌아옵니다. 연결 여부는 Space c l로 확인할 수 있습니다.
언어 서버를 새로 설치하거나 설정할 필요는 없습니다.

공식 기본 키맵: https://www.lazyvim.org/keymaps (2026-10-23 확인)
