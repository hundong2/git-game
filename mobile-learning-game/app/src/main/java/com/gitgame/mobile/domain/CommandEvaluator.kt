package com.gitgame.mobile.domain

object CommandEvaluator {
    fun evaluate(stage: Stage, command: String): Pair<Boolean, String> {
        val normalized = command.trim().lowercase()
        if (normalized.isEmpty()) {
            return false to "명령어를 입력하세요."
        }

        for (check in stage.checks) {
            val passed = check.patterns.any { it.containsMatchIn(normalized) }
            if (!passed) {
                return false to check.description
            }
        }
        return true to "스테이지 ${stage.id} 완료"
    }
}
