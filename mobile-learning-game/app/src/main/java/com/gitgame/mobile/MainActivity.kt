package com.gitgame.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.gitgame.mobile.ui.GameViewModel
import com.gitgame.mobile.ui.theme.GitLearningMobileTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            GitLearningMobileTheme {
                GitGameScreen()
            }
        }
    }
}

@Composable
fun GitGameScreen(vm: GameViewModel = viewModel()) {
    val state by vm.uiState.collectAsState()
    val stage = vm.currentStage()

    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Git Learning Mobile",
                style = MaterialTheme.typography.headlineSmall
            )
            Text(
                text = "진행률 ${state.completedCount}/${vm.stageCount}",
                style = MaterialTheme.typography.bodyMedium
            )

            if (!state.gameFinished) {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(text = "Stage ${stage.id}: ${stage.title}", style = MaterialTheme.typography.titleMedium)
                        Text(text = stage.objective, style = MaterialTheme.typography.bodyMedium)
                        if (state.showHint) {
                            Text(text = "Hint: ${stage.hint}", color = MaterialTheme.colorScheme.primary)
                        }
                        if (state.showSolution) {
                            Text(text = "Solution: ${stage.solution}", color = MaterialTheme.colorScheme.tertiary)
                        }
                    }
                }

                OutlinedTextField(
                    value = state.commandInput,
                    onValueChange = vm::onCommandChanged,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Git command") },
                    singleLine = true
                )

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(onClick = vm::runCommand) { Text("실행") }
                    OutlinedButton(onClick = vm::toggleHint) { Text("힌트") }
                    OutlinedButton(onClick = vm::toggleSolution) { Text("정답") }
                    OutlinedButton(onClick = vm::resetCurrentStage) { Text("초기화") }
                }
            } else {
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text("모든 스테이지를 완료했습니다.", style = MaterialTheme.typography.titleMedium)
                        Text("총 20개 스테이지 완료", style = MaterialTheme.typography.bodyLarge)
                        Button(onClick = vm::restartGame) { Text("다시 시작") }
                    }
                }
            }

            Text("Terminal", style = MaterialTheme.typography.titleMedium)
            LazyColumn(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
                    .background(Color(0xFF0F172A), RoundedCornerShape(12.dp)),
                contentPadding = PaddingValues(12.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(state.terminalLogs) { log ->
                    Text(
                        text = log.text,
                        fontFamily = FontFamily.Monospace,
                        color = if (log.success) Color(0xFF86EFAC) else Color(0xFFE2E8F0)
                    )
                }
            }
            Spacer(modifier = Modifier.height(2.dp))
        }
    }
}
