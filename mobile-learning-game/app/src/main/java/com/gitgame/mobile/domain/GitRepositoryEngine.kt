package com.gitgame.mobile.domain

import android.app.Application
import org.eclipse.jgit.api.Git
import org.eclipse.jgit.lib.ObjectId
import org.eclipse.jgit.lib.Repository
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

data class EngineResult(
    val success: Boolean,
    val output: String
)

class GitRepositoryEngine(private val application: Application) {
    private var git: Git? = null
    private var currentStageId: Int = -1
    private var repoDir: File? = null

    fun prepareStage(stageId: Int): String {
        currentStageId = stageId
        val baseDir = File(application.cacheDir, "git-learning-mobile")
        val stageDir = File(baseDir, "stage-$stageId")
        if (stageDir.exists()) {
            stageDir.deleteRecursively()
        }
        stageDir.mkdirs()

        git = Git.init().setDirectory(stageDir).call()
        repoDir = stageDir
        configureUser()
        seedBaseRepo(stageId)

        return "Stage $stageId 저장소를 초기화했습니다."
    }

    fun execute(stageId: Int, rawCommand: String): EngineResult {
        if (git == null || stageId != currentStageId) {
            prepareStage(stageId)
        }

        val command = rawCommand.trim()
        if (command.isEmpty()) {
            return EngineResult(false, "명령어를 입력하세요.")
        }
        if (!command.startsWith("git ")) {
            return EngineResult(false, "모바일 버전은 git 명령만 지원합니다.")
        }

        return try {
            runGitCommand(command)
        } catch (e: Exception) {
            EngineResult(false, "실행 실패: ${e.message}")
        }
    }

    private fun runGitCommand(command: String): EngineResult {
        val g = git ?: return EngineResult(false, "저장소가 초기화되지 않았습니다.")

        return when {
            Regex("^git\\s+status\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val status = g.status().call()
                val tracked = status.added + status.changed + status.modified + status.removed
                EngineResult(true, "On branch ${currentBranch()} | changed=${tracked.size} untracked=${status.untracked.size}")
            }
            Regex("^git\\s+log\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val log = g.log().setMaxCount(5).call().joinToString("\n") {
                    "${it.name.take(7)} ${it.shortMessage}"
                }
                EngineResult(true, if (log.isBlank()) "커밋이 없습니다." else log)
            }
            Regex("^git\\s+(checkout\\s+-b|switch\\s+-c)\\s+", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val branch = command.split(Regex("\\s+")).lastOrNull()
                if (branch.isNullOrBlank()) return EngineResult(false, "브랜치 이름이 필요합니다.")
                g.checkout().setCreateBranch(true).setName(branch).call()
                EngineResult(true, "새 브랜치 생성: $branch")
            }
            Regex("^git\\s+checkout\\s+", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val branch = command.substringAfter("checkout").trim().split(" ").firstOrNull()
                if (branch.isNullOrBlank()) return EngineResult(false, "체크아웃 대상이 필요합니다.")
                g.checkout().setName(branch).call()
                EngineResult(true, "브랜치 전환: $branch")
            }
            Regex("^git\\s+add\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val filePattern = command.substringAfter("add").trim().ifEmpty { "." }
                g.add().addFilepattern(filePattern).call()
                EngineResult(true, "staged: $filePattern")
            }
            Regex("^git\\s+commit\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val message = extractCommitMessage(command) ?: defaultCommitMessage()
                ensureSomethingToCommit(g)
                g.commit().setMessage(message).setAllowEmpty(false).call()
                EngineResult(true, "commit 완료: $message")
            }
            Regex("^git\\s+tag\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val name = extractTagName(command)
                if (name.isNullOrBlank()) return EngineResult(false, "태그 이름이 필요합니다.")
                val msg = extractCommitMessage(command) ?: "release $name"
                g.tag().setName(name).setMessage(msg).call()
                EngineResult(true, "태그 생성: $name")
            }
            Regex("^git\\s+cherry-pick\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val ref = command.substringAfter("cherry-pick").trim().split(" ").firstOrNull()
                if (ref.isNullOrBlank()) return EngineResult(false, "cherry-pick 대상이 필요합니다.")
                val id = resolve(ref) ?: return EngineResult(false, "참조를 찾을 수 없습니다: $ref")
                EngineResult(true, "cherry-pick 대상 확인: ${id.name.take(7)} (학습 모드 반영)")
            }
            Regex("^git\\s+merge\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val ref = command.substringAfter("merge").trim().split(" ").lastOrNull()
                if (ref.isNullOrBlank()) return EngineResult(false, "merge 대상이 필요합니다.")
                val id = resolve(ref) ?: return EngineResult(false, "참조를 찾을 수 없습니다: $ref")
                EngineResult(true, "merge 대상 확인: ${id.name.take(7)} (학습 모드 반영)")
            }
            Regex("^git\\s+revert\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val ref = command.substringAfter("revert").trim().split(" ").firstOrNull()
                if (ref.isNullOrBlank()) return EngineResult(false, "revert 대상이 필요합니다.")
                val id = resolve(ref) ?: return EngineResult(false, "참조를 찾을 수 없습니다: $ref")
                EngineResult(true, "revert 대상 확인: ${id.name.take(7)} (학습 모드 반영)")
            }
            Regex("^git\\s+branch\\s+-d\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                val branch = command.substringAfter("-d").trim().split(" ").firstOrNull()
                if (branch.isNullOrBlank()) return EngineResult(false, "삭제할 브랜치 이름이 필요합니다.")
                g.branchDelete().setBranchNames(branch).setForce(false).call()
                EngineResult(true, "브랜치 삭제: $branch")
            }
            Regex("^git\\s+stash\\b", RegexOption.IGNORE_CASE).containsMatchIn(command) -> {
                g.stashCreate().call()
                EngineResult(true, "stash 생성 완료")
            }
            else -> EngineResult(
                true,
                "해당 git 명령은 JGit 완전 실행 대상이 아니어서 학습 모드로 처리했습니다."
            )
        }
    }

    private fun configureUser() {
        val repository = git?.repository ?: return
        repository.config.setString("user", null, "name", "Mobile Learner")
        repository.config.setString("user", null, "email", "mobile@example.com")
        repository.config.save()
    }

    private fun seedBaseRepo(stageId: Int) {
        val g = git ?: return
        writeFile("README.md", "# Stage $stageId\n")
        g.add().addFilepattern("README.md").call()
        g.commit().setMessage("Initial stage $stageId").call()
        ensureMainBranch(g)

        when (stageId) {
            1 -> {
                g.checkout().setCreateBranch(true).setName("hotfix").call()
                writeFile("README.md", "# Stage $stageId\nhotfix=true\n")
                g.add().addFilepattern("README.md").call()
                g.commit().setMessage("Hotfix: enable runtime patch").call()
                g.checkout().setName("main").call()
            }
            3 -> {
                g.checkout().setCreateBranch(true).setName("feature-ui").call()
                writeFile("ui.txt", "mode=feature\n")
                g.add().addFilepattern("ui.txt").call()
                g.commit().setMessage("UI tweak").call()
                g.checkout().setName("main").call()
                writeFile("ui.txt", "mode=main\n")
                g.add().addFilepattern("ui.txt").call()
                g.commit().setMessage("Main hardening").call()
            }
            5 -> {
                g.checkout().setCreateBranch(true).setName("release").call()
                writeFile("service.py", "def add(a,b):\n    return a+b\n")
                g.add().addFilepattern("service.py").call()
                g.commit().setMessage("Release prep").call()
                g.checkout().setName("main").call()
            }
            9 -> {
                g.checkout().setCreateBranch(true).setName("feature-range").call()
                writeFile("config.py", "ENABLED=true\n")
                g.add().addFilepattern("config.py").call()
                g.commit().setMessage("Feature: add config").call()
                g.checkout().setName("main").call()
            }
            10 -> {
                writeFile("calc.py", "def add(a,b):\n    return a+b+1\n")
                g.add().addFilepattern("calc.py").call()
                g.commit().setMessage("Bad commit: off by one").call()
            }
            18 -> {
                g.checkout().setCreateBranch(true).setName("feature-merge").call()
                writeFile("config.yml", "mode: feature\n")
                g.add().addFilepattern("config.yml").call()
                g.commit().setMessage("Feature config").call()
                g.checkout().setName("main").call()
                writeFile("config.yml", "mode: main\n")
                g.add().addFilepattern("config.yml").call()
                g.commit().setMessage("Main stable config").call()
            }
            19 -> {
                g.checkout().setCreateBranch(true).setName("feature-cleanup").call()
                writeFile("cleanup.txt", "done\n")
                g.add().addFilepattern("cleanup.txt").call()
                g.commit().setMessage("Cleanup done").call()
                g.checkout().setName("main").call()
            }
        }
    }

    private fun writeFile(name: String, content: String) {
        val base = repoDir ?: return
        val file = File(base, name)
        file.parentFile?.mkdirs()
        file.writeText(content)
    }

    private fun ensureMainBranch(g: Git) {
        val current = currentBranch()
        if (current != "main") {
            g.branchRename().setNewName("main").call()
        }
    }

    private fun extractCommitMessage(command: String): String? {
        val single = Regex("-m\\s+'([^']+)'").find(command)?.groupValues?.get(1)
        val double = Regex("-m\\s+\"([^\"]+)\"").find(command)?.groupValues?.get(1)
        return single ?: double
    }

    private fun extractTagName(command: String): String? {
        val parts = command.split(Regex("\\s+"))
        if (parts.size < 3) return null
        return parts.drop(2).firstOrNull { token ->
            !token.startsWith("-") && token != "-m"
        }
    }

    private fun defaultCommitMessage(): String {
        val stamp = SimpleDateFormat("HH:mm:ss", Locale.US).format(Date())
        return "Mobile commit $stamp"
    }

    private fun ensureSomethingToCommit(g: Git) {
        val status = g.status().call()
        val dirty = status.added.isNotEmpty() ||
            status.changed.isNotEmpty() ||
            status.modified.isNotEmpty() ||
            status.untracked.isNotEmpty() ||
            status.removed.isNotEmpty()

        if (!dirty) {
            writeFile("journal.txt", "tick=${System.currentTimeMillis()}\n")
            g.add().addFilepattern("journal.txt").call()
        }
    }

    private fun resolve(ref: String): ObjectId? {
        val repository: Repository = git?.repository ?: return null
        return repository.resolve(ref)
    }

    private fun currentBranch(): String {
        val repository: Repository = git?.repository ?: return "unknown"
        return repository.branch
    }
}
