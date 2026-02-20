package com.gitgame.mobile.domain

data class Stage(
    val id: Int,
    val title: String,
    val objective: String,
    val hint: String,
    val solution: String,
    val checks: List<CommandCheck>
)

data class CommandCheck(
    val description: String,
    val patterns: List<Regex>
)
