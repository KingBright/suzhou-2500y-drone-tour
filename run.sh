#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="${ROOT_DIR}/web"
PORT="${PORT:-4173}"
MODE="${1:-preview}"

case "${MODE}" in
  dev)
    echo ">>> 启动开发服务器 (http://127.0.0.1:${PORT})"
    cd "${WEB_DIR}"
    exec npx vite --host 127.0.0.1 --port "${PORT}"
    ;;
  build)
    echo ">>> 编译生产包..."
    cd "${WEB_DIR}"
    npm run build
    echo ">>> 构建完成: ${WEB_DIR}/dist"
    ;;
  rebuild)
    echo ">>> 编译并启动预览服务器 (http://127.0.0.1:${PORT})"
    cd "${WEB_DIR}"
    npm run build
    exec npx vite preview --host 127.0.0.1 --port "${PORT}"
    ;;
  video)
    echo ">>> 编译并渲染 720p 30fps 无人机大片 MP4..."
    cd "${WEB_DIR}"
    npm run build
    exec node "${ROOT_DIR}/qa/render_video.mjs"
    ;;
  preview|*)
    cd "${WEB_DIR}"
    if [[ ! -d "${WEB_DIR}/dist" ]]; then
      echo ">>> 未检测到 dist，先执行构建..."
      npm run build
    fi
    echo ">>> 启动一镜飞越2500年苏州 3D 预览 (http://127.0.0.1:${PORT})"
    exec npx vite preview --host 127.0.0.1 --port "${PORT}"
    ;;
esac
