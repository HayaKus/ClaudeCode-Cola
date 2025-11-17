cask "claudecode-cola" do
  version "1.0.0"
  sha256 "YOUR_SHA256_HERE"  # 使用 shasum -a 256 dist/ClaudeCode-Cola-1.0.0.dmg 计算

  url "https://your-server.com/ClaudeCode-Cola-#{version}.dmg"
  name "ClaudeCode-Cola"
  desc "Monitor Claude Code sessions and TodoWrite tasks"
  homepage "https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola"

  livecheck do
    url :homepage
    strategy :github_latest
  end

  app "ClaudeCode-Cola.app"

  zap trash: [
    "~/.claudecode-cola",
  ]
end
