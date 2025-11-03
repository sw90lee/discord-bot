# Discord Welcome Bot 설정 및 배포 가이드

## 목차
1. [Discord 봇 생성 및 설정](#1-discord-봇-생성-및-설정)
2. [로컬 환경에서 테스트](#2-로컬-환경에서-테스트)
3. [Docker 이미지 빌드](#3-docker-이미지-빌드)
4. [Kubernetes에 배포](#4-kubernetes에-배포)
5. [봇 명령어 사용법](#5-봇-명령어-사용법)
6. [문제 해결](#6-문제-해결)

---

## 1. Discord 봇 생성 및 설정

### 1.1 Discord Developer Portal에서 애플리케이션 생성

1. [Discord Developer Portal](https://discord.com/developers/applications)에 접속합니다.
2. 우측 상단의 **"New Application"** 버튼을 클릭합니다.
3. 봇 이름을 입력하고 **"Create"**를 클릭합니다.

### 1.2 봇 생성 및 토큰 발급

1. 좌측 메뉴에서 **"Bot"**을 클릭합니다.
2. **"Add Bot"** 버튼을 클릭하고 확인합니다.
3. **"Reset Token"** 버튼을 클릭하여 봇 토큰을 생성합니다.
4. 생성된 토큰을 복사하여 안전한 곳에 보관합니다. (이 토큰은 나중에 필요합니다)

### 1.3 봇 권한 설정

1. Bot 페이지에서 아래로 스크롤하여 **"Privileged Gateway Intents"** 섹션을 찾습니다.
2. 다음 옵션들을 활성화합니다:
   - ✅ **PRESENCE INTENT**
   - ✅ **SERVER MEMBERS INTENT**
   - ✅ **MESSAGE CONTENT INTENT**
3. **"Save Changes"**를 클릭합니다.

### 1.4 봇을 서버에 초대

1. 좌측 메뉴에서 **"OAuth2"** → **"URL Generator"**를 클릭합니다.
2. **SCOPES** 섹션에서 다음을 선택합니다:
   - ✅ `bot`
3. **BOT PERMISSIONS** 섹션에서 다음 권한을 선택합니다:
   - ✅ `Send Messages` (메시지 전송)
   - ✅ `Embed Links` (임베드 링크)
   - ✅ `Attach Files` (파일 첨부)
   - ✅ `Read Message History` (메시지 기록 읽기)
   - ✅ `Use External Emojis` (외부 이모지 사용)
4. 하단에 생성된 URL을 복사하여 브라우저에 붙여넣습니다.
5. 봇을 추가할 서버를 선택하고 **"승인"**을 클릭합니다.

### 1.5 환영 채널 ID 확인

1. Discord 앱에서 **설정** → **고급** → **개발자 모드**를 활성화합니다.
2. 환영 메시지를 보낼 채널을 우클릭하고 **"ID 복사"**를 선택합니다.
3. 복사한 채널 ID를 안전한 곳에 보관합니다.

---

## 2. 로컬 환경에서 테스트

### 2.1 Python 환경 설정

```bash
# Python 3.11 이상이 설치되어 있는지 확인
python --version

# 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

### 2.2 의존성 설치

```bash
pip install -r requirements.txt
```

### 2.3 환경 변수 설정

**방법 1: .env 파일 사용 (추천)**

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 실제 값을 입력합니다:

```env
# Discord Bot Token (필수)
DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OTAuAbCdEf.GhIjKlMnOpQrStUvWxYz...

# Welcome Channel ID (선택사항)
WELCOME_CHANNEL_ID=123456789012345678
```

**방법 2: 환경 변수 직접 설정**

```bash
export DISCORD_TOKEN="your_discord_bot_token_here"
export WELCOME_CHANNEL_ID="your_welcome_channel_id_here"
```

### 2.4 봇 실행

```bash
python bot.py
```

봇이 정상적으로 실행되면 다음과 같은 메시지가 표시됩니다:
```
2025-11-04 12:00:00 - discord.client - INFO - YourBot (ID: 123456789)로 로그인했습니다.
2025-11-04 12:00:00 - __main__ - INFO - 봇이 정상적으로 시작되었습니다.
```

---

## 3. Docker 이미지 빌드

### 3.1 Docker 이미지 빌드

```bash
# 이미지 빌드
docker build -t discord-welcome-bot:latest .

# 특정 레지스트리에 푸시할 경우 태그 추가
docker tag discord-welcome-bot:latest your-registry.com/discord-welcome-bot:latest
```

### 3.2 Docker로 로컬 테스트

```bash
docker run -d \
  --name discord-bot \
  -e DISCORD_TOKEN="your_discord_bot_token_here" \
  -e WELCOME_CHANNEL_ID="your_welcome_channel_id_here" \
  discord-welcome-bot:latest

# 로그 확인
docker logs -f discord-bot

# 컨테이너 중지 및 삭제
docker stop discord-bot
docker rm discord-bot
```

### 3.3 이미지 레지스트리에 푸시

```bash
# Docker Hub에 푸시하는 경우
docker login
docker push your-dockerhub-username/discord-welcome-bot:latest

# 프라이빗 레지스트리에 푸시하는 경우
docker login your-registry.com
docker push your-registry.com/discord-welcome-bot:latest
```

---

## 4. Kubernetes에 배포

### 배포 방법 선택

Discord 봇을 Kubernetes에 배포하는 두 가지 방법이 있습니다:

- **방법 A**: Helm Chart 사용 (권장) - 간편하고 관리하기 쉬움
- **방법 B**: 직접 YAML 매니페스트 사용 - 더 세밀한 제어 가능

---

## 4-A. Helm Chart로 배포 (권장)

### 4-A.1 사전 준비

다음 도구가 설치되어 있어야 합니다:
- Kubernetes 1.19+
- Helm 3.0+
- `kubectl` CLI

```bash
# Helm 설치 확인
helm version

# kubectl 설치 확인
kubectl version --client

# 클러스터 연결 확인
kubectl cluster-info
```

### 4-A.2 values.yaml 설정

`k8s/helm-chart/values.yaml` 파일을 수정합니다:

```yaml
# 이미지 설정
image:
  repository: your-registry.com/discord-bot
  tag: "latest"

# 봇 설정 (필수)
bot:
  discordToken: "YOUR_DISCORD_BOT_TOKEN"
  welcomeChannelId: "YOUR_CHANNEL_ID"  # 선택사항
```

### 4-A.3 Helm으로 설치

```bash
# Helm Chart 디렉토리로 이동
cd k8s/helm-chart

# 설치
helm install discord-bot . -n discord-bot --create-namespace

# 또는 커맨드라인에서 값 지정
helm install discord-bot . \
  --set bot.discordToken="YOUR_TOKEN" \
  --set image.repository="your-registry.com/discord-bot" \
  -n discord-bot --create-namespace
```

### 4-A.4 배포 상태 확인

```bash
# 릴리스 확인
helm list -n discord-bot

# Pod 상태 확인
kubectl get pods -n discord-bot

# 로그 확인
kubectl logs -f deployment/discord-bot -n discord-bot
```

### 4-A.5 업그레이드

설정을 변경하고 업그레이드:

```bash
# values.yaml 수정 후
helm upgrade discord-bot . -f values.yaml -n discord-bot

# 또는 특정 값만 변경
helm upgrade discord-bot . \
  --set bot.discordToken="NEW_TOKEN" \
  -n discord-bot
```

### 4-A.6 삭제

```bash
# Helm 릴리스 삭제
helm uninstall discord-bot -n discord-bot

# 네임스페이스도 삭제
kubectl delete namespace discord-bot
```

자세한 내용은 `k8s/helm-chart/README.md`를 참고하세요.

---

## 4-B. YAML 매니페스트로 직접 배포

### 4-B.1 사전 준비

Kubernetes 클러스터가 준비되어 있어야 합니다. 다음 도구가 설치되어 있는지 확인합니다:
- `kubectl` (Kubernetes CLI)
- 클러스터에 대한 접근 권한

```bash
# kubectl 설치 확인
kubectl version --client

# 클러스터 연결 확인
kubectl cluster-info
```

### 4-B.2 네임스페이스 생성

```bash
kubectl apply -f k8s/manifests/namespace.yaml
```

### 4-B.3 Secret 생성

1. `k8s/manifests/secret.yaml.template` 파일을 복사하여 `secret.yaml`을 생성합니다:

```bash
cp k8s/manifests/secret.yaml.template k8s/manifests/secret.yaml
```

2. `k8s/manifests/secret.yaml` 파일을 편집하여 실제 값을 입력합니다:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: discord-bot-secret
  namespace: discord-bot
type: Opaque
stringData:
  DISCORD_TOKEN: "MTIzNDU2Nzg5MDEyMzQ1Njc4OTAuAbCdEf.GhIjKlMnOpQrStUvWxYz..."
  WELCOME_CHANNEL_ID: "123456789012345678"
```

3. Secret을 Kubernetes에 생성합니다:

```bash
kubectl apply -f k8s/manifests/secret.yaml
```

**보안 주의사항**: `secret.yaml` 파일은 Git에 커밋하지 마세요! (`.gitignore`에 이미 포함되어 있습니다)

### 4-B.4 Deployment 수정

`k8s/manifests/deployment.yaml` 파일에서 이미지 경로를 수정합니다:

```yaml
spec:
  containers:
  - name: bot
    image: your-registry.com/discord-welcome-bot:latest  # 실제 이미지 경로로 변경
```

### 4-B.5 ConfigMap과 PVC 생성

```bash
kubectl apply -f k8s/manifests/configmap.yaml
kubectl apply -f k8s/manifests/pvc.yaml
```

### 4-B.6 Deployment 생성

```bash
kubectl apply -f k8s/manifests/deployment.yaml
```

### 4-B.7 배포 상태 확인

```bash
# Pod 상태 확인
kubectl get pods -n discord-bot

# Pod 로그 확인
kubectl logs -f deployment/discord-welcome-bot -n discord-bot

# Deployment 상세 정보
kubectl describe deployment discord-welcome-bot -n discord-bot
```

정상적으로 배포되었다면 Pod가 `Running` 상태여야 합니다:

```
NAME                                   READY   STATUS    RESTARTS   AGE
discord-welcome-bot-xxxxxxxxxx-xxxxx   1/1     Running   0          30s
```

---

## 5. 봇 명령어 사용법

봇이 정상적으로 작동하면 Discord 서버에서 다음 명령어를 사용할 수 있습니다:

### 🎉 환영 시스템

**`/setwelcome`** - 환영 메시지 커스터마이징 (관리자)
```
/setwelcome title:"환영합니다!" description:"{mention}님 반갑습니다!"
```

**`/welcomechannel`** - 환영 채널 설정 (관리자)
```
/welcomechannel channel:#환영-채널
```

**`/welcometest`** - 환영 메시지 미리보기 (관리자)
```
/welcometest
```

### 👮 모더레이션

**`/kick`** - 멤버 추방
```
/kick member:@사용자 reason:"규칙 위반"
```

**`/ban`** - 멤버 차단
```
/ban member:@사용자 reason:"악의적 행동" delete_messages:7
```

**`/unban`** - 차단 해제
```
/unban user_id:123456789
```

**`/timeout`** - 임시 타임아웃
```
/timeout member:@사용자 minutes:60 reason:"경고"
```

**`/clear`** - 메시지 대량 삭제
```
/clear amount:50
```

**`/warn`** - 경고 부여
```
/warn member:@사용자 reason:"스팸"
```

**`/warnings`** - 경고 목록 확인
```
/warnings member:@사용자
```

### 🎭 역할 관리

**`/autorole`** - 신규 멤버 자동 역할 설정
```
/autorole role:@멤버
```

**`/role`** - 역할 부여/제거
```
/role member:@사용자 role:@역할 action:부여
```

**`/reactionrole`** - 반응 역할 설정
```
/reactionrole message_id:123456 emoji:👋 role:@역할
```

### 📊 레벨링 시스템

**`/rank`** - 내 레벨 확인
```
/rank
/rank member:@사용자  # 다른 사용자 확인
```

**`/leaderboard`** - 서버 순위표
```
/leaderboard page:1
```

**`/setlevel`** - 레벨 설정 (관리자)
```
/setlevel member:@사용자 level:10
```

### 🛠️ 유틸리티

**`/ping`** - 봇 응답 속도 확인
```
/ping
```

**`/serverinfo`** - 서버 정보
```
/serverinfo
```

**`/userinfo`** - 사용자 정보
```
/userinfo
/userinfo member:@사용자
```

**`/poll`** - 투표 생성
```
/poll question:"점심 메뉴?" option1:"치킨" option2:"피자" option3:"햄버거"
```

**`/announce`** - 공지사항 생성
```
/announce title:"중요 공지" description:"내용" color:red
```

**`/avatar`** - 아바타 확인
```
/avatar member:@사용자
```

### 📰 뉴스 자동 전송

**`/news`** - 최신 뉴스 조회
```
/news news_type:IT_뉴스 count:5
```

**`/schedulenews`** - 특정 시간에 자동 뉴스 전송 설정 (관리자)
```
/schedulenews channel:#뉴스-채널 time:09:00 news_type:구글_뉴스_한국
```

**`/stopnews`** - 뉴스 자동 전송 중지 (관리자)
```
/stopnews
```

**`/newsstatus`** - 뉴스 설정 상태 확인 (관리자)
```
/newsstatus
```

**지원하는 뉴스 종류:**
- 구글 뉴스 한국: 한국의 주요 뉴스
- 네이버 뉴스 헤드라인: 네이버 헤드라인 뉴스
- IT 뉴스: IT 및 기술 관련 뉴스
- 경제 뉴스: 경제 관련 뉴스

### 📈 주식 시장 정보

**`/stocks`** - 주식 시장 현황 조회
```
/stocks index1:코스피 index2:나스닥 index3:비트코인
```

**`/schedulestocks`** - 특정 시간에 자동 주식 정보 전송 설정 (관리자)
```
/schedulestocks channel:#주식-채널 time:09:00 indices:코스피,코스닥,나스닥
```

**`/stopstocks`** - 주식 자동 전송 중지 (관리자)
```
/stopstocks
```

**`/stocksstatus`** - 주식 설정 상태 확인 (관리자)
```
/stocksstatus
```

**지원하는 지표:**
- 코스피 (^KS11): 한국 종합주가지수
- 코스닥 (^KQ11): 한국 코스닥지수
- 나스닥 (^IXIC): 미국 나스닥 종합지수
- S&P 500 (^GSPC): 미국 S&P 500 지수
- 다우존스 (^DJI): 미국 다우존스 산업평균지수
- 비트코인 (BTC-USD): 비트코인 가격
- 이더리움 (ETH-USD): 이더리움 가격
- 원/달러 (KRW=X): 원/달러 환율

### 🔔 주식 감시 및 알림

**`/addstock`** - 감시 목록에 주식 추가 (최대 10개)
```
/addstock ticker:AAPL name:애플
/addstock ticker:005930.KS name:삼성전자
/addstock ticker:BTC-USD
```

**`/removestock`** - 감시 목록에서 제거
```
/removestock ticker:AAPL
```

**`/watchlist`** - 감시 중인 주식 목록 확인
```
/watchlist
```

**`/setalert`** - 주식 변동 알림 설정 (관리자)
```
/setalert channel:#주식-알림 threshold:5
```
- threshold: 알림을 받을 변동률 (%, 기본값 5%)
- 5분마다 자동으로 감시 목록의 주식들을 체크
- 설정한 임계값 이상 변동 시 자동으로 알림 전송

**`/stopalert`** - 주식 알림 중지 (관리자)
```
/stopalert
```

**주요 티커 심볼 예시:**
- 미국 주식: AAPL (애플), TSLA (테슬라), MSFT (마이크로소프트), GOOGL (구글), NVDA (엔비디아)
- 한국 주식: 005930.KS (삼성전자), 000660.KS (SK하이닉스), 035420.KS (네이버), 035720.KS (카카오)
- 암호화폐: BTC-USD (비트코인), ETH-USD (이더리움), XRP-USD (리플)

**사용 시나리오:**
1. `/addstock ticker:TSLA name:테슬라` - 테슬라 주식을 감시 목록에 추가
2. `/setalert channel:#주식-알림 threshold:3` - 3% 이상 변동 시 알림 받도록 설정
3. 5분마다 자동으로 테슬라 주가를 체크
4. 3% 이상 상승/하락하면 #주식-알림 채널에 자동 알림 📈/📉

### 자동 기능

- **자동 환영 메시지**: 새 멤버가 서버에 참가하면 자동으로 환영 메시지 전송
- **자동 레벨링**: 채팅할수록 자동으로 XP 획득 및 레벨업
- **반응 역할**: 설정한 메시지에 반응하면 자동으로 역할 부여
- **자동 뉴스 전송**: 설정한 시간에 자동으로 최신 뉴스 전송 (매일)
- **자동 주식 정보 전송**: 설정한 시간에 자동으로 주식 시장 현황 전송 (매일)
- **주식 감시 및 알림**: 감시 목록의 주식을 5분마다 자동 모니터링, 큰 변동 시 즉시 알림

---

## 6. 문제 해결

### 봇이 시작되지 않는 경우

1. **토큰 확인**: `DISCORD_TOKEN`이 올바르게 설정되었는지 확인합니다.
2. **권한 확인**: Discord Developer Portal에서 Privileged Gateway Intents가 활성화되어 있는지 확인합니다.

```bash
# Kubernetes 로그 확인
kubectl logs deployment/discord-welcome-bot -n discord-bot
```

### 환영 메시지가 전송되지 않는 경우

1. **채널 ID 확인**: `WELCOME_CHANNEL_ID`가 올바른지 확인합니다.
2. **봇 권한 확인**: 봇이 해당 채널에 메시지를 보낼 권한이 있는지 확인합니다.
3. **Intents 확인**: `SERVER MEMBERS INTENT`가 활성화되어 있는지 확인합니다.

### Pod가 CrashLoopBackOff 상태인 경우

```bash
# Pod 로그 확인
kubectl logs deployment/discord-welcome-bot -n discord-bot

# Secret이 올바르게 생성되었는지 확인
kubectl get secret discord-bot-secret -n discord-bot -o yaml

# Deployment 재시작
kubectl rollout restart deployment/discord-welcome-bot -n discord-bot
```

### 이미지를 가져올 수 없는 경우 (ImagePullBackOff)

1. **이미지 경로 확인**: `deployment.yaml`의 이미지 경로가 올바른지 확인합니다.
2. **레지스트리 인증**: 프라이빗 레지스트리를 사용하는 경우 ImagePullSecret을 설정합니다.

```bash
# Docker 레지스트리 인증 Secret 생성
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email \
  -n discord-bot

# deployment.yaml에 imagePullSecrets 추가
spec:
  imagePullSecrets:
  - name: regcred
```

---

## 추가 정보

### 봇 업데이트

새로운 코드를 배포하려면:

```bash
# 1. 새 이미지 빌드 및 푸시
docker build -t your-registry.com/discord-welcome-bot:v1.1 .
docker push your-registry.com/discord-welcome-bot:v1.1

# 2. Deployment 이미지 업데이트
kubectl set image deployment/discord-welcome-bot \
  bot=your-registry.com/discord-welcome-bot:v1.1 \
  -n discord-bot

# 3. 롤아웃 상태 확인
kubectl rollout status deployment/discord-welcome-bot -n discord-bot
```

### 봇 삭제

```bash
# Deployment 삭제
kubectl delete -f k8s/deployment.yaml

# Secret 삭제
kubectl delete -f k8s/secret.yaml

# Namespace 삭제 (모든 리소스 삭제)
kubectl delete -f k8s/namespace.yaml
```

### 리소스 모니터링

```bash
# 리소스 사용량 확인
kubectl top pod -n discord-bot

# Pod 이벤트 확인
kubectl get events -n discord-bot --sort-by='.lastTimestamp'
```

---

## 지원 및 문의

문제가 발생하거나 질문이 있으시면 GitHub Issues를 통해 문의해주세요.

**즐거운 Discord 봇 운영 되세요!** 🎉
