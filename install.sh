#!/data/data/com.termux/files/usr/bin/bash
set -e

APP_DIR="$HOME/.termux-ai"
BIN_DIR="$PREFIX/bin"
REPO_URL="https://github.com/mohmb142/Tol-Termux-.git"

printf '\n🤖 تثبيت Tol-Termux AI Agent\n\n'

pkg update -y
pkg install -y python python-pip git curl

if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull --ff-only
else
  rm -rf "$APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
fi

# Termux manages pip through python-pip; do not self-upgrade pip.
python -m pip install -r "$APP_DIR/requirements.txt"

printf '\n🔑 إعداد OpenRouter\n'
printf 'أدخل OpenRouter API Key (يُحفظ محليًا في ~/.termux-ai/.env): '
read -r OPENROUTER_API_KEY
if [ -z "$OPENROUTER_API_KEY" ]; then
  echo '❌ لم يتم إدخال مفتاح API.'
  exit 1
fi

printf 'اسم النموذج [openrouter/free]: '
read -r OPENROUTER_MODEL
OPENROUTER_MODEL=${OPENROUTER_MODEL:-openrouter/free}

cat > "$APP_DIR/.env" <<EOF
OPENROUTER_API_KEY=$OPENROUTER_API_KEY
OPENROUTER_MODEL=$OPENROUTER_MODEL
EOF
chmod 600 "$APP_DIR/.env"

cat > "$BIN_DIR/termux-ai" <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "$HOME/.termux-ai"
exec python -m termux_ai.main "$@"
EOF
chmod +x "$BIN_DIR/termux-ai"

printf '\n✅ اكتمل التثبيت.\n'
printf 'شغّل الأداة بالأمر: termux-ai\n'
printf 'لتغيير المفتاح أو النموذج: nano ~/.termux-ai/.env\n\n'
