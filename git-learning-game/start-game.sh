#!/bin/bash
# Git Learning Game 시작 스크립트

# 기본 포트 설정
GAME_PORT=${1:-3001}
API_PORT=${2:-8001}
DB_PORT=${3:-5433}
REDIS_PORT=${4:-6380}

echo "🎮 Git Learning Game 시작"
echo "🌐 게임 URL: http://localhost:$GAME_PORT"
echo "🛠️ API URL: http://localhost:$API_PORT"
echo "📦 Database Port: $DB_PORT"
echo "🟥 Redis Port: $REDIS_PORT"
echo ""

# 환경변수 설정
export GAME_PORT=$GAME_PORT
export GAME_API_PORT=$API_PORT
export POSTGRES_PORT=$DB_PORT
export REDIS_PORT=$REDIS_PORT

# Docker Compose 실행
docker-compose up -d

echo ""
echo "✅ 게임이 시작되었습니다!"
echo "🚀 브라우저에서 http://localhost:$GAME_PORT 에 접속하세요"
echo ""
echo "🔄 중지: docker-compose down"
echo "📈 로그: docker-compose logs -f"
