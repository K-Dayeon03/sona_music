#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

section() {
  printf "\n==> %s\n" "$1"
}

check_dangerous_paths() {
  local paths
  paths="$(git ls-files && git diff --cached --name-only)"

  if printf "%s\n" "$paths" | grep -E '(^|/)(\.env$|\.venv/|node_modules/|dist/|build/|\.sona/|\.idea/)|\.sqlite3$' >/dev/null; then
    printf "%s\n" "커밋하면 안 되는 파일이 git 추적/스테이징 목록에 포함되어 있습니다:"
    printf "%s\n" "$paths" | grep -E '(^|/)(\.env$|\.venv/|node_modules/|dist/|build/|\.sona/|\.idea/)|\.sqlite3$'
    exit 1
  fi
}

python_bin() {
  if [[ -x "$ROOT_DIR/backend/.venv/bin/python" ]]; then
    printf "%s\n" "$ROOT_DIR/backend/.venv/bin/python"
  else
    printf "%s\n" "python3"
  fi
}

section "위험 파일 검사"
check_dangerous_paths

section "공백 오류 검사"
git diff --check

PYTHON_BIN="$(python_bin)"

section "백엔드 문법 검사"
"$PYTHON_BIN" -m compileall backend/app

section "백엔드 앱 import 확인"
(
  cd backend
  "$PYTHON_BIN" -c "from app.main import app; print(app.title)"
)

section "프론트엔드 빌드"
npm --prefix frontend run build

section "완료"
printf "%s\n" "커밋 전 검사 통과"
