# skills_set

个人 Codex skills 管理仓库。这个仓库只保存可复用的个人 skill，不保存 Codex 系统 skill、插件缓存、机器本地配置或临时生成物。

## Skills

- `orchestrator-workers`: Coordinate a GPT-5.5 planning agent with worker53/worker54mini subagents for planning, delegation, review, and integration.
- `professional-book-reading-tutor`: Read, explain, derive formulas from, and create review cards for professional books, textbooks, scanned pages, and dense technical material.

## 目录约定

每个 skill 使用一个独立目录，目录内必须包含 `SKILL.md`：

```text
skills_set/
  orchestrator-workers/
    SKILL.md
    agents/
      openai.yaml
  professional-book-reading-tutor/
    SKILL.md
    references/
      output-template.md
  skills-manifest.json
  manage-skills.py
  install.sh
  install.ps1
  README.md
```

安装脚本会扫描仓库根目录下所有包含 `SKILL.md` 的一级目录，并同步到：

```text
${CODEX_HOME:-$HOME/.codex}/skills
```

不要把这些内容提交进仓库：

- `.system/`
- 插件缓存，例如 `plugins/cache/`
- 机器相关配置
- 临时输出、日志、构建产物

## 远程 WSL/Linux 安装

首次安装：

```bash
git clone https://github.com/toudatouda/skills_set.git ~/skills_set
cd ~/skills_set
./install.sh
```

如果脚本没有执行权限：

```bash
chmod +x ./install.sh
./install.sh
```

安装到自定义 Codex 目录：

```bash
CODEX_HOME="$HOME/.codex" ./install.sh
```

查看将安装哪些 skill：

```bash
./install.sh --list
./install.sh --dry-run
```

安装完成后，重启 Codex，让新 skills 被重新加载。

## 自动查缺补漏

`skills-manifest.json` 是新环境配置清单，包含三类 skill：

- `local`: 本仓库维护的个人 skill，可以自动安装。
- `github`: 有明确 GitHub 来源的外部 skill，可以自动安装。
- `builtin` / `plugin` / `manual`: 只检查和报告，不复制安装。

查看清单和当前安装状态：

```bash
python manage-skills.py list
```

检查新环境缺什么：

```bash
python manage-skills.py doctor
```

自动补装可安装项：

```bash
python manage-skills.py install-missing
```

预览安装动作：

```bash
python manage-skills.py install-missing --dry-run
```

使用自定义 Codex skills 目录：

```bash
python manage-skills.py doctor --dest "$HOME/.codex/skills"
```

Windows 同样可用：

```powershell
python .\manage-skills.py doctor
python .\manage-skills.py install-missing
```

`doctor` 如果发现 required skill 缺失，会返回非零退出码，方便在新机器初始化脚本中使用。系统 skill 会在 `.codex/skills/.system` 下检测，插件 skill 会在 `.codex/plugins/cache` 下检测；缺失时，根据输出安装对应 Codex Desktop 插件、运行时或升级 Codex。

## Windows 本地安装

在 PowerShell 7 中运行：

```powershell
git clone https://github.com/toudatouda/skills_set.git C:\Users\lhsok\skills_set
cd C:\Users\lhsok\skills_set
.\install.ps1
```

查看将安装哪些 skill：

```powershell
.\install.ps1 -List
.\install.ps1 -DryRun
```

安装目标默认是：

```text
C:\Users\<you>\.codex\skills
```

也可以通过 `CODEX_HOME` 指定：

```powershell
$env:CODEX_HOME = "C:\Users\lhsok\.codex"
.\install.ps1
```

安装完成后，重启 Codex。

## 更新流程

在任意机器上更新到最新版本：

```bash
cd ~/skills_set
git pull
./install.sh
```

Windows：

```powershell
cd C:\Users\lhsok\skills_set
git pull
.\install.ps1
```

## 从本地迁移已有个人 skills

迁移时只复制你自己维护的 skill 目录。不要整体复制 `~/.codex` 或 `C:\Users\lhsok\.codex`。

Windows 本地来源通常是：

```text
C:\Users\lhsok\.codex\skills
```

远程 WSL 目标通常是：

```text
~/.codex/skills
```

迁移步骤：

1. 在本机 `C:\Users\lhsok\.codex\skills` 中确认哪些目录是个人 skill。
2. 把这些目录复制到本仓库根目录。
3. 确认每个目录都有 `SKILL.md`。
4. 提交并推送：

```bash
git add .
git commit -m "Add personal skills"
git push
```

5. 在远程 WSL 中 `git pull && ./install.sh`。

## 管理原则

- 仓库是个人 skills 的唯一来源。
- Codex 运行目录 `~/.codex/skills` 是安装结果，不手工维护。
- 更新 skill 后先提交到仓库，再在目标机器运行安装脚本。
- 系统 skills 和插件 skills 由 Codex 或插件机制管理，不放进这个仓库。
- 安装脚本会覆盖同名目标 skill 目录；执行前可用 `--dry-run` 或 `-DryRun` 检查。
