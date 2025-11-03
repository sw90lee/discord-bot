# Discord Multi-Purpose Bot 문서

Discord 봇의 모든 기능에 대한 상세 문서입니다.

## 목차

### 시작하기
- [설치 및 설정](../SETUP.md)
- [빠른 시작](../README.md)

### 핵심 기능

#### 1. 환영 시스템
- [환영 메시지 설정](features/welcome.md)
- 새 멤버 자동 환영
- 커스터마이징 가능한 메시지
- 자동 역할 부여

#### 2. 모더레이션
- [모더레이션 기능](features/moderation.md)
- 멤버 관리 (킥, 밴, 타임아웃)
- 메시지 관리
- 경고 시스템

#### 3. 역할 관리
- [역할 관리 시스템](features/roles.md)
- 자동 역할 부여
- 반응 역할
- 역할 할당/제거

#### 4. 레벨링 시스템
- [레벨 및 경험치](features/leveling.md)
- 자동 XP 획득
- 순위표
- 레벨업 알림

#### 5. 유틸리티
- [유틸리티 명령어](features/utility.md)
- 서버 정보
- 사용자 정보
- 투표 및 공지

#### 6. 뉴스 자동 전송
- [뉴스 기능](features/news.md)
- 실시간 뉴스 조회
- 자동 뉴스 전송 스케줄
- 다양한 뉴스 소스

#### 7. 주식 시장 정보
- [주식 정보 및 감시](features/stocks.md)
- 실시간 주가 조회
- 자동 주식 정보 전송
- 주식 감시 목록
- 가격 변동 알림

## 명령어 빠른 참조

### 환영 시스템
| 명령어 | 설명 | 권한 |
|-------|------|-----|
| `/setwelcome` | 환영 메시지 설정 | 관리자 |
| `/welcomechannel` | 환영 채널 설정 | 관리자 |
| `/welcometest` | 환영 메시지 미리보기 | 관리자 |

### 모더레이션
| 명령어 | 설명 | 권한 |
|-------|------|-----|
| `/kick` | 멤버 추방 | Kick Members |
| `/ban` | 멤버 차단 | Ban Members |
| `/unban` | 차단 해제 | Ban Members |
| `/timeout` | 임시 타임아웃 | Moderate Members |
| `/clear` | 메시지 삭제 | Manage Messages |
| `/warn` | 경고 부여 | Moderate Members |

### 역할 관리
| 명령어 | 설명 | 권한 |
|-------|------|-----|
| `/autorole` | 자동 역할 설정 | Manage Roles |
| `/role` | 역할 부여/제거 | Manage Roles |
| `/reactionrole` | 반응 역할 설정 | Manage Roles |

### 레벨링
| 명령어 | 설명 | 권한 |
|-------|------|-----|
| `/rank` | 내 레벨 확인 | 모두 |
| `/leaderboard` | 순위표 | 모두 |
| `/setlevel` | 레벨 설정 | 관리자 |

### 유틸리티
| 명령어 | 설명 | 권한 |
|-------|------|-----|
| `/ping` | 응답 속도 | 모두 |
| `/serverinfo` | 서버 정보 | 모두 |
| `/userinfo` | 사용자 정보 | 모두 |
| `/poll` | 투표 생성 | 모두 |
| `/announce` | 공지 생성 | Manage Messages |

### 뉴스
| 명령어 | 설명 | 권한 |
|-------|------|-----|
| `/news` | 뉴스 조회 | 모두 |
| `/schedulenews` | 자동 전송 설정 | 관리자 |
| `/stopnews` | 자동 전송 중지 | 관리자 |

### 주식
| 명령어 | 설명 | 권한 |
|-------|------|-----|
| `/stocks` | 주가 조회 | 모두 |
| `/addstock` | 감시 목록 추가 | Manage Guild |
| `/watchlist` | 감시 목록 확인 | 모두 |
| `/setalert` | 알림 설정 | 관리자 |

## 자주 묻는 질문 (FAQ)

### 일반

**Q: 봇이 응답하지 않아요**
A: 다음을 확인해주세요:
1. 봇이 온라인 상태인지 확인
2. 봇에게 해당 채널 접근 권한이 있는지 확인
3. 슬래시 명령어(`/`)를 사용하고 있는지 확인

**Q: 환영 메시지가 전송되지 않아요**
A: Discord Developer Portal에서 `SERVER MEMBERS INTENT`가 활성화되어 있는지 확인하세요.

**Q: 레벨링 시스템이 작동하지 않아요**
A: `MESSAGE CONTENT INTENT`가 활성화되어 있는지 확인하세요.

### 설정

**Q: 환영 메시지를 어떻게 변경하나요?**
A: `/setwelcome` 명령어를 사용하여 제목, 내용, 색상 등을 변경할 수 있습니다.

**Q: 특정 채널에만 레벨링을 적용하고 싶어요**
A: 현재는 모든 채널에서 레벨링이 작동합니다. 특정 채널 제외 기능은 추후 추가 예정입니다.

## 지원

문제가 발생하거나 질문이 있으시면:
- GitHub Issues: [이슈 생성](https://github.com/your-repo/discord-bot/issues)
- 로그 확인: `kubectl logs -f deployment/discord-bot -n discord-bot`

## 기여

기여는 언제나 환영합니다! 자세한 내용은 CONTRIBUTING.md를 참고하세요.
