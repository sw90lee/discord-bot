# Discord Bot Helm Chart

이 Helm Chart는 Discord Multi-Purpose Bot을 Kubernetes 클러스터에 배포합니다.

## 사전 요구사항

- Kubernetes 1.19+
- Helm 3.0+
- PersistentVolume 프로비저너 지원 (스토리지)

## 설치

### 1. Chart 다운로드

```bash
cd k8s/helm-chart
```

### 2. values.yaml 수정

`values.yaml` 파일을 열고 다음 값들을 설정하세요:

```yaml
bot:
  discordToken: "YOUR_DISCORD_BOT_TOKEN_HERE"
  welcomeChannelId: "YOUR_CHANNEL_ID"  # 선택사항

image:
  repository: your-registry.com/discord-bot
  tag: "latest"
```

### 3. 설치

```bash
# 기본 설치
helm install discord-bot . -n discord-bot --create-namespace

# 또는 values 파일 지정
helm install discord-bot . -f values.yaml -n discord-bot --create-namespace

# 또는 커맨드라인에서 값 설정
helm install discord-bot . \
  --set bot.discordToken="YOUR_TOKEN" \
  --set image.repository="your-registry.com/discord-bot" \
  -n discord-bot --create-namespace
```

## 업그레이드

설정을 변경하고 업그레이드:

```bash
helm upgrade discord-bot . -f values.yaml -n discord-bot
```

## 삭제

```bash
helm uninstall discord-bot -n discord-bot
```

네임스페이스도 함께 삭제:

```bash
kubectl delete namespace discord-bot
```

## 설정 값

| 키 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `namespace` | string | `"discord-bot"` | 배포할 네임스페이스 |
| `image.repository` | string | `"discord-bot"` | 컨테이너 이미지 레포지토리 |
| `image.tag` | string | `"latest"` | 이미지 태그 |
| `image.pullPolicy` | string | `"Always"` | 이미지 pull 정책 |
| `bot.discordToken` | string | `""` | Discord 봇 토큰 (필수) |
| `bot.welcomeChannelId` | string | `""` | 환영 채널 ID (선택) |
| `replicaCount` | int | `1` | Pod 복제본 수 |
| `resources.requests.memory` | string | `"256Mi"` | 메모리 요청 |
| `resources.requests.cpu` | string | `"200m"` | CPU 요청 |
| `resources.limits.memory` | string | `"512Mi"` | 메모리 제한 |
| `resources.limits.cpu` | string | `"400m"` | CPU 제한 |
| `persistence.enabled` | bool | `true` | 영구 스토리지 사용 여부 |
| `persistence.size` | string | `"1Gi"` | 스토리지 크기 |
| `persistence.storageClassName` | string | `""` | StorageClass 이름 |

## 예제

### 프로덕션 환경 설정

```yaml
image:
  repository: myregistry.azurecr.io/discord-bot
  tag: "v1.0.0"
  pullPolicy: IfNotPresent

resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"

persistence:
  enabled: true
  storageClassName: "premium-ssd"
  size: 5Gi

nodeSelector:
  disktype: ssd
```

### 개발 환경 설정

```yaml
image:
  repository: discord-bot
  tag: "dev"

resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"

persistence:
  enabled: false
```

## 트러블슈팅

### Pod가 시작되지 않는 경우

```bash
# Pod 상태 확인
kubectl get pods -n discord-bot

# Pod 로그 확인
kubectl logs -f deployment/discord-bot -n discord-bot

# Pod 이벤트 확인
kubectl describe pod -n discord-bot -l app.kubernetes.io/name=discord-bot
```

### 이미지를 가져올 수 없는 경우

ImagePullSecret을 설정:

```bash
kubectl create secret docker-registry regcred \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  -n discord-bot
```

values.yaml에 추가:

```yaml
imagePullSecrets:
  - name: regcred
```

## 라이선스

MIT License
