# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 봇 코드 복사
COPY bot.py .

# 비-루트 사용자 생성 및 전환 (보안 강화)
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# 봇 실행
CMD ["python", "-u", "bot.py"]
