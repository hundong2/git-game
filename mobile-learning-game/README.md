# mobile-learning-game

Kotlin + Jetpack Compose 기반의 모바일 Git 학습 게임입니다.
기존 `git-learning-game`의 CLI 스테이지 흐름을 모바일 입력형 게임으로 옮겼습니다.

## 포함 내용

- 스테이지 20개(Cherry-pick, Rebase, Merge, Revert, Worktree 등)
- 명령어 입력 기반 진행
- JGit 기반 로컬 저장소 세션 초기화/명령 실행(지원 범위 내 실제 반영)
- 힌트/정답 표시
- 터미널 로그 UI
- 완료율 표시 및 재시작

## 실행 방법

1. Android Studio에서 `mobile-learning-game` 폴더를 Open
2. Gradle Sync 실행
3. 에뮬레이터 또는 실제 기기(API 24+)에서 실행

## JGit 실행 엔진

- 엔진 파일: `app/src/main/java/com/gitgame/mobile/domain/GitRepositoryEngine.kt`
- 스테이지 시작/리셋 시 stage 전용 로컬 Git 저장소를 재생성합니다.
- `status`, `log`, `checkout/switch`, `add`, `commit`, `tag`, `merge`, `cherry-pick`, `revert`, `stash`, `branch -d`를 JGit로 실행합니다.
- 고급 명령(`rebase -i`, `worktree`, `bundle`, `bisect`, `notes`, `replace`)은 학습 모드로 처리하고 스테이지 패턴 검증은 유지합니다.

## CI / Release

- 워크플로우: `.github/workflows/mobile-android-release.yml`
- PR/브랜치 push 시 Debug APK 빌드 + artifact 업로드
- `v*` 태그 push 시 Release APK 빌드 + GitHub Release 생성 + APK 첨부

## 버전 정책

- `versionCode`:
  - Android 배포용 정수 버전
  - CI에서 `git rev-list --count HEAD`(전체 커밋 수) 사용
  - 단조 증가를 보장하는 실무형 방식
- `versionName`:
  - 일반 빌드: `0.0.0-dev.YYYYMMDD+<shortSha>` (예: `0.0.0-dev.20260220+1a2b3c4`)
  - 태그 릴리스(`v1.2.3`): `1.2.3` 사용(SemVer)
- Gradle은 `APP_VERSION_CODE`, `APP_VERSION_NAME` 환경변수를 받아 반영

## 구조

- `app/src/main/java/com/gitgame/mobile/data/StageRepository.kt`: 스테이지 데이터
- `app/src/main/java/com/gitgame/mobile/domain/CommandEvaluator.kt`: 명령어 검증
- `app/src/main/java/com/gitgame/mobile/domain/GitRepositoryEngine.kt`: JGit 저장소 엔진
- `app/src/main/java/com/gitgame/mobile/ui/GameViewModel.kt`: 게임 상태 관리
- `app/src/main/java/com/gitgame/mobile/MainActivity.kt`: Compose UI

## 참고

이 모바일 버전은 학습용 입력 시뮬레이터입니다. 실제 Git 저장소를 직접 조작하는 대신,
스테이지별 핵심 명령 패턴을 검증해 학습 루프를 제공합니다.
