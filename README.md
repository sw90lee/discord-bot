# Discord Multi-Purpose Bot

다양한 기능을 제공하는 Discord 봇입니다. 환영 메시지, 모더레이션, 역할 관리, 레벨링 시스템 등을 지원합니다.

## 주요 기능

### 🎉 환영 시스템
- 새 멤버 자동 환영 메시지
- 커스터마이징 가능한 환영 메시지 (Discord 명령어로 설정)
- 임베드 형식의 예쁜 환영 메시지
- 자동 역할 부여

### 👮 모더레이션
- `/kick` - 멤버 추방
- `/ban` - 멤버 차단
- `/unban` - 차단 해제
- `/timeout` - 임시 타임아웃
- `/clear` - 메시지 대량 삭제
- `/warn` - 경고 부여
- `/warnings` - 경고 목록 확인

### 🎭 역할 관리
- `/autorole` - 신규 멤버 자동 역할 설정
- `/role` - 역할 부여/제거
- `/reactionrole` - 반응으로 역할 받기 설정
- 반응 추가/제거 시 자동 역할 부여/제거

### 📊 레벨링 시스템
- 채팅할수록 자동 XP 획득
- 레벨업 시 자동 알림
- `/rank` - 내 레벨 확인
- `/leaderboard` - 서버 순위표
- `/setlevel` - 레벨 설정 (관리자)

### 🛠️ 유틸리티
- `/ping` - 봇 응답 속도 확인
- `/serverinfo` - 서버 정보
- `/userinfo` - 사용자 정보
- `/poll` - 투표 생성
- `/announce` - 공지사항 생성
- `/avatar` - 아바타 확인

### 📰 뉴스 자동 전송
- `/news` - 최신 뉴스 조회
- `/schedulenews` - 특정 시간에 자동으로 뉴스 전송 설정
- `/stopnews` - 뉴스 자동 전송 중지
- `/newsstatus` - 뉴스 설정 상태 확인
- 지원 뉴스: 구글 뉴스, 네이버 뉴스, IT 뉴스, 경제 뉴스

### 📈 주식 시장 정보
- `/stocks` - 주식 시장 현황 조회
- `/schedulestocks` - 특정 시간에 자동으로 주식 정보 전송 설정
- `/stopstocks` - 주식 자동 전송 중지
- `/stocksstatus` - 주식 설정 상태 확인
- 지원 지표: 코스피, 코스닥, 나스닥, S&P 500, 다우존스, 비트코인, 이더리움, 원/달러

### 🔔 주식 감시 및 알림
- `/addstock` - 특정 주식을 감시 목록에 추가 (최대 10개)
- `/removestock` - 감시 목록에서 제거
- `/watchlist` - 현재 감시 중인 주식 목록 확인
- `/setalert` - 변동 알림 설정 (5% 이상 등락 시 자동 알림)
- `/stopalert` - 알림 중지
- 5분마다 자동 모니터링, 임계값 초과 시 실시간 알림

## 빠른 시작

### 로컬 환경에서 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성 (추천)
cp .env.example .env
# .env 파일을 편집하여 DISCORD_TOKEN을 입력하세요

# 또는 환경 변수로 직접 설정
export DISCORD_TOKEN="your_bot_token"
export WELCOME_CHANNEL_ID="your_channel_id"  # 선택사항

# 봇 실행
python bot.py
```

### Docker로 실행

```bash
docker build -t discord-bot .
docker run -e DISCORD_TOKEN="your_token" discord-bot
```

### Kubernetes에 배포

**방법 A: Helm Chart 사용 (권장)**
```bash
cd k8s/helm-chart
helm install discord-bot . -n discord-bot --create-namespace \
  --set bot.discordToken="YOUR_TOKEN"
```

**방법 B: YAML 매니페스트 사용**
```bash
kubectl apply -f k8s/manifests/namespace.yaml
kubectl apply -f k8s/manifests/configmap.yaml
kubectl apply -f k8s/manifests/secret.yaml
kubectl apply -f k8s/manifests/pvc.yaml
kubectl apply -f k8s/manifests/deployment.yaml
```

## 프로젝트 구조

```
discord-welcome-bot/
├── bot.py                      # 메인 봇 코드
├── cogs/                       # 기능별 Cogs
│   ├── welcome.py             # 환영 시스템
│   ├── moderation.py          # 모더레이션
│   ├── roles.py               # 역할 관리
│   ├── leveling.py            # 레벨링 시스템
│   ├── utility.py             # 유틸리티
│   ├── news.py                # 뉴스 자동 전송
│   └── stocks.py              # 주식 시장 정보
├── utils/                      # 유틸리티 모듈
│   ├── database.py            # SQLite 데이터베이스
│   └── config.py              # 설정 관리
├── data/                       # 데이터 디렉토리 (자동 생성)
│   ├── bot.db                 # SQLite 데이터베이스
│   └── config.json            # 설정 파일
├── requirements.txt            # Python 의존성
├── Dockerfile                  # Docker 이미지
├── .dockerignore              # Docker 빌드 제외
├── .gitignore                 # Git 제외
├── README.md                  # 프로젝트 소개
├── SETUP.md                   # 상세 설정 가이드
└── k8s/                       # Kubernetes 배포
    ├── manifests/             # YAML 매니페스트
    │   ├── namespace.yaml
    │   ├── secret.yaml.template
    │   ├── configmap.yaml
    │   ├── pvc.yaml
    │   └── deployment.yaml
    └── helm-chart/            # Helm Chart
        ├── Chart.yaml
        ├── values.yaml
        ├── README.md
        └── templates/
            ├── deployment.yaml
            ├── secret.yaml
            ├── configmap.yaml
            ├── pvc.yaml
            └── namespace.yaml
```

## 환영 메시지 설정

재배포 없이 환영 메시지를 변경할 수 있습니다:

### 1. Discord 명령어로 설정 (추천)
```
/setwelcome title:"환영합니다!" description:"{mention}님, {server}에 오신 것을 환영합니다!"
/welcomechannel channel:#환영-채널
/welcometest  # 미리보기
```

### 2. ConfigMap 수정 (Kubernetes)
```bash
kubectl edit configmap discord-bot-config -n discord-bot
# 수정 후 봇 재시작
kubectl rollout restart deployment/discord-welcome-bot -n discord-bot
```

### 3. JSON 파일 수정 (로컬)
`data/config.json` 파일을 직접 편집

## 사용 가능한 변수

환영 메시지에서 다음 변수를 사용할 수 있습니다:
- `{mention}` - 사용자 멘션
- `{name}` - 사용자 이름
- `{server}` - 서버 이름
- `{member_count}` - 현재 멤버 수

## 요구사항

- Python 3.11+
- discord.py 2.3.2+
- aiosqlite 0.19.0+
- feedparser 6.0.10+ (뉴스 기능)
- aiohttp 3.9.1+ (HTTP 요청)
- yfinance 0.2.33+ (주식 정보)
- Docker (컨테이너 배포 시)
- Kubernetes (K8s 배포 시)

## 상세 가이드

봇 설정 및 배포에 대한 자세한 내용은 [SETUP.md](SETUP.md)를 참고하세요.

## 라이선스

MIT License
