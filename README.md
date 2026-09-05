# Agent Skills

个人维护的编程智能体技能（Agent Skills）集合，涵盖中文文档、术语、文本润色、Git 工作流、会话命名和 macOS 输入法开发。每个技能都是独立目录，包含 `SKILL.md` 以及可选的脚本、参考资料和评估用例，可以按需安装。

这些技能可通过 [`skills`](https://github.com/vercel-labs/skills) CLI 安装到 Codex、Claude Code 等支持 Agent Skills 的编程智能体。具体任务需要的工具和依赖见各技能的 `SKILL.md`。

## Skills

| 技能 | 适用场景 |
| --- | --- |
| [`chinese-doc-style`](chinese-doc-style/SKILL.md) | 创建、修改正式中文文档或专项审阅混排、标点、专名和格式；新建与改写兼顾基本表达，只读格式审阅只给建议 |
| [`chinese-stem-terminology`](chinese-stem-terminology/SKILL.md) | 写作、翻译或审校数学、物理、计算机、化学等内容时，规范中国大陆常用中文术语 |
| [`conversation-namer`](conversation-namer/SKILL.md) | 按 `MMDD｜类型｜主题` 规范会话标题，默认使用中文，以原始创建时间换算上海时区日期；默认预览确认，复用已有明确授权 |
| [`git-crypt`](git-crypt/SKILL.md) | 使用 git-crypt 配置文件加密、管理访问权限和排障；按需处理已有明文并区分暂存与提交验证 |
| [`git-commit-writer`](git-commit-writer/SKILL.md) | 撰写、检查或修改提交信息，采用英文 ASCII Conventional Commits 格式并要求有用的正文 |
| [`humanizer`](humanizer/SKILL.md) | 修订 AI 味较重的文本，保留事实和作者语气；使用上游原版 |
| [`humanizer-zh`](Humanizer-zh/SKILL.md) | 润色中文文本或专项审阅套话、夸张表述和机械句式，保留事实与作者语气；一般阅读、事实与逻辑审查不触发 |
| [`macos-input-method`](macos-input-method/SKILL.md) | 使用 InputMethodKit 创建、修改、安装和调试 macOS 输入法，按任务读取项目、安装和排障指南 |

表中的名称用于安装。`humanizer-zh` 的源码目录是 `Humanizer-zh/`，两者大小写不同。`git-commit-writer` 使用英文说明，提交信息要求英文 ASCII；仅约束提交信息本身，不额外规定检查改动、暂存或执行提交的流程。附带脚本只在明确要求校验提交信息时运行。中文技术文档同时涉及术语和排版时，先规范术语，再统一格式。

`humanizer-zh` 与 `chinese-doc-style` 可独立使用。前者处理表达问题，后者处理正式文档的书写规范；两者的专项审阅均可只报告问题，是否改稿由用户请求决定。仅阅读、总结或比较内容不会因此加载它们。正式文档需要专门润色时，先处理表达，再检查术语和格式；仅排版时保留原有表达。

## 使用 npx skills 安装

需要可运行 `npx` 的 Node.js/npm 环境，以及下载仓库所需的网络访问。以下命令的参数以 [`skills` CLI 文档](https://github.com/vercel-labs/skills) 为准。

先查看仓库中可安装的技能，这一步不会安装：

```bash
npx skills add erning/agent-skills --list
```

在需要使用技能的项目目录中，交互式安装指定技能：

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

安装全部技能到这两个智能体：

```bash
npx skills add erning/agent-skills \
  --skill '*' \
  --global \
  --agent codex \
  --agent claude-code \
  --yes
```

不使用 `--global` 时，默认安装到当前项目；全局安装供当前用户的多个项目使用。`--agent` 指定目标智能体，`--yes` 跳过安装确认。按需替换或移除示例中的目标智能体。

## 安装后如何使用

在任务中点名技能，并给出要处理的文件或范围。例如：

```text
请使用 chinese-doc-style，直接修改 README.md 的中文安装说明，统一格式并保留命令。

请使用 chinese-stem-terminology，审校 notes.md 的物理术语，使用中国大陆常用译名。

请使用 git-commit-writer，为当前改动起草提交信息。

请使用 conversation-namer，规范当前项目的会话标题，先展示预览。
```

Codex CLI 和 IDE 扩展支持用 `$技能名` 显式调用；任务符合技能描述时也可以自动选用。用法见 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills)。其他智能体的调用入口以其自身文档为准。

如果技能未出现，先检查安装范围和目标智能体，再查看安装目录中的 `SKILL.md` 是否存在、符号链接是否有效；必要时重启智能体。

## 从本地仓库安装

需要 Git。克隆本仓库后，可以直接从本地路径安装：

```bash
git clone https://github.com/erning/agent-skills.git
cd agent-skills

npx skills add . --list
npx skills add . --skill git-commit-writer --global
```

也可以直接指定单个技能目录：

```bash
npx skills add ./git-commit-writer --global
```

## 管理已安装的技能

```bash
# 查看项目级和全局技能
npx skills list

# 仅查看全局技能
npx skills list --global

# 更新当前项目的技能
npx skills update --project

# 更新全局技能
npx skills update --global

# 删除全局技能
npx skills remove --global git-commit-writer
```

上述命令管理安装副本。维护本地源码时，用 Git 更新本仓库；手动创建的符号链接会直接反映所指向源码的变化。

## 手动安装

不使用 `npx skills` 时，也可以将完整技能目录复制或链接到智能体的发现目录。以下是手动安装位置：

```text
Codex project:       .agents/skills/
Codex global:        ~/.agents/skills/
Claude Code project: .claude/skills/
Claude Code global:  ~/.claude/skills/
```

Codex 路径依据 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills)，Claude Code 路径可参见 [`skills` 的智能体目录表](https://github.com/vercel-labs/skills#supported-agents)。CLI 管理的安装路径可能与手动安装位置不同，以安装输出为准。

例如，将本地技能链接到 Claude Code 的用户目录：

```bash
mkdir -p ~/.claude/skills
ln -s /absolute/path/to/git-commit-writer \
  ~/.claude/skills/git-commit-writer
```

将示例中的绝对路径替换为实际源码路径。保留完整目录，以便技能读取随附的脚本和参考资料。

## 仓库结构与维护

```text
agent-skills/
├── <skill-name>/       # 技能源文件：SKILL.md、参考资料、脚本、评估用例等
├── .agents/skills/     # 本仓库维护时使用的部分技能的符号链接
├── .claude/skills/     # 同上，供 Claude Code 发现
├── AGENTS.md           # 面向 coding agents 的维护说明
├── CLAUDE.md           # 指向 AGENTS.md 的符号链接
├── upstreams.json      # 第三方技能的上游配置
├── scripts/            # 上游配置读取和同步脚本
├── tests/              # 仓库维护脚本的测试
└── justfile            # 列出、同步上游技能的命令入口
```

修改技能时编辑顶层源码目录。新增技能至少需要带 `name` 和 `description` 的 `SKILL.md`，并在本 README 的目录表中添加入口。脚本、参考资料、显示元数据和评估用例按需添加，具体约定及验证命令见 [AGENTS.md](AGENTS.md)。

本仓库没有统一构建步骤。`evals/` 中的 JSON 保存评估提示词和预期行为，不属于 Python 单元测试，也没有统一的自动执行入口。

## 同步上游技能

[`upstreams.json`](upstreams.json) 记录通过 squash Git subtree 保存在本仓库中的第三方技能。此操作用于维护仓库中的源码，会创建 Git 提交；更新已安装的技能请使用前面的 `npx skills update`。

| 同步名称 | 目录 | 上游 |
| --- | --- | --- |
| `humanizer` | `humanizer/` | [`blader/humanizer`][humanizer] |
| `humanizer-zh` | `Humanizer-zh/` | [`op7418/Humanizer-zh`][humanizer-zh] |

[humanizer]: https://github.com/blader/humanizer
[humanizer-zh]: https://github.com/op7418/Humanizer-zh

subtree 将文件保存在本仓库中，因此普通克隆和 `npx skills` 安装都不需要初始化 Git submodule。同步时保留各上游的许可证及元数据。

运行同步需要 Bash、Python 3、带 `git subtree` 的 Git，以及上游仓库的网络访问权限。下面的快捷命令还需要 [`just`](https://github.com/casey/just)。请从仓库根目录运行，并确保工作区干净，包括没有未跟踪文件。

同步所有上游技能：

```bash
just sync
```

也可以只同步一个：

```bash
just sync humanizer
just sync humanizer-zh
```

查看配置中所有第三方技能，不会拉取或修改文件：

```bash
just list
```

运行不带参数的 `just` 可以查看所有可用命令。没有安装 `just` 时，可以直接执行脚本：

```bash
./scripts/sync-upstream-skills.sh --list
./scripts/sync-upstream-skills.sh humanizer
./scripts/sync-upstream-skills.sh all
```

增加第三方技能时，在 `upstreams.json` 中以技能名为键添加一项：

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

- 顶层键：同步命令使用的名称，也是 Conventional Commit 的 scope。
- `target_path`：同步到本仓库后的相对目录，可省略，默认与顶层键相同。
- `repository`：上游 Git 仓库 URL，必填。
- `ref`：要跟踪的上游分支、标签或提交引用，必填，且需要能从上游拉取。
- `source_path`：技能在上游仓库中的相对目录，可省略；省略或设为 `.` 时同步整个仓库。

可以先检查配置，命令成功时会输出解析后的记录：

```bash
python3 scripts/read-upstreams.py upstreams.json
```

提交配置文件后，运行以下命令即可首次导入：

```bash
just sync example-skill
```

若 `target_path` 不存在，脚本使用 `git subtree add` 导入。已存在时，整仓来源使用 `git subtree pull` 更新，子目录来源则先 `git subtree split`，再使用 `git subtree merge` 更新。

上例的 `"source_path": "skills/example-skill"` 表示只导入上游该子目录的内容，不会引入上游仓库中的其他文件。

脚本从配置的 `ref` 拉取内容，使用 `--squash` 创建同步提交，不会导入完整的上游提交历史。完成后检查差异，并按所更新技能的维护说明运行相关验证。

`humanizer/` 保留已同步的上游原版，沿用上游格式和校验规则，仅在存在具体使用问题时考虑本地修复。

`Humanizer-zh/` 以用户确认的中文适配和行为修订为准，具体差异记录在其 README 中。同步上游时逐项合并适用改动；发生冲突时优先保留本地约定，并保留上游来源和许可证。
