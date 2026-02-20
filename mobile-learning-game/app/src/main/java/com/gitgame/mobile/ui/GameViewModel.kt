package com.gitgame.mobile.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import com.gitgame.mobile.data.StageRepository
import com.gitgame.mobile.domain.CommandEvaluator
import com.gitgame.mobile.domain.GitRepositoryEngine
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

data class UiLog(val text: String, val success: Boolean = false)

data class GameUiState(
    val currentStageIndex: Int = 0,
    val terminalLogs: List<UiLog> = listOf(UiLog("Git Learning Mobile에 오신 것을 환영합니다.")),
    val completedCount: Int = 0,
    val showHint: Boolean = false,
    val showSolution: Boolean = false,
    val commandInput: String = "",
    val gameFinished: Boolean = false
)

class GameViewModel(application: Application) : AndroidViewModel(application) {
    private val stages = StageRepository.stages
    private val engine = GitRepositoryEngine(application)

    private val _uiState = MutableStateFlow(GameUiState())
    val uiState: StateFlow<GameUiState> = _uiState.asStateFlow()

    val stageCount: Int = stages.size

    init {
        val stage = stages.first()
        val bootstrap = engine.prepareStage(stage.id)
        _uiState.value = _uiState.value.copy(
            terminalLogs = _uiState.value.terminalLogs + UiLog(bootstrap)
        )
    }

    fun currentStage() = stages[_uiState.value.currentStageIndex]

    fun onCommandChanged(value: String) {
        _uiState.value = _uiState.value.copy(commandInput = value)
    }

    fun runCommand() {
        val state = _uiState.value
        if (state.gameFinished) return

        val stage = stages[state.currentStageIndex]
        val command = state.commandInput
        val engineResult = engine.execute(stage.id, command)
        val (passed, message) = CommandEvaluator.evaluate(stage, command)
        val overallSuccess = engineResult.success && passed

        val newLogs = state.terminalLogs + UiLog(
            text = "$ ${command.trim()}\n${engineResult.output}\n$message",
            success = overallSuccess
        )

        if (!overallSuccess) {
            _uiState.value = state.copy(
                terminalLogs = newLogs,
                commandInput = ""
            )
            return
        }

        val nextIndex = state.currentStageIndex + 1
        val finished = nextIndex >= stages.size
        val stageInitLog = if (!finished) engine.prepareStage(stages[nextIndex].id) else "전체 스테이지 완료"

        _uiState.value = state.copy(
            terminalLogs = newLogs + UiLog(stageInitLog, success = true),
            commandInput = "",
            completedCount = state.completedCount + 1,
            currentStageIndex = if (finished) state.currentStageIndex else nextIndex,
            showHint = false,
            showSolution = false,
            gameFinished = finished
        )
    }

    fun toggleHint() {
        val state = _uiState.value
        _uiState.value = state.copy(showHint = !state.showHint)
    }

    fun toggleSolution() {
        val state = _uiState.value
        _uiState.value = state.copy(showSolution = !state.showSolution)
    }

    fun resetCurrentStage() {
        val state = _uiState.value
        val stage = stages[state.currentStageIndex]
        val resetMessage = engine.prepareStage(stage.id)

        _uiState.value = state.copy(
            terminalLogs = state.terminalLogs + UiLog(resetMessage),
            commandInput = "",
            showHint = false,
            showSolution = false
        )
    }

    fun restartGame() {
        val bootstrap = engine.prepareStage(stages.first().id)
        _uiState.value = GameUiState(
            terminalLogs = listOf(UiLog("새 게임을 시작했습니다."), UiLog(bootstrap))
        )
    }
}
