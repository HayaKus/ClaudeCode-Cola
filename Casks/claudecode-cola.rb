cask "claudecode-cola" do
  version "1.0.1"
  sha256 "7a877d112f65a46df8aa57c24538b34b85aee5c302e2c0fce84e1add0b3d2c25"

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
