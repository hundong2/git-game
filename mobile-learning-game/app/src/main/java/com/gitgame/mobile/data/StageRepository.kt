package com.gitgame.mobile.data

import com.gitgame.mobile.domain.CommandCheck
import com.gitgame.mobile.domain.Stage

object StageRepository {
    val stages: List<Stage> = listOf(
        Stage(
            id = 1,
            title = "Cherry-pick Hotfix",
            objective = "hotfix 브랜치 커밋을 main으로 가져오세요.",
            hint = "git cherry-pick <hash>",
            solution = "git cherry-pick <hotfix-commit>",
            checks = listOf(
                CommandCheck("`git cherry-pick` 명령이 필요합니다.", listOf(Regex("^git\\s+cherry-pick\\b")))
            )
        ),
        Stage(
            id = 2,
            title = "Rebase Squash",
            objective = "커밋을 squash/reword 해서 Feature: 메시지로 정리하세요.",
            hint = "git rebase -i HEAD~N",
            solution = "git rebase -i HEAD~3",
            checks = listOf(
                CommandCheck("`git rebase -i`가 필요합니다.", listOf(Regex("^git\\s+rebase\\s+-i\\b")))
            )
        ),
        Stage(
            id = 3,
            title = "Conflict Merge",
            objective = "feature-ui를 merge 하세요.",
            hint = "git merge feature-ui",
            solution = "git merge feature-ui",
            checks = listOf(
                CommandCheck("`git merge feature-ui`가 필요합니다.", listOf(Regex("^git\\s+merge\\s+feature-ui\\b")))
            )
        ),
        Stage(
            id = 4,
            title = "Reset Recovery",
            objective = "잘못된 draft를 reset으로 정리하세요.",
            hint = "git reset --soft HEAD~1",
            solution = "git reset --soft HEAD~1",
            checks = listOf(
                CommandCheck("`git reset` 명령이 필요합니다.", listOf(Regex("^git\\s+reset\\b")))
            )
        ),
        Stage(
            id = 5,
            title = "Release Hotfix",
            objective = "release 변경을 반영하고 fix 커밋을 남기세요.",
            hint = "git commit -m 'fix: ...'",
            solution = "git commit -m 'fix: apply release hotfix'",
            checks = listOf(
                CommandCheck("fix 메시지가 포함된 커밋이 필요합니다.", listOf(Regex("^git\\s+commit\\b.*fix", RegexOption.IGNORE_CASE)))
            )
        ),
        Stage(
            id = 6,
            title = "Feature Branch Start",
            objective = "feature/auth 브랜치를 생성하세요.",
            hint = "git checkout -b feature/auth",
            solution = "git checkout -b feature/auth",
            checks = listOf(
                CommandCheck("feature/auth 브랜치 생성 명령이 필요합니다.", listOf(Regex("^git\\s+(checkout\\s+-b|switch\\s+-c)\\s+feature/auth\\b")))
            )
        ),
        Stage(
            id = 7,
            title = "Stash Practice",
            objective = "stash를 생성하는 명령을 실행하세요.",
            hint = "git stash push -m 'api timeout'",
            solution = "git stash push -m 'api timeout'",
            checks = listOf(
                CommandCheck("`git stash` 명령이 필요합니다.", listOf(Regex("^git\\s+stash\\b")))
            )
        ),
        Stage(
            id = 8,
            title = "Release Tag",
            objective = "v1.0.0 태그를 생성하세요.",
            hint = "git tag -a v1.0.0 -m 'release'",
            solution = "git tag -a v1.0.0 -m 'release'",
            checks = listOf(
                CommandCheck("v1.0.0 태그 생성 명령이 필요합니다.", listOf(Regex("^git\\s+tag\\b.*v1\\.0\\.0")))
            )
        ),
        Stage(
            id = 9,
            title = "Cherry-pick Range",
            objective = "커밋 범위를 cherry-pick 하세요.",
            hint = "git cherry-pick <start>^..<end>",
            solution = "git cherry-pick abc123^..def456",
            checks = listOf(
                CommandCheck("range cherry-pick 명령이 필요합니다.", listOf(Regex("^git\\s+cherry-pick\\b.*\\.\\.")))
            )
        ),
        Stage(
            id = 10,
            title = "Revert Bad Commit",
            objective = "버그 커밋을 revert 하세요.",
            hint = "git revert <hash>",
            solution = "git revert abc123",
            checks = listOf(
                CommandCheck("`git revert`가 필요합니다.", listOf(Regex("^git\\s+revert\\b")))
            )
        ),
        Stage(
            id = 11,
            title = "Rebase Onto",
            objective = "feature 브랜치를 rebase --onto 하세요.",
            hint = "git rebase --onto main old-base feature",
            solution = "git rebase --onto main old-base feature",
            checks = listOf(
                CommandCheck("`git rebase --onto`가 필요합니다.", listOf(Regex("^git\\s+rebase\\s+--onto\\b")))
            )
        ),
        Stage(
            id = 12,
            title = "Reflog Rescue",
            objective = "reflog를 확인해 복구 지점을 찾으세요.",
            hint = "git reflog",
            solution = "git reflog",
            checks = listOf(
                CommandCheck("`git reflog`가 필요합니다.", listOf(Regex("^git\\s+reflog\\b")))
            )
        ),
        Stage(
            id = 13,
            title = "Bisect Start",
            objective = "bisect 탐색을 시작하세요.",
            hint = "git bisect start",
            solution = "git bisect start",
            checks = listOf(
                CommandCheck("`git bisect start`가 필요합니다.", listOf(Regex("^git\\s+bisect\\s+start\\b")))
            )
        ),
        Stage(
            id = 14,
            title = "Worktree Hotfix",
            objective = "hotfix worktree를 생성하세요.",
            hint = "git worktree add ../hotfix -b hotfix",
            solution = "git worktree add ../hotfix -b hotfix",
            checks = listOf(
                CommandCheck("`git worktree add`가 필요합니다.", listOf(Regex("^git\\s+worktree\\s+add\\b")))
            )
        ),
        Stage(
            id = 15,
            title = "Bundle Export",
            objective = "feature.bundle 파일을 생성하세요.",
            hint = "git bundle create feature.bundle HEAD",
            solution = "git bundle create feature.bundle HEAD",
            checks = listOf(
                CommandCheck("`git bundle create`가 필요합니다.", listOf(Regex("^git\\s+bundle\\s+create\\b")))
            )
        ),
        Stage(
            id = 16,
            title = "Notes Namespace",
            objective = "team 네임스페이스에 note를 추가하세요.",
            hint = "git notes --ref=team add -m 'review'",
            solution = "git notes --ref=team add -m 'review'",
            checks = listOf(
                CommandCheck("`git notes --ref=team add`가 필요합니다.", listOf(Regex("^git\\s+notes\\b.*--ref=team.*\\badd\\b")))
            )
        ),
        Stage(
            id = 17,
            title = "Replace Object",
            objective = "replace ref를 생성하세요.",
            hint = "git replace <bad> <good>",
            solution = "git replace oldhash newhash",
            checks = listOf(
                CommandCheck("`git replace` 명령이 필요합니다.", listOf(Regex("^git\\s+replace\\b")))
            )
        ),
        Stage(
            id = 18,
            title = "Merge Strategy Ours",
            objective = "-X ours 옵션으로 merge 하세요.",
            hint = "git merge -X ours feature-merge",
            solution = "git merge -X ours feature-merge",
            checks = listOf(
                CommandCheck("`git merge -X ours`가 필요합니다.", listOf(Regex("^git\\s+merge\\b.*-x\\s+ours", RegexOption.IGNORE_CASE)))
            )
        ),
        Stage(
            id = 19,
            title = "Merge Then Cleanup Branch",
            objective = "브랜치를 merge 후 삭제하세요.",
            hint = "git branch -d feature-cleanup",
            solution = "git branch -d feature-cleanup",
            checks = listOf(
                CommandCheck("브랜치 삭제 명령이 필요합니다.", listOf(Regex("^git\\s+branch\\s+-d\\s+feature-cleanup\\b")))
            )
        ),
        Stage(
            id = 20,
            title = "Final Amend",
            objective = "마지막 커밋을 amend 하세요.",
            hint = "git commit --amend -m 'Final: ...'",
            solution = "git commit --amend -m 'Final: finish'",
            checks = listOf(
                CommandCheck("`git commit --amend`가 필요합니다.", listOf(Regex("^git\\s+commit\\b.*--amend"))),
                CommandCheck("커밋 메시지에 Final: 이 필요합니다.", listOf(Regex("final:", RegexOption.IGNORE_CASE)))
            )
        )
    )
}
