import socketio
import os
import shutil
import subprocess
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.game.stages import get_stage, Stage, STAGES_BY_ID

# --- 전역 상태 관리 ---
user_states: dict[str, dict] = {}
BASE_WORKDIR = os.path.abspath("user_workspaces")
RANKING_FILE = "ranking.json"

# --- FastAPI 설정 ---
app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=[])
socket_app = socketio.ASGIApp(sio)
app.mount("/socket.io", socket_app)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# --- Helper 함수 ---
def get_user_base_dir(sid: str) -> str:
    return os.path.join(BASE_WORKDIR, sid)

def get_user_cwd(sid: str) -> str:
    return os.path.join(get_user_base_dir(sid), "local_repo")

def save_score(username: str, duration: float):
    try:
        with open(RANKING_FILE, "r") as f:
            rankings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        rankings = []

    rankings.append({"username": username, "time": duration})
    rankings.sort(key=lambda x: x["time"])

    with open(RANKING_FILE, "w") as f:
        json.dump(rankings, f, indent=4)

def get_ranking() -> str:
    try:
        with open(RANKING_FILE, "r") as f:
            rankings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return "No rankings yet. Be the first!"

    if not rankings:
        return "No rankings yet. Be the first!"

    output = "--- Top 10 Rankings ---\n"
    for i, entry in enumerate(rankings[:10]):
        output += f"{i+1}. {entry['username']}: {entry['time']:.2f} seconds\n"
    return output

async def send_stage_info(sid: str, stage: Stage):
    await sio.emit("stage_info", {
        "title": stage.title,
        "description": stage.description,
    }, to=sid)

async def send_git_state(sid: str, cwd: str):
    if not os.path.isdir(os.path.join(cwd, ".git")):
        await sio.emit("git_state_update", {"status": "Not a git repository.", "log": "", "branch": ""}, to=sid)
        return
    try:
        status_proc = subprocess.run("git status", shell=True, cwd=cwd, capture_output=True, text=True, timeout=3)
        log_proc = subprocess.run("git log --graph --all --decorate --oneline", shell=True, cwd=cwd, capture_output=True, text=True, timeout=3)
        branch_proc = subprocess.run("git branch", shell=True, cwd=cwd, capture_output=True, text=True, timeout=3)
        await sio.emit("git_state_update", {
            "status": status_proc.stdout + status_proc.stderr,
            "log": log_proc.stdout + log_proc.stderr,
            "branch": branch_proc.stdout + branch_proc.stderr
        }, to=sid)
    except Exception as e:
        print(f"Error getting git state for {sid}: {e}")

# --- Socket.IO 이벤트 핸들러 ---
@sio.event
async def connect(sid, environ):
    print(f"Socket.IO client connected: {sid}")

    base_dir = get_user_base_dir(sid)
    remote_path = os.path.join(base_dir, "remote_repo.git")
    local_path = get_user_cwd(sid)

    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)

    try:
        # 원격/로컬 저장소 생성
        os.makedirs(remote_path, exist_ok=True)
        subprocess.run("git init --bare", shell=True, cwd=remote_path, check=True)
        subprocess.run(f"git clone {remote_path} {local_path}", shell=True, cwd=base_dir, check=True)

        # 사용자 상태 초기화
        user_states[sid] = {
            "stage_id": 1,
            "username": f"user_{sid[:6]}",
            "start_time": datetime.now(),
            "end_time": None,
        }

        # 첫 스테이지 정보 전송
        stage = get_stage(1)
        if stage:
            stage.setup(local_path)
            await send_stage_info(sid, stage)
            await send_git_state(sid, local_path)

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error setting up git environment for {sid}: {e}")
        await sio.emit("response", {"output": "Error: Could not initialize the game environment."}, to=sid)
        await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    print(f"Socket.IO client disconnected: {sid}")
    base_dir = get_user_base_dir(sid)
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    if sid in user_states:
        del user_states[sid]

@sio.on("command")
async def handle_command(sid, data):
    command = data.get("command", "").strip()
    if not command:
        return

    user_cwd = get_user_cwd(sid)
    stage_id = user_states[sid].get("stage_id", 1)

    # 명령어 처리
    if command.lower() == 'help':
        stage = get_stage(stage_id)
        output = f"Hint: {stage.hint}" if stage else "No hint available."
        await sio.emit("response", {"output": output}, to=sid)
        return
    elif command.lower().startswith("name "):
        parts = command.split(" ", 1)
        if len(parts) > 1 and parts[1].strip():
            username = parts[1].strip()
            user_states[sid]["username"] = username
            output = f"Username changed to: {username}"
        else:
            output = "Invalid command. Usage: name <your_username>"
        await sio.emit("response", {"output": output}, to=sid)
        return
    elif command.lower() == 'ranking':
        output = get_ranking()
        await sio.emit("response", {"output": output}, to=sid)
        return

    # Git 명령어 실행
    try:
        process = subprocess.run(command, shell=True, cwd=user_cwd, capture_output=True, text=True, timeout=5)
        output = process.stdout + process.stderr
    except subprocess.TimeoutExpired:
        output = "Command timed out."
    except Exception as e:
        output = f"An error occurred: {e}"
    await sio.emit("response", {"output": output}, to=sid)

    # Git 상태 업데이트 및 스테이지 완료 확인
    await send_git_state(sid, user_cwd)
    stage = get_stage(stage_id)
    if stage and user_states[sid].get("end_time") is None and stage.check(user_cwd):
        await sio.emit("response", {"output": f"\n🎉 축하합니다! 스테이지 {stage.id} 클리어! 🎉\n"}, to=sid)

        last_stage_id = max(STAGES_BY_ID.keys()) if STAGES_BY_ID else 0

        if stage_id == last_stage_id:
            end_time = datetime.now()
            user_states[sid]["end_time"] = end_time
            duration = (end_time - user_states[sid]["start_time"]).total_seconds()
            username = user_states[sid]["username"]
            save_score(username, duration)
            await sio.emit("response", {
                "output": f"모든 스테이지를 클리어했습니다! 대단해요!\n"
                          f"총 소요 시간: {duration:.2f} 초\n"
                          f"'ranking' 명령어로 순위를 확인해보세요."
            }, to=sid)
        else:
            next_stage_id = stage_id + 1
            next_stage = get_stage(next_stage_id)
            if next_stage:
                user_states[sid]["stage_id"] = next_stage_id
                next_stage.setup(user_cwd)
                await send_stage_info(sid, next_stage)
                await send_git_state(sid, user_cwd)
