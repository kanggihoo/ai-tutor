# C5. dev는 정말 비공개인가

지금 하는 일: `lab-dev`와 `lab-prod`가 한 VPS에서 돌 때, dev를 tailnet 안에서만 보이게 하려면 무엇을 해야 하는지 봅니다.

## 상황

서버에 ufw가 켜져 있고 8080 포트를 막아 놨으니 dev는 인터넷에서 안 보일 것이라고 생각하기 쉽습니다. 그런데 compose에 `ports: "8080:80"`을 쓰면 Docker가 컨테이너 포트를 열면서 방화벽 규칙(iptables)을 직접 추가합니다. 이 규칙은 ufw가 관리하는 규칙보다 먼저 적용되어서, ufw에서 막아 둬도 8080이 인터넷에서 열립니다.

`vps-infra`의 `okf/architecture/a302-adoption-candidates.md`에도 "Docker가 게시한 포트는 ufw를 우회한다"고 적혀 있습니다.

## 막는 장치

`ports`를 `"127.0.0.1:8080:80"`처럼 주소와 함께 씁니다. 그러면 그 포트는 서버 자기 자신에서만 열립니다. 바깥에서 오는 요청은 서버의 nginx나 내부 Caddy가 받아서 전달합니다. dev를 tailnet에서 보려면 포트를 tailnet IP에 바인딩하거나, 호스트의 프록시가 tailnet 쪽 주소에서만 받도록 합니다.

인수 기준은 "공개 인터넷에서 dev가 열리지 않는다"입니다. 서버 밖(예: 모바일 데이터에 연결한 휴대폰)에서 실제로 접속을 시도해서 확인합니다.

## 그래도 남는 구멍

dev와 prod는 별도 OS 사용자, 별도 Docker 네트워크, `mem_limit`으로 나뉘지만 커널과 Docker 데몬은 같습니다. dev 컨테이너에서 탈출하거나 docker 권한을 얻으면 prod까지 거리가 짧습니다. 그래서 환경별 SSH 키와 root 소유 고정 compose가 필요합니다(ADR 0002).

같은 서버에 있는 Jenkins는 `docker.sock`을 마운트하고 GitHub PAT와 SOPS 키를 갖고 있어서(`jenkins/compose.yml`), Jenkins가 침해되면 lab의 두 환경도 같이 무너집니다. 이 위험은 lab이 만든 것이 아니고 기존 서버에 있던 것입니다. Jenkins를 폐기하는 단계(D-22)까지 남는 위험으로 둡니다.

## 직접 해보기

로컬 Docker로 바인딩 주소의 차이만 봅니다. Mac에는 ufw가 없어서 우회 자체는 재현되지 않습니다.

```
docker run -d --name a -p 8080:80 nginx
docker run -d --name b -p 127.0.0.1:8081:80 nginx
docker ps --format '{{.Names}} {{.Ports}}'
docker rm -f a b
```

`a`는 `0.0.0.0:8080->80/tcp`(모든 주소), `b`는 `127.0.0.1:8081->80/tcp`(자기 자신만)로 보입니다.

## 확인 질문

ufw에서 8080을 막았는데도 compose의 `"8080:80"`이 인터넷에서 열리는 이유를, Docker가 하는 일을 중심으로 설명해 보세요.

## 결정 로그

D-19, D-21, ADR 0002.
