#!/bin/bash
# 개발용 스크립트 - 백엔드와 프론트엔드를 각각 다른 포트에서 실행

BACKEND_PORT=${1:-8000}
FRONTEND_PORT=${2:-3000}

echo "🔧 개발 모드로 시작..."
echo "🔍 백엔드: http://localhost:$BACKEND_PORT"
echo "⚙️ 프론트엔드: http://localhost:$FRONTEND_PORT"
echo ""

# 백엔드 시작 (백그라운드)
echo "🚀 백엔드 시작 중..."
cd backend
python -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1
uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
BACKEND_PID=$!

# 프론트엔드 시작
echo "🎨 프론트엔드 시작 중..."
cd ../frontend
npm install > /dev/null 2>&1 || echo "⚠️ npm install 실패 - 수동으로 실행하세요"

# 환경변수 설정
export REACT_APP_API_URL=http://localhost:$BACKEND_PORT
export REACT_APP_WS_URL=ws://localhost:$BACKEND_PORT

# 종료 함수
cleanup() {
    echo "
💯 종료 중..."
    kill $BACKEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup INT TERM

echo "
✅ 준비 완료!"
echo "🚀 게임 접속: http://localhost:$FRONTEND_PORT"
echo "🔍 API 도큐먼트: http://localhost:$BACKEND_PORT/docs"
echo "🚫 종료: Ctrl+C"
echo ""

# 프론트엔드 시작 (전경에서 실행)
PORT=$FRONTEND_PORT npm start
