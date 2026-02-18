# 스테이지 템플릿 초안

아래 템플릿은 `backend/stages.py` 구조를 유지하면서, 협업 시나리오/힌트/해답/재도전 규칙을 명확히 정의하기 위한 초안이다.

## 스테이지 정의 템플릿 (구조)

```
{
  "stage_id": <number>,
  "title": "<짧은 제목>",
  "description": "<한 문장 요약>",
  "difficulty": "basic | intermediate | advanced",

  "story": {
    "context": "<협업 상황 요약>",
    "teammate": "<가상 협력자 이름/역할>",
    "incident": "<문제 발생 계기: 충돌/누락/잘못된 커밋 등>"
  },

  "objectives": [
    "<유저가 수행해야 할 구체 행동 1>",
    "<유저가 수행해야 할 구체 행동 2>",
    "<유저가 수행해야 할 구체 행동 3>"
  ],

  "constraints": [
    "<금지/제약: merge 금지, rebase만 허용 등>",
    "<허용 커맨드/옵션 제한>"
  ],

  "initial_files": {
    "<path>": "<content>"
  },

  "initial_commits": [
    {"message": "<msg>", "files": {"<path>": "<content>"}}
  ],

  "initial_branches": [
    {
      "name": "<branch-name>",
      "checkout": true|false,
      "commits": [
        {"message": "<msg>", "files": {"<path>": "<content>"}}
      ]
    }
  ],

  "collaboration_events": [
    {
      "trigger": "<stage-start | after-command | after-commit>",
      "action": "<create-commit | create-branch | force-conflict>",
      "message": "<협력자 메시지>"
    }
  ],

  "validation": {
    "must_have": [
      {"type": "<rule-type>", "value": "<rule-value>"}
    ],
    "must_not_have": [
      {"type": "<rule-type>", "value": "<rule-value>"}
    ]
  },

  "hint": "<짧은 힌트>",
  "solution": "<명령 시퀀스 요약>",

  "retry_policy": {
    "on_hint_or_solution": "repeat_same_stage_once",
    "recording": "new_session_with_repeat_flag"
  }
}
```

## 예시 A: Cherry-pick 충돌 해결

```
{
  "stage_id": 21,
  "title": "Cherry-pick Conflict Drill",
  "description": "협력자의 변경을 cherry-pick하고 충돌을 해결한다",
  "difficulty": "intermediate",

  "story": {
    "context": "동료가 hotfix 브랜치에서 급히 수정했다",
    "teammate": "Mina (backend)",
    "incident": "동일 파일에 서로 다른 수정이 있어 충돌이 발생"
  },

  "objectives": [
    "hotfix 브랜치의 커밋을 cherry-pick 한다",
    "충돌을 올바르게 해결한다",
    "커밋 메시지를 팀 규칙대로 정리한다"
  ],

  "constraints": [
    "merge 금지",
    "cherry-pick --no-commit 사용 금지"
  ],

  "initial_files": {
    "config.py": "DEBUG = False\nVERSION = '1.1'\n"
  },

  "initial_commits": [
    {"message": "Baseline config", "files": {"config.py": "DEBUG = False\nVERSION = '1.1'\n"}}
  ],

  "initial_branches": [
    {
      "name": "hotfix",
      "checkout": false,
      "commits": [
        {"message": "Hotfix: enable debug temporarily", "files": {"config.py": "DEBUG = True\nVERSION = '1.1'\n"}}
      ]
    }
  ],

  "collaboration_events": [
    {
      "trigger": "stage-start",
      "action": "create-commit",
      "message": "Mina: hotfix 커밋했어. 지금 바로 가져와야 해."
    }
  ],

  "validation": {
    "must_have": [
      {"type": "head_message_contains", "value": "Hotfix:"},
      {"type": "file_contains", "path": "config.py", "value": "DEBUG = True"}
    ],
    "must_not_have": [
      {"type": "has_merge_commits"}
    ]
  },

  "hint": "cherry-pick 이후 충돌 파일을 직접 수정한 다음 `git add`와 `git cherry-pick --continue`.",
  "solution": "git cherry-pick <hotfix-commit> -> resolve -> git add -> git cherry-pick --continue",

  "retry_policy": {
    "on_hint_or_solution": "repeat_same_stage_once",
    "recording": "new_session_with_repeat_flag"
  }
}
```

## 예시 B: Interactive Rebase 정리

```
{
  "stage_id": 22,
  "title": "Team Rebase Cleanup",
  "description": "협업 브랜치의 잡다한 커밋을 정리한다",
  "difficulty": "intermediate",

  "story": {
    "context": "PR을 올리기 전에 커밋 히스토리를 정리해야 한다",
    "teammate": "Joon (reviewer)",
    "incident": "작업 중 커밋이 너무 잘게 쪼개졌다"
  },

  "objectives": [
    "최근 4개의 커밋을 2개로 squash 한다",
    "최종 커밋 메시지를 규칙에 맞게 변경한다"
  ],

  "constraints": [
    "merge 금지",
    "rebase -i만 허용"
  ],

  "initial_commits": [
    {"message": "Add feature flag", "files": {"feature.py": "FLAG = False\n"}},
    {"message": "WIP: tweak flag", "files": {"feature.py": "FLAG = True\n"}},
    {"message": "Refactor flag logic", "files": {"feature.py": "def enabled():\n    return True\n"}},
    {"message": "Fix typo", "files": {"feature.py": "def enabled():\n    return True\n"}}
  ],

  "collaboration_events": [
    {
      "trigger": "stage-start",
      "action": "create-branch",
      "message": "Joon: 커밋이 너무 많아. 2개로 정리해줘."
    }
  ],

  "validation": {
    "must_have": [
      {"type": "commit_count_at_most", "value": 2, "max_count": 2},
      {"type": "head_message_contains", "value": "Feature:"}
    ],
    "must_not_have": [
      {"type": "has_merge_commits"}
    ]
  },

  "hint": "git rebase -i HEAD~4 후 pick/squash로 2개만 남긴다.",
  "solution": "git rebase -i HEAD~4 -> squash -> 메시지 수정",

  "retry_policy": {
    "on_hint_or_solution": "repeat_same_stage_once",
    "recording": "new_session_with_repeat_flag"
  }
}
```
