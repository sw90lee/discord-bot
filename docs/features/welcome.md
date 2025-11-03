# 환영 시스템

새로운 멤버가 서버에 참가할 때 자동으로 환영 메시지를 전송하는 기능입니다.

## 목차
- [개요](#개요)
- [명령어](#명령어)
- [설정 방법](#설정-방법)
- [사용 예시](#사용-예시)
- [커스터마이징](#커스터마이징)
- [문제 해결](#문제-해결)

## 개요

환영 시스템은 새 멤버가 서버에 참가할 때 자동으로 환영 메시지를 보내고, 선택적으로 자동 역할을 부여할 수 있는 기능입니다.

### 주요 기능
- ✅ 자동 환영 메시지 전송
- ✅ 커스터마이징 가능한 메시지 (제목, 내용, 색상, 푸터)
- ✅ 임베드 형식의 예쁜 메시지
- ✅ 멤버 정보 표시 (아바타, 멤버 수)
- ✅ 변수 사용 가능 ({mention}, {name}, {server}, {member_count})
- ✅ 재배포 없이 메시지 변경 가능
- ✅ 자동 역할 부여 기능

## 명령어

### `/setwelcome`
환영 메시지를 커스터마이징합니다.

**권한**: 관리자 (Administrator)

**매개변수**:
- `title` (선택): 환영 메시지 제목
- `description` (선택): 환영 메시지 내용
- `color` (선택): 색상 (hex 코드, 예: #00ff00)
- `footer` (선택): 하단 텍스트

**예시**:
```
/setwelcome title:"환영합니다!" description:"{mention}님, {server}에 오신 것을 환영합니다!"
/setwelcome color:#FF5733 footer:"즐거운 시간 되세요!"
```

### `/welcomechannel`
환영 메시지를 보낼 채널을 설정합니다.

**권한**: 관리자 (Administrator)

**매개변수**:
- `channel` (필수): 환영 메시지를 보낼 채널

**예시**:
```
/welcomechannel channel:#환영-채널
/welcomechannel channel:#입장
```

### `/welcometest`
현재 환영 메시지 설정을 미리 볼 수 있습니다.

**권한**: 관리자 (Administrator)

**예시**:
```
/welcometest
```

## 설정 방법

### 1단계: 환영 채널 설정

먼저 환영 메시지를 보낼 채널을 지정합니다:

```
/welcomechannel channel:#환영-채널
```

> **참고**: 채널을 설정하지 않으면 서버의 시스템 채널에 메시지가 전송됩니다.

### 2단계: 환영 메시지 커스터마이징

원하는 대로 메시지를 수정합니다:

```
/setwelcome
  title:"🎉 새로운 멤버 도착!"
  description:"{mention}님, {server}에 오신 것을 환영합니다! 현재 멤버 수: {member_count}명"
```

### 3단계: 메시지 미리보기

설정한 메시지를 확인합니다:

```
/welcometest
```

### 4단계: 자동 역할 설정 (선택사항)

새 멤버에게 자동으로 역할을 부여하려면:

```
/autorole role:@멤버
```

> 자동 역할 설정은 [역할 관리](roles.md) 문서를 참고하세요.

## 사용 예시

### 예시 1: 기본 환영 메시지

```
/setwelcome title:"환영합니다!" description:"{mention}님, 반갑습니다!"
```

**결과**:
```
┌─────────────────────────────────┐
│ 🎉 환영합니다!                    │
│                                 │
│ @신규멤버님, 반갑습니다!            │
│                                 │
│ 서버 정보                         │
│ 현재 멤버 수: 150명               │
│                                 │
│ 즐거운 시간 되세요!                │
└─────────────────────────────────┘
```

### 예시 2: 상세한 환영 메시지

```
/setwelcome
  title:"🌟 {server}에 오신 것을 환영합니다!"
  description:"{mention}님, 환영합니다!

규칙을 확인하시려면 #규칙 채널을 방문해주세요.
질문이 있으시면 #질문 채널에 문의해주세요.

현재 {member_count}명의 멤버가 함께하고 있습니다!"
  color:#FFD700
  footer:"즐거운 커뮤니티 생활 되세요!"
```

### 예시 3: 게임 서버 환영 메시지

```
/setwelcome
  title:"⚔️ 모험가님을 환영합니다!"
  description:"{mention}님이 {server}에 입장하셨습니다!

🎮 게임 시작하기: #게임방
📋 규칙 확인: #공지사항
💬 자유 대화: #잡담

함께 즐거운 시간 보내요!"
  color:#FF0000
```

## 커스터마이징

### 사용 가능한 변수

환영 메시지에서 다음 변수를 사용할 수 있습니다:

| 변수 | 설명 | 예시 |
|-----|------|-----|
| `{mention}` | 멤버 멘션 | @홍길동 |
| `{name}` | 멤버 이름 | 홍길동 |
| `{server}` | 서버 이름 | 우리 서버 |
| `{member_count}` | 현재 멤버 수 | 150 |

**예시**:
```
{mention}님, {server}에 오신 {member_count}번째 멤버입니다!
```

### 색상 코드

색상은 Hex 코드로 지정할 수 있습니다:

| 색상 | Hex 코드 | 용도 |
|-----|---------|-----|
| 초록색 | #00FF00 | 환영, 성공 |
| 파란색 | #0000FF | 일반 정보 |
| 빨간색 | #FF0000 | 중요, 게임 |
| 금색 | #FFD700 | 특별, 프리미엄 |
| 보라색 | #800080 | 고급, 엘리트 |
| 주황색 | #FFA500 | 활동적, 밝음 |

**예시**:
```
/setwelcome color:#FFD700
```

### 메시지 요소 표시/숨기기

`config.json` 또는 ConfigMap에서 설정 가능:

```json
{
  "welcome": {
    "enabled": true,
    "show_member_count": true,    // 멤버 수 표시
    "show_avatar": true            // 아바타 표시
  }
}
```

## 고급 설정

### 서버별 설정

각 서버마다 다른 환영 메시지를 설정할 수 있습니다. `/setwelcome` 명령어는 자동으로 해당 서버에만 적용됩니다.

### 환영 메시지 비활성화

환영 메시지를 일시적으로 비활성화하려면 `config.json`을 수정:

```json
{
  "welcome": {
    "enabled": false
  }
}
```

### ConfigMap으로 기본값 설정 (Kubernetes)

Kubernetes에서 ConfigMap을 수정하여 기본 환영 메시지를 설정할 수 있습니다:

```bash
kubectl edit configmap discord-bot-config -n discord-bot
```

```yaml
data:
  config.json: |
    {
      "welcome": {
        "enabled": true,
        "title": "환영합니다!",
        "description": "{mention}님, 환영합니다!",
        "color": 65280,
        "footer": "즐거운 시간 되세요!"
      }
    }
```

변경 후 Pod 재시작:
```bash
kubectl rollout restart deployment/discord-bot -n discord-bot
```

## 문제 해결

### 환영 메시지가 전송되지 않아요

**원인 1**: Bot Intent가 비활성화됨
- Discord Developer Portal → Bot → Privileged Gateway Intents
- `SERVER MEMBERS INTENT` 활성화 확인

**원인 2**: 채널 권한 부족
- 봇이 환영 채널에 메시지를 보낼 권한이 있는지 확인
- 필요한 권한: `Send Messages`, `Embed Links`

**원인 3**: 채널 ID가 잘못됨
- `/welcomechannel` 명령어로 채널 재설정

### 색상이 제대로 표시되지 않아요

**해결**:
- Hex 코드 앞에 `#`을 붙였는지 확인
- 올바른 형식: `#FF0000` (O), `FF0000` (X)

### 변수가 그대로 표시돼요

**원인**: 중괄호 형식이 잘못됨
- 올바른 형식: `{mention}` (O)
- 잘못된 형식: `mention`, `{{mention}}` (X)

### 아바타가 표시되지 않아요

**원인**: 봇에게 `Embed Links` 권한이 없음
- 서버 설정 → 역할 → 봇 역할 → `Embed Links` 권한 활성화

## 모범 사례

### ✅ 추천하는 설정

1. **간결하고 명확한 메시지**
   - 너무 길지 않게 (3-5줄 권장)
   - 핵심 정보만 포함

2. **중요한 채널 안내**
   - 규칙 채널 링크
   - 자기소개 채널
   - 질문 채널

3. **친근한 톤**
   - 이모지 적절히 사용
   - 따뜻한 인사말

4. **서버 특색 반영**
   - 게임 서버: 게임 관련 이모지/용어
   - 스터디 서버: 학습 관련 메시지
   - 커뮤니티: 친근하고 편안한 분위기

### ❌ 피해야 할 것

1. **과도하게 긴 메시지**
   - 10줄 이상의 긴 메시지는 읽지 않음

2. **너무 많은 이모지**
   - 가독성 저하

3. **복잡한 규칙 나열**
   - 환영 메시지에는 간단히, 자세한 규칙은 별도 채널에

4. **멘션 남용**
   - 역할 멘션은 피하기 (스팸으로 인식될 수 있음)

## 관련 기능

- [역할 관리](roles.md) - 자동 역할 부여
- [유틸리티](utility.md) - 서버 정보 표시

## 추가 리소스

- [Discord Embed 색상표](https://gist.github.com/thomasbnt/b6f455e2c7d743b796917fa3c205f812)
- [Discord 권한 가이드](https://discord.com/developers/docs/topics/permissions)
