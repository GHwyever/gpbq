#!/bin/bash
# 番茄小说下载器启动脚本
# 使用方法: ./run.sh <书籍ID或URL>

cd "$(dirname "$0")"

if [ -z "$1" ]; then
    echo "用法: ./run.sh <书籍ID或URL>"
    echo "示例:"
    echo "  ./run.sh 7143038691944959011"
    echo "  ./run.sh https://fanqienovel.com/page/7143038691944959011"
    exit 1
fi

# 检查依赖
pip install requests lxml beautifulsoup4 --break-system-packages -q 2>/dev/null

# 运行下载器
python3 run.py "$1"
