#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="$SCRIPT_DIR/trim.py"
SYSTEM_BIN_DIR="/usr/local/bin"
USER_BIN_DIR="$HOME/.local/bin"
USER_SHELL_RC="$HOME/.zshrc"
PATH_EXPORT='export PATH="$HOME/.local/bin:$PATH"'

chmod +x "$SOURCE_SCRIPT"

if [[ -w "$SYSTEM_BIN_DIR" ]]; then
  TARGET_DIR="$SYSTEM_BIN_DIR"
else
  mkdir -p "$USER_BIN_DIR"
  TARGET_DIR="$USER_BIN_DIR"

  if ! grep -Fqx "$PATH_EXPORT" "$USER_SHELL_RC" 2>/dev/null; then
    printf "\n%s\n" "$PATH_EXPORT" >> "$USER_SHELL_RC"
    echo "La til ~/.local/bin i PATH via $USER_SHELL_RC"
  fi
fi

ln -sf "$SOURCE_SCRIPT" "$TARGET_DIR/trim"
echo "Installert trim -> $TARGET_DIR/trim"

if [[ "$TARGET_DIR" == "$USER_BIN_DIR" ]]; then
  echo "Åpne en ny terminal, eller kjør: source ~/.zshrc"
fi
