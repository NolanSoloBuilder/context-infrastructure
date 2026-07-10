# 第一层 01b：Oh My Zsh 配置 Prompt

用途：在第一层系统工具链完成后，让新电脑 Codex 重建一份干净、可审计的 Oh My Zsh 配置。该 Prompt 不复制旧机器的 `.zshrc`，因为旧配置存在重复初始化和已废弃工具引用。

## 目标状态

- Oh My Zsh 来源：`https://github.com/ohmyzsh/ohmyzsh.git`
- 主题：`robbyrussell`
- 内置插件：`git`、`z`、`brew`
- 外部插件：`zsh-autosuggestions`、`zsh-syntax-highlighting`
- Homebrew PATH 只在 `.zprofile` 初始化一次，同时兼容 Apple Silicon 和 Intel。
- Homebrew Node 是唯一全局 Node，不加载 `nvm` 或 `fnm`。
- `pyenv` 只在命令存在时初始化。
- 机器本地扩展统一写到 `~/.config/zsh/local.zsh`，主 `.zshrc` 不放 secrets。

## 给新电脑 Codex 的 Prompt

```text
请直接在这台新 Mac 上安装并配置 Oh My Zsh，完成验证和报告，不要只给我教程。

前置与边界：
1. 这是系统工具链的 01b 子步骤。假设 Xcode Command Line Tools、Git 和 Homebrew 已在 01 层安装；先验证，缺失时停止并指出应该先完成哪一步。
2. 不读取、复制或输出旧机器的 shell 文件、token、API key、SSH key、npmrc、Keychain 或任何 secret。
3. 不安装或初始化 nvm、fnm、jenv、rbenv、Conda、Bun、autojump。
4. 不加入 bundler、dotenv、rake、rbenv、ruby、autojump 插件。尤其不要启用 dotenv 插件自动读取项目 .env。
5. 不使用非官方 Homebrew 镜像，不设置 HOMEBREW_API_DOMAIN 或 HOMEBREW_BOTTLE_DOMAIN。
6. 不使用 curl | sh 安装 Oh My Zsh；使用官方 GitHub 仓库 git clone，避免安装脚本擅自覆盖配置。
7. 不覆盖用户文件而不备份，不把 secret 写入报告。

目标配置：
- Oh My Zsh: https://github.com/ohmyzsh/ohmyzsh.git
- 主题: robbyrussell
- 插件顺序:
  git
  z
  brew
  zsh-autosuggestions
  zsh-syntax-highlighting
- 外部插件官方仓库:
  https://github.com/zsh-users/zsh-autosuggestions
  https://github.com/zsh-users/zsh-syntax-highlighting.git
- 更新策略使用 reminder，不静默自动升级。
- Homebrew Node 是唯一全局 Node 环境。

请按以下顺序执行：

1. 采集安全的安装前状态：
   - sw_vers
   - uname -m
   - echo $SHELL
   - command -v zsh git brew
   - 只判断 ~/.zshrc、~/.zprofile、~/.zshenv、~/.oh-my-zsh 是否存在，不输出文件内容。

2. 创建备份目录：
   ~/Documents/CodexMigration/pre-omz-setup-<timestamp>/
   将已存在的 ~/.zshrc、~/.zprofile 和 ~/.zshenv 原样备份进去，目录权限设为 700。不要把备份提交到 Git。

3. 幂等安装 Oh My Zsh：
   - 若 ~/.oh-my-zsh 不存在，从官方仓库 clone。
   - 若它是正确的官方 Git 仓库，执行安全的 git fetch，并仅在可以 fast-forward 时更新；不要 reset --hard。
   - 若目录存在但不是该仓库，不得删除或覆盖，记录冲突并停止。

4. 幂等安装两个外部插件到 ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/：
   - zsh-autosuggestions
   - zsh-syntax-highlighting
   已存在且 remote 正确时只允许 fast-forward 更新；目录冲突时不要删除。

5. 重建 ~/.zprofile，内容职责仅限登录 shell 环境：
   - Apple Silicon 检测 /opt/homebrew/bin/brew。
   - Intel 检测 /usr/local/bin/brew。
   - 找到后执行对应 brew shellenv。
   - pyenv 存在时执行 eval "$(pyenv init --path)"。
   - 不添加 Homebrew 镜像变量，不添加重复 PATH，不加载 bash 配置。

6. 重建 ~/.zshrc，保持结构简洁且只有一次 Oh My Zsh 初始化：
   - export ZSH="$HOME/.oh-my-zsh"
   - ZSH_THEME="robbyrussell"
   - zstyle ':omz:update' mode reminder
   - plugins=(git z brew zsh-autosuggestions zsh-syntax-highlighting)
   - source "$ZSH/oh-my-zsh.sh"
   - pyenv 存在时执行 eval "$(pyenv init - zsh)"
   - 如果 ~/.config/zsh/local.zsh 存在，则 source 它
   - 不出现第二个 plugins= 或第二次 source oh-my-zsh.sh
   - 不出现 nvm、fnm、jenv、rbenv、Conda、Bun、autojump、source ~/.bash_profile

7. 创建 ~/.config/zsh/local.zsh：
   - 如果不存在，创建为空文件，并加注释说明它只放机器本地、非敏感、按需加载的工具初始化。
   - 如果已经存在，不覆盖。
   - 不创建或迁移 secret 文件。

8. 不主动修改 ~/.zshenv：
   - 若不存在，不创建。
   - 若存在，只报告它可能影响所有 zsh 进程，需要人工 review；不得输出其内容或覆盖它。

9. 默认 shell：
   - 如果当前登录 shell 已是 /bin/zsh，不执行 chsh。
   - 如果不是，只报告建议命令 chsh -s /bin/zsh，不自动触发密码交互。

10. 验证：
   - zsh -n ~/.zprofile
   - zsh -n ~/.zshrc
   - 启动一次干净的 login interactive zsh，确认没有报错。
   - 确认 ZSH、ZSH_THEME 和插件数组符合目标。
   - 确认两个外部插件目录存在且 Git remote 正确。
   - 确认 oh-my-zsh.sh 在 ~/.zshrc 只 source 一次。
   - 确认 ~/.zshrc 不包含上述禁止的旧初始化关键词。
   - 确认 command -v brew、git、node、npm、rg、gh 在新 login shell 中可见。
   - 确认 node/npm 来自 Homebrew 前缀；不要安装另一套 Node manager 来修 PATH。

11. 将执行结果写入：
   ~/Documents/CodexMigration/layer-01b-oh-my-zsh-report.md
   报告只包含文件路径、版本、Git remote、验证状态和待办，不得包含环境变量值、shell 文件全文或 secret。

最终回复必须说明：
- 是否安装或更新了 Oh My Zsh 和两个插件。
- 哪些 shell 文件被备份、重建或保留。
- 语法检查和 login shell smoke test 是否通过。
- 是否发现目录冲突、旧初始化或 PATH 问题。
- report 的绝对路径。
- 明确确认没有迁移 secrets，没有启用 nvm/fnm，没有 source ~/.bash_profile，没有重复加载 Oh My Zsh。

除真实目录冲突、缺失第一层前置工具或系统密码交互外，不要停在计划阶段，执行到验证和报告完成。
```
