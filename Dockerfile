# Python 3.11을 베이스 이미지로 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /usr/src/app

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY ./app /usr/src/app/app
COPY ./static /usr/src/app/static

# 8000번 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
