#!/usr/bin/env sh
set -eu

BRANCH="arena/75760c53-adelina"
ARENA_URL="https://github.com/a24415858-sketch/adelina.git"
SAIT_URL="https://github.com/a24415858-sketch/sait.git"
MESSAGE="${1:-chore: sync project changes}"

# Arena восстанавливает локальный .git между ходами, поэтому remotes
# настраиваются заново при каждой синхронизации.
gh auth setup-git >/dev/null 2>&1 || true

if ! git remote | grep -qx arena-origin; then
    git remote add arena-origin "$ARENA_URL"
fi
if ! git remote | grep -qx origin; then
    git remote add origin "$SAIT_URL"
fi

git remote set-url arena-origin "$ARENA_URL"
git remote set-url origin "$SAIT_URL"

# Подтягиваем уже опубликованную историю и аккуратно накладываем на неё
# текущее рабочее дерево без force-push.
git fetch arena-origin "+$BRANCH:refs/remotes/arena-origin/$BRANCH"
git reset --soft "refs/remotes/arena-origin/$BRANCH"
git add -A

if git diff --cached --quiet; then
    echo "Nothing to commit."
else
    git commit -m "$MESSAGE"
fi

git push -u arena-origin "$BRANCH"

# Новый origin может быть недоступен, пока GitHub App не получил доступ
# к созданному вручную репозиторию sait.
if git push -u origin "$BRANCH"; then
    echo "Pushed to origin (sait)."
    gh api --method PATCH repos/a24415858-sketch/sait \
        -f default_branch="$BRANCH" >/dev/null 2>&1 || true
else
    echo "WARNING: push to origin (sait) is blocked; changes are safe in arena-origin." >&2
    exit 0
fi
