# C2. 게시 경계: 이미지를 올릴 수 있는 곳

지금 하는 일: PR이 통과해 `main`에 합쳐진 뒤, 이미지를 레지스트리에 올리는 단계를 봅니다. 이미지를 올리는 권한을 누가 어떻게 얻는지가 주제입니다.

## 상황 1: 워크플로 파일은 PR이 고칠 수 있다

GitHub Actions의 워크플로 파일은 저장소 안의 평범한 파일(`.github/workflows/*.yml`)입니다. 같은 저장소의 branch에서 PR을 올리면 GitHub은 그 PR 쪽 버전의 파일로 워크플로를 돌립니다. 포크에서 온 PR은 시크릿을 받지 못하지만, 같은 저장소 branch에서 온 PR은 받을 수 있습니다.

혼자 쓰는 저장소라서 같은 저장소 branch는 전부 사용자님이 만들 것 같지만, branch를 만들 수 있는 주체는 더 있습니다. AI 에이전트에게 쥐여 준 토큰, 의존성 갱신 봇(Dependabot), 유출된 개인 토큰이 그렇습니다. 이 중 하나가 PR에서 워크플로 파일에 `permissions: packages: write`와 이미지 게시 단계를 추가하면, PR 검사가 도는 동안 자기 이미지가 `ghcr.io/kanggihoo/ci-cd-lab/be`에 올라갑니다.

## 막는 장치 1

이미지 게시는 `main`에 push될 때만 도는 별도 워크플로 파일에서만 합니다. PR 검사 파일에는 게시 단계와 쓰기 권한이 없습니다. 여기에 세 가지를 더합니다.

- 저장소 기본 토큰 권한을 read로 낮춥니다.
- Environment가 배포를 허용하는 branch를 `main` 하나로 제한합니다.
- `pull_request_target`, `workflow_run`, `issue_comment` 이벤트로 시크릿이나 쓰기 권한이 있는 잡을 돌리지 않습니다. 이 이벤트들은 PR이 직접 코드를 돌리지 못하는 대신, PR이 만든 결과를 특권이 있는 쪽에서 실행하게 만드는 통로가 되기 때문입니다.

`actions/checkout`에는 `persist-credentials: false`를 씁니다. 기본값이면 checkout이 토큰을 `.git/config`에 남기고, 그 폴더를 artifact로 올릴 때 토큰이 같이 올라갈 수 있습니다.

## 상황 2: 태그는 이름표다

`sha-<커밋>` 태그는 이미지에 붙은 이름표입니다. 레지스트리에 올릴 권한이 있으면 같은 이름표를 다른 이미지에 붙일 수 있습니다. 같은 커밋의 빌드를 재실행해도 결과물이 비트 단위로 같지 않으면, 같은 이름표에 다른 이미지가 올라갑니다.

GHCR이 태그를 덮어쓰지 못하게 보장하는지는 문서에서 찾지 못했습니다. 확인하지 못했으므로 보장이 없다고 가정합니다.

## 막는 장치 2

게시 단계가 시작할 때 그 태그가 이미 있는지 확인하고, 있으면 실패합니다. 배포와 복구는 태그를 쓰지 않고 digest만 씁니다. digest는 이미지 내용에서 계산한 지문이라 내용이 하나라도 달라지면 값이 달라집니다. 그래서 "정확히 이 이미지"를 가리킵니다.

## 그래도 남는 구멍

`main`에 악성 코드가 병합되면 이 경계는 그것을 정상 이미지로 게시합니다. 이 경계가 지키는 것은 "`main`을 거치지 않은 게시"입니다. `main`에 들어오는 코드의 품질은 C1의 `gate`와 D-6의 스캔이 맡습니다.

SHA 고정은 워크플로가 부르는 액션을 고정할 뿐입니다. 이미지를 빌드하는 중에 내려받는 npm이나 Go 패키지의 내용은 보증하지 않습니다.

## 직접 해보기

로컬에서 같은 태그에 다른 이미지를 두 번 만들어 봅니다.

```
mkdir -p ~/Desktop/cicd-practice/tag && cd ~/Desktop/cicd-practice/tag
printf 'FROM alpine\nRUN echo v1 > /v\n' > Dockerfile
docker build -q -t demo:1 .
printf 'FROM alpine\nRUN echo EVIL > /v\n' > Dockerfile
docker build -q -t demo:1 .
```

`-q`가 이미지 ID(`sha256:…`)를 출력합니다. 둘 다 `demo:1`인데 값이 다릅니다. 로컬의 이미지 ID와 레지스트리의 digest는 계산하는 대상이 조금 다르지만, 내용이 바뀌면 값이 바뀐다는 성질은 같습니다.

## 확인 질문

`ghcr.io/kanggihoo/ci-cd-lab/be:sha-abc1234`로 배포하는 방식과 `be@sha256:…`로 배포하는 방식은, 누군가 이미지를 바꿔치기하려 할 때 어떻게 다른가요?

## 결정 로그

D-8, D-9, D-14의 (1)과 (4).
