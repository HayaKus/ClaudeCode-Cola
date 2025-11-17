cask "claudecode-cola" do
  version "1.0.0"
  sha256 "750144754610c2f7d496853f4979bb31b95fd224bf0ad84b5cd4b64d39f87de5"

  # 直接从 GitLab 下载 DMG，不需要 Git LFS
  url "https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola/-/raw/master/dist/ClaudeCode-Cola-#{version}.dmg",
      verified: "code.alibaba-inc.com"
  name "ClaudeCode-Cola"
  desc "Monitor Claude Code sessions and TodoWrite tasks"
  homepage "https://code.alibaba-inc.com/haya.lhw/ClaudeCode-Cola"

  livecheck do
    url :homepage
    strategy :page_match
    regex(/ClaudeCode-Cola[._-]v?(\d+(?:\.\d+)+)\.dmg/i)
  end

  app "ClaudeCode-Cola.app"

  zap trash: [
    "~/.claudecode-cola",
  ]
end
