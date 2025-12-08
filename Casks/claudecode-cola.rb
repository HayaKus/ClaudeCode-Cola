cask "claudecode-cola" do
  version "1.0.2"
  sha256 "8679d235d7050f855ed58f0b06b047a37a0deee6608ef350052cde439ff32d47"

  url "https://github.com/HayaKus/ClaudeCode-Cola/releases/download/v#{version}/ClaudeCode-Cola-#{version}.dmg"
  name "ClaudeCode-Cola"
  desc "Monitor Claude Code sessions and TodoWrite tasks"
  homepage "https://github.com/HayaKus/ClaudeCode-Cola"

  livecheck do
    url :url
    strategy :github_latest
  end

  app "ClaudeCode-Cola.app"

  zap trash: [
    "~/.claudecode-cola",
  ]
end
