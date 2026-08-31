#!/usr/bin/env bash
# مشغّل مختصر لتشغيل الـ workflow.
# الاستخدام: ./run.sh   أو   ./run.sh --dry-run
cd "$(dirname "$0")" || exit 1
python3 main.py "$@"
