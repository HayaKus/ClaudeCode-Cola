#!/bin/bash

# 推送主仓库到所有远程
echo "=== 推送主仓库 ==="
cd ~/Code/ClaudeCode-Cola

echo "推送到内网 GitLab..."
git push origin master

echo "推送到 GitHub..."
git push github master

echo ""
echo "=== 推送 Tap 仓库 ==="
cd ~/Code/homebrew-claudecode-cola

echo "推送到内网 GitLab..."
git push origin master

echo "推送到 GitHub..."
git push github master

echo ""
echo "✅ 所有代码已推送到内网和 GitHub！"
