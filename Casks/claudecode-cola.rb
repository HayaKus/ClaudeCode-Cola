cask "claudecode-cola" do
  version "1.0.1"
  sha256 :no_check

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
