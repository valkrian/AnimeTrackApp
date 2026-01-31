# Git Workflow for Task-Based Development

## Branch Naming Convention

For each task from the seasonal-anime-tracker spec, create a branch using this format:
```
task/{task-number}-{task-name-kebab-case}
```

### Examples:
- `task/1-backend-foundation-setup` ✅ (completed)
- `task/2-external-api-integration`
- `task/3-api-routes-cors-config`
- `task/4-backend-checkpoint`
- `task/5-frontend-foundation-setup`

## Workflow Steps

### 1. Starting a New Task
```bash
# Create and switch to new task branch from current branch
git checkout -b task/{number}-{name}
```

### 2. During Development
```bash
# Regular commits with descriptive messages
git add .
git commit -m "feat: implement {specific feature}

- Detail 1
- Detail 2
- Requirements satisfied: X.X, Y.Y"
```

### 3. Completing a Task
```bash
# Push the task branch
git push -u origin task/{number}-{name}
```

### 4. Task Completion Commit Format
```
feat: {task title}

- {implementation detail 1}
- {implementation detail 2}
- {implementation detail 3}

Completes task {number} from seasonal-anime-tracker spec
Requirements satisfied: {requirement numbers}
```

## Branch Management

- **main**: Production-ready code
- **task/***: Individual task development
- **feature/***: Multi-task features (if needed)
- **hotfix/***: Emergency fixes

## Current Status

✅ **Task 1**: Backend Foundation Setup (task/1-backend-foundation-setup)
- FastAPI project structure
- Configuration management
- Dependencies setup

🔄 **Next**: Task 2 - External API Integration and Caching

## Notes

- Each task gets its own branch for clean development
- Commit messages follow conventional commit format
- All task branches are pushed to remote for backup
- Requirements traceability maintained in commit messages