# Agent Skills

个人维护的 coding agent skills 集合。每个 skill 都是一个独立目录，
包含 `SKILL.md` 以及可选的脚本和参考资料。

这些 skills 遵循 Agent Skills 格式，可通过
[`skills`](https://github.com/vercel-labs/skills) CLI 安装到 Codex、
Claude Code 等 coding agents。

## Skills

| Skill | 说明 |
| --- | --- |
| `chinese-doc-style` | 统一中文和中英文混排文档格式 |
| `git-crypt` | 在 Git 仓库中配置和使用 `git-crypt` |
| `git-commit-writer` | 检查改动并创建严格的 Conventional Commit |
| `humanizer` | 去除英文文本中的 AI 写作痕迹 |
| `humanizer-zh` | 去除中文文本中的 AI 写作痕迹 |
| `macos-input-method` | 使用 InputMethodKit 开发 macOS 输入法 |

## 使用 npx skills 安装

先查看仓库中可安装的 skills：

```bash
npx skills add erning/agent-skills --list
```

交互式安装指定 skill：

```bash
npx skills add erning/agent-skills --skill git-commit-writer
```

全局安装到 Codex 和 Claude Code：

```bash
npx skills add erning/agent-skills \
  --skill git-commit-writer \
  --global \
  --agent codex \
  --agent claude-code \
  --yes
```

安装全部 skills：

```bash
npx skills add erning/agent-skills \
  --skill '*' \
  --global \
  --agent codex \
  --agent claude-code \
  --yes
```

不使用 `--global` 时，skill 默认安装到当前项目。项目级安装适合将
skill 配置随项目提交；全局安装则让该用户的所有项目都能使用。

## 从本地仓库安装

Clone 本仓库后，可以直接从本地路径安装：

```bash
git clone https://github.com/erning/agent-skills.git
cd agent-skills

npx skills add . --list
npx skills add . --skill git-commit-writer --global
```

也可以直接指定单个 skill 目录：

```bash
npx skills add ./git-commit-writer --global
```

## 管理已安装的 skills

```bash
# 查看项目级和全局 skills
npx skills list

# 仅查看全局 skills
npx skills list --global

# 更新全局 skills
npx skills update --global

# 删除全局 skill
npx skills remove --global git-commit-writer
```

安装或更新后，如果 coding agent 没有立即发现 skill，请重新启动
对应的 agent 或新建会话。

## 手动安装

不使用 `npx skills` 时，也可以将 skill 目录复制或链接到 agent 的
发现目录：

```text
Codex project:       .agents/skills/
Codex global:        ~/.agents/skills/
Claude Code project: .claude/skills/
Claude Code global:  ~/.claude/skills/
```

例如：

```bash
ln -s /absolute/path/to/git-commit-writer \
  ~/.claude/skills/git-commit-writer
```

使用 skill 前，请先检查其 `SKILL.md`、脚本和依赖。

## 同步上游 skills

[`upstreams.json`](upstreams.json) 记录通过 squash
Git subtree 保存在本仓库中的第三方 skills：

| 目录 | 上游 |
| --- | --- |
| `humanizer/` | [`blader/humanizer`][humanizer] |
| `Humanizer-zh/` | [`op7418/Humanizer-zh`][humanizer-zh] |

[humanizer]: https://github.com/blader/humanizer
[humanizer-zh]: https://github.com/op7418/Humanizer-zh

subtree 会把完整文件保存在本仓库中，因此普通 clone 和
`npx skills` 安装都不需要初始化 submodule。

同步所有上游 skills：

```bash
just sync
```

也可以只同步一个：

```bash
just sync humanizer
just sync humanizer-zh
```

查看配置中所有第三方 skills：

```bash
just list
```

运行不带参数的 `just` 可以查看所有可用命令。以上 recipes 调用
`scripts/sync-upstream-skills.sh`，也可以直接执行该脚本。

增加第三方 skill 时，在 `upstreams.json` 中以 skill name 为 key
添加一项：

```json
{
  "example-skill": {
    "target_path": "example-skill",
    "repository": "https://github.com/OWNER/REPO.git",
    "ref": "main",
    "source_path": "skills/example-skill"
  }
}
```

字段含义：

- 顶层 key：同步命令使用的名称，也是 Conventional Commit 的 scope
- `target_path`：skill 同步到本仓库后的目录，可省略；默认与顶层
  key 相同
- `repository`：上游 Git 仓库 URL
- `ref`：要跟踪的上游分支、标签或 commit
- `source_path`：skill 在上游仓库中的目录，可省略；省略时同步
  整个上游仓库

提交配置文件后，运行以下命令即可首次导入：

```bash
just sync example-skill
```

若 `target_path` 不存在，脚本使用 `git subtree add` 导入。已存在时，
整仓来源使用 `git subtree pull` 更新，子目录来源则先
`git subtree split`，再使用 `git subtree merge` 更新。

例如，上游仓库结构为：

```text
skills/
└── example-skill/
    └── SKILL.md
```

配置 `"source_path": "skills/example-skill"` 后，本仓库的
`example-skill/` 只会包含该子目录的内容，不会引入上游仓库中的
其他文件。

同步前工作区必须保持干净。脚本会从配置的 `ref` 拉取最新
内容，使用 `--squash` 创建同步提交，不会导入完整的上游提交
历史。
