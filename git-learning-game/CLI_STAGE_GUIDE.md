# CLI Stage Guide (20 Stages)

이 문서는 `./git-trainer.sh play` 기준의 실습 가이드다.

## 공통 사용법
- 스테이지 목표 확인: `:status`
- 힌트/해답: `:hint`, `:solution` (사용 시 동일 스테이지 1회 재도전)
- 완료 후 다음 이동: `:next`
- 리셋: `:reset`

## Stage 1. Cherry-pick Hotfix
- 목표: `hotfix` 브랜치 커밋을 `main`에 반영
- 체크리스트:
1. `git log --oneline hotfix`로 커밋 해시 확인
2. `main`에서 `git cherry-pick <hash>`
3. 마지막 커밋 메시지에 `Hotfix:` 유지
- 통과 신호: `app.cfg`에 `hotfix=true`

## Stage 2. Rebase Squash
- 목표: 커밋 수를 2개 이하로 정리, 마지막 메시지를 `Feature:`로 시작
- 체크리스트:
1. `git rebase -i HEAD~2` 또는 `HEAD~3`
2. `squash/fixup` 정리
3. 마지막 커밋 메시지 `Feature: ...`
- 통과 신호: `:status`가 완료 조건 충족

## Stage 3. Conflict Merge
- 목표: `feature-ui` merge 후 충돌 제거
- 체크리스트:
1. `git merge feature-ui`
2. `README.md` 충돌 해결
3. `git add README.md && git commit`
- 통과 신호: 충돌 마커(`<<<<<<<`) 없음 + merge 커밋 존재

## Stage 4. Reset Recovery
- 목표: `lost draft` 제거 + clean working tree
- 체크리스트:
1. `git reset --soft/--mixed`로 정리
2. `notes.txt`에서 `lost draft` 제거
3. 커밋 후 `git status` clean
- 통과 신호: `notes.txt`에 `lost draft` 없음

## Stage 5. Release Hotfix
- 목표: release 변경 반영 + `fix` 메시지 커밋
- 체크리스트:
1. `release` 작업 내용(`def sub`) 반영
2. 커밋 메시지에 `fix` 포함
- 통과 신호: `service.py`에 `def sub`

## Stage 6. Feature Branch Start
- 목표: `feature/auth` 브랜치에서 `Feature:` 커밋
- 체크리스트:
1. `git checkout -b feature/auth`
2. 파일 수정 후 `git commit -m "Feature: ..."`
- 통과 신호: 현재 브랜치 `feature/auth`

## Stage 7. Stash Practice
- 목표: stash 1개 이상 + `api.py`에 `timeout=60`
- 체크리스트:
1. `api.py`를 `timeout=60`으로 수정
2. `git stash push ...`로 stash 생성
3. 필요 시 `git stash apply`
- 통과 신호: `git stash list`에 항목 존재

## Stage 8. Release Tag
- 목표: `v1.0.0` 태그 생성
- 체크리스트:
1. `git tag -a v1.0.0 -m "release v1.0.0"`
2. `git tag --list` 확인
- 통과 신호: `v1.0.0` 태그 존재

## Stage 9. Cherry-pick Range
- 목표: `feature-range`에서 필요한 커밋만 반영
- 체크리스트:
1. `git log --oneline feature-range`
2. `git cherry-pick <start>^..<end>`
3. merge 없이 선형 히스토리 유지
- 통과 신호: `config.py` 생성 + merge 커밋 없음

## Stage 10. Revert Bad Commit
- 목표: 버그 커밋을 `revert`
- 체크리스트:
1. `git log --oneline`
2. `git revert <bad-commit>`
- 통과 신호: 마지막 메시지 `Revert` 포함 + 버그 코드 제거

## Stage 11. Rebase Onto
- 목표: `old-base` 제외하고 `feature` 재배치
- 체크리스트:
1. `git checkout feature`
2. `git rebase --onto main old-base feature`
- 통과 신호: 최근 로그에 `Old:` 제거, `Feature:` 유지

## Stage 12. Reflog Rescue
- 목표: reflog로 `critical-v2` 복구
- 체크리스트:
1. `git reflog`
2. `git reset --hard <v2-hash>`
- 통과 신호: `important.py`에 `critical-v2`

## Stage 13. Bisect Start
- 목표: bisect 기록 남기기
- 체크리스트:
1. `git bisect start`
2. `git bisect bad`
3. `git bisect good <hash>`
- 통과 신호: `.git/BISECT_LOG` 파일 존재

## Stage 14. Worktree Hotfix
- 목표: worktree에서 `hotfix` 브랜치 커밋(`Hotfix WT`)
- 체크리스트:
1. `git worktree add ../hotfix -b hotfix`
2. worktree 경로에서 수정/커밋 (`Hotfix WT` 포함)
3. 원래 repo에서 로그 확인
- 통과 신호: `hotfix` 브랜치 + 로그에 `Hotfix WT`

## Stage 15. Bundle Export
- 목표: `feature.bundle` 생성
- 체크리스트:
1. `git bundle create feature.bundle HEAD`
2. `ls -lh feature.bundle`
- 통과 신호: `feature.bundle` 존재(0바이트 아님)

## Stage 16. Notes Namespace
- 목표: `team` namespace로 note 추가
- 체크리스트:
1. `git notes --ref=team add -m "review"`
2. `git notes --ref=team list`
- 통과 신호: `.git/refs/notes/team` 존재

## Stage 17. Replace Object
- 목표: `git replace` ref 생성
- 체크리스트:
1. old/new 커밋 해시 확인
2. `git replace <old> <new>`
3. `ls .git/refs/replace`
- 통과 신호: `.git/refs/replace/*` 생성

## Stage 18. Merge Strategy Ours
- 목표: `-X ours`로 merge + main 설정 유지
- 체크리스트:
1. `git merge -X ours feature-merge`
2. `config.yml` 내용 확인
- 통과 신호: merge 커밋 존재 + `config.yml`에 main 계열 값 유지

## Stage 19. Merge Then Cleanup Branch
- 목표: merge 후 feature 브랜치 삭제
- 체크리스트:
1. `git merge feature-cleanup`
2. `git branch -d feature-cleanup`
- 통과 신호: merge 커밋 존재 + 브랜치 삭제 완료

## Stage 20. Final Amend
- 목표: staged 변경 포함 `--amend` + 메시지 `Final:`
- 체크리스트:
1. staged 상태 확인
2. `git commit --amend -m "Final: ..."`
3. `git status` clean
- 통과 신호: 마지막 커밋 메시지 `Final:` + 작업트리 clean

## 막힐 때 빠른 디버그
1. 현재 브랜치: `git branch --show-current`
2. 최근 로그: `git log --oneline -n 8`
3. 작업 상태: `git status`
4. 다시 시작: `:reset`
