# Git Trainer CLI Strategy

## Product Positioning
- `1분 안에 실행 가능한 Git 실습 도구`
- 브라우저 없이 터미널에서 바로 학습/검증/복습
- 스테이지 방식으로 실무 커맨드(cherry-pick, rebase, merge conflict, reset) 집중 훈련

## Growth Strategy (GitHub Stars)
- 빠른 온보딩: `./git-trainer.sh doctor` 와 `./git-trainer.sh play` 두 줄만 제공
- 공유 가능한 결과: 완료 통계(커맨드 수, 힌트 수)를 출력해 학습 인증 스크린샷 유도
- 기여 확장: 스테이지 정의 파일(`cli_trainer/stages.py`)을 단순화해 PR 진입장벽 최소화
- 안정성 강조: 환경 진단(`doctor`) + 테스트(`pytest`) 기본 제공

## Next Feature Bets
- JSON 기반 사용자 커스텀 스테이지 로더
- 실패 패턴 분석(자주 틀리는 명령어 자동 리포트)
- CI에서 스테이지 리그레션 테스트
- `git bisect`, `reflog`, `worktree`, `submodule` 고난도 트랙

