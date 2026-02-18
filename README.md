# git-game

Main project lives in `git-learning-game/`.

## 실행 방법 (CLI 학습앱)

### Make로 실행 (추천)

```bash
make doctor
make list
make play PLAYER=your_name STAGE=1
make leaderboard LIMIT=10
make help
```

### 직접 스크립트 실행

```bash
cd git-learning-game

# 1) 환경 점검
./git-trainer.sh doctor

# 2) 스테이지 목록 확인
./git-trainer.sh list

# 3) 학습 시작
./git-trainer.sh play

# 4) 점수 확인
./git-trainer.sh leaderboard
```

플레이 중 내장 명령:
- `:status` 현재 스테이지 완료 조건 확인
- `:hint` 힌트 보기 (같은 스테이지 1회 재도전 트리거)
- `:solution` 해답 보기 (같은 스테이지 1회 재도전 트리거)
- `:next` 다음 스테이지 이동
- `:reset` 현재 스테이지 초기화
- `:leaderboard` 리더보드 보기
- `:quit` 종료
