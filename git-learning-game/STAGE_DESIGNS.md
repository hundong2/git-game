# 스테이지 상세 설계안 (초안)

각 스테이지는 협업 상황을 바탕으로 구성되며, 힌트/해답 조회 시 동일 스테이지 1회 재도전 정책을 기본 적용한다.

## Basic (5)

### B-1: Cherry-pick Hotfix
- Context: 동료가 hotfix 브랜치에 긴급 수정.
- Objectives: hotfix 커밋 cherry-pick, 충돌 해결, 메시지 규칙 준수.
- Constraints: merge 금지.
- Hint: `git cherry-pick <hash>` 후 충돌 해결.
- Solution: `git cherry-pick <hash> -> resolve -> git add -> git cherry-pick --continue`.
- Validation:
  - must_have: `head_message_contains` "Hotfix:"; `file_contains` "config.py" "DEBUG = True"
  - must_not_have: `has_merge_commits`

### B-2: Rebase Squash Cleanup
- Context: PR 전 커밋을 깔끔하게 정리해야 함.
- Objectives: 최근 4개 커밋을 2개로 squash, 메시지 수정.
- Constraints: merge 금지, rebase -i만 허용.
- Hint: `git rebase -i HEAD~4`.
- Solution: `git rebase -i HEAD~4 -> squash -> 메시지 수정`.
- Validation:
  - must_have: `commit_count_at_most` 2; `head_message_contains` "Feature:"
  - must_not_have: `has_merge_commits`

### B-3: Reset and Recover
- Context: 실수로 커밋을 되돌렸고 다시 복구해야 함.
- Objectives: `reset --soft`와 `reset --mixed` 수행, 최종 파일 상태 유지.
- Constraints: `reset --hard` 금지.
- Hint: `git reset --soft HEAD~1` 후 상태 확인.
- Solution: `git reset --soft HEAD~1 -> git reset --mixed HEAD~1`.
- Validation:
  - must_have: `commit_count_at_most` 3; `worktree_clean`
  - must_not_have: `file_contains` "notes.txt" "lost"

### B-4: Stash Partial Changes
- Context: 긴급 버그 수정으로 일부 변경만 잠시 저장.
- Objectives: staged 변경만 stash, 이름 지정, apply 후 유지.
- Constraints: `stash pop` 금지.
- Hint: `git stash push -S -m <name>`.
- Solution: `git add <files> -> git stash push -S -m "partial" -> git stash apply`.
- Validation:
  - must_have: `stash_count_at_least` 1

### B-5: Simple Conflict Merge
- Context: 동료가 같은 파일을 수정해 충돌 발생.
- Objectives: 충돌 해결 후 merge 완료.
- Constraints: rebase 금지.
- Hint: `git merge <branch>` 후 파일 수정.
- Solution: `git merge <branch> -> resolve -> git add -> git commit`.
- Validation:
  - must_have: `has_merge_commits`

## Intermediate (5)

### I-1: Rebase --onto
- Context: 오래된 베이스 브랜치에서 파생된 기능을 최신 master로 이동.
- Objectives: 특정 구간만 옮겨 rebase.
- Constraints: merge 금지.
- Hint: `git rebase --onto master <old> <feature>`.
- Solution: `git rebase --onto master old-base feature`.
- Validation:
  - must_have: `branch_is_current` "feature"; `no_merge_commits`

### I-2: Reflog Rescue
- Context: 잘못된 reset으로 커밋 분실.
- Objectives: reflog로 커밋 복구.
- Constraints: filter-repo 금지.
- Hint: `git reflog`로 커밋 찾기.
- Solution: `git reflog -> git reset --hard <hash>`.
- Validation:
  - must_have: `file_exists` "important.py"; `worktree_clean`

### I-3: Cherry-pick Range
- Context: 기능 브랜치에서 특정 범위만 선택.
- Objectives: 범위 cherry-pick, 충돌 해결.
- Constraints: merge 금지.
- Hint: `git cherry-pick A..B`.
- Solution: `git cherry-pick <start>^..<end>`.
- Validation:
  - must_have: `commit_message_contains` "Feature:"; `no_merge_commits`

### I-4: Bisect Bug Hunt
- Context: 특정 커밋에서 버그가 도입됨.
- Objectives: bisect로 원인 커밋 찾기.
- Constraints: 수동 reset 금지.
- Hint: `git bisect start`.
- Solution: `git bisect start -> bad -> good <hash>`.
- Validation:
  - must_have: `commit_message_contains` "BUG"

### I-5: Worktree Hotfix
- Context: 릴리즈 중인 브랜치와 별도로 긴급 수정 필요.
- Objectives: worktree 생성, 수정, 제거.
- Constraints: 기존 작업 트리 변경 금지.
- Hint: `git worktree add`.
- Solution: `git worktree add ../hotfix hotfix -> fix -> git worktree remove`.
- Validation:
  - must_have: `branch_exists` "hotfix"

## Advanced (5)

### A-1: Filter-Repo Cleanup
- Context: 민감 정보가 히스토리에 포함됨.
- Objectives: filter-repo로 특정 파일 제거.
- Constraints: 직접 amend 금지.
- Hint: `git filter-repo --path <file> --invert-paths`.
- Solution: `git filter-repo --path secrets.txt --invert-paths`.
- Validation:
  - must_have: `file_exists` "README.md"
  - must_not_have: `file_exists` "secrets.txt"

### A-2: Replace Object
- Context: 잘못된 커밋을 임시로 교체.
- Objectives: git replace로 커밋 교체 후 확인.
- Constraints: reset 금지.
- Hint: `git replace <old> <new>`.
- Solution: `git replace <old> <new> -> git log --decorate`.
- Validation:
  - must_have: `commit_message_contains` "replace"

### A-3: Bundle Exchange
- Context: 네트워크 없는 환경에서 변경 공유.
- Objectives: bundle 생성 후 적용.
- Constraints: 원격 push 금지.
- Hint: `git bundle create`.
- Solution: `git bundle create feature.bundle <branch>`.
- Validation:
  - must_have: `file_exists` "feature.bundle"

### A-4: Custom Merge Strategy
- Context: 특정 파일은 항상 ours 전략 적용.
- Objectives: merge 전략 옵션 사용.
- Constraints: 기본 merge 금지.
- Hint: `git merge -X ours`.
- Solution: `git merge -X ours feature`.
- Validation:
  - must_have: `has_merge_commits`

### A-5: Notes Workflow
- Context: 커밋에 리뷰 메모를 남겨 공유.
- Objectives: notes 추가, 네임스페이스 분리.
- Constraints: amend 금지.
- Hint: `git notes --ref`.
- Solution: `git notes add -m "review" -> git notes --ref=team`.
- Validation:
  - must_have: `commit_message_contains` "notes"
