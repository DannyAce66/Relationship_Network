# Relationship Network (RN)

> A lightweight personal relationship manager. CLI + Python library. Zero dependencies, pure Python stdlib.
>
> 轻量级个人人脉管理工具。命令行 + Python 库双模式，零依赖，纯 Python 标准库。

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](requirements.txt)

---

## Why RN? / 为什么需要 RN？

Your network is scattered across LinkedIn, phone contacts, WhatsApp, WeChat, spreadsheets, and your brain. When you need "an investor in NYC who knows fintech," you spend 15 minutes searching.

Your network is your net worth — but only if you can find the right person when it matters.

RN gives you a **tag-based system** to organize your contacts, **natural language search** to find them instantly, and **path finding** to discover who can introduce you to whom.

你的人脉散落在 LinkedIn、通讯录、微信、Excel、大脑里。想找"深圳做投资的朋友"时，得翻半天。

人脉就是钱脉——但前提是关键时刻你能找到对的人。

---

## Quick Start / 快速开始

```bash
# 1. Clone / 克隆
git clone https://github.com/your-username/Relationship_Network.git
cd Relationship_Network

# 2. Install (zero deps) / 安装（零依赖）
pip install -e .

# 3. Start using / 开始使用
rn add "John Smith,investor,NYC,met at conference"
rn search investor
rn list
rn path "John Smith" "Jane Doe"
rn recommend "NYC investor"
rn tagcloud
```

---

## Commands / 命令一览

| Command / 命令 | Description / 说明 | Example / 示例 |
|------|------|------|
| `rn add` | Add a contact / 添加联系人 | `rn add "John Smith,investor,NYC,met at conference"` |
| `rn search` | Search contacts / 搜索联系人 | `rn search investor` |
| `rn list` | List all contacts / 列出所有人 | `rn list` |
| `rn remove` | Remove a contact / 删除联系人 | `rn remove "John Smith"` |
| `rn path` | Find connection path between two people / 找两人连接路径 | `rn path "John" "Jane"` |
| `rn recommend` | Recommend contacts by scenario / 按场景推荐 | `rn recommend "NYC investor"` |
| `rn relation` | Manage relationship network / 管理关系网络 | `rn relation add "John" "Jane" partner` |
| `rn tagcloud` | Show tag cloud / 显示标签云 | `rn tagcloud` |

---

## Sample Data / 示例数据

The repo includes 10 fictional contacts for instant testing / 项目自带 10 条虚构示例数据：

```bash
# English examples / 英文示例
rn --data data/sample.jsonl list
rn --data data/sample.jsonl search investor
rn --data data/sample.jsonl tagcloud

# Chinese examples also work / 中文同样支持
rn --data data/sample.jsonl search 投资
rn --data data/sample.jsonl recommend 深圳
```

---

## Python API

```python
from rn import RelationshipNetwork

net = RelationshipNetwork()

# Add contacts in any language / 支持任何语言
net.add_person("John Smith", tags=["investor", "NYC:#location"], met_how="met at TechCrunch")
net.add_person("张三", tags=["投资人", "深圳:#location"], met_how="创业大会认识")

# Search works across languages / 跨语言搜索
results = net.search("investor")
results = net.search("投资")

# Find who connects you to someone / 找到谁可以帮你搭线
path = net.find_path("John Smith", "Jane Doe")
```

---

## Data Storage / 数据存储

- **Default path / 默认路径**: `~/.rn/persons.jsonl`
- **Format / 格式**: JSONL (one contact per line, human-readable / 一行一个联系人)
- **Plain text / 纯文本**: Open with any text editor / 可直接用记事本打开
- Your data lives on **your machine only** — no cloud, no servers / 数据完全在本地，不上传任何服务器

---


## Storage Backends / 存储模式

RN supports two storage backends. Both are zero-dependency (SQLite is built into Python).
RN 支持两种存储模式，都零依赖（SQLite 是 Python 内置的）。

| Feature / 特性 | JSONL (default) | SQLite (`--db`) |
|------|:--:|:--:|
| Human-readable file / 人类可读 | ✅ | — |
| Git-friendly / 可版本控制 | ✅ | — |
| Fast queries / 查询快 | — | ✅ |
| Rich relations / 关系查询 | — | ✅ |
| Stats dashboard / 统计面板 | — | ✅ |
| Best for / 适合 | < 500 contacts | > 500 contacts |

```bash
# JSONL mode (default) / JSONL 模式（默认）
rn add "John Smith,investor,NYC"

# SQLite mode / SQLite 模式
rn --db add "John Smith,investor,NYC"
rn --db stats
```

---

## Project Structure / 项目结构

```
rn/                     ← Python package / Python 包
  __init__.py           ← API exports / API 导出
  network.py            ← Core engine (JSONL) / 核心模块
  database.py           ← SQLite backend / SQLite 引擎
  cli.py                ← CLI tool / 命令行工具
data/
  sample.jsonl          ← Sample data / 示例数据（fictional / 虚构）
skills/
  AGENTS.md             ← AI Agent integration guide / AI Agent 集成指南
scripts/
  install.sh            ← One-click install / 一键安装脚本
docs/
  GUIDE.md              ← Full tutorial (bilingual) / 完整教程（中英双语）
```

### AI Agent Integration / AI Agent 集成

RN can auto-detect names in your chat conversations and prompt you to add them.
Load `skills/AGENTS.md` into your AI agent (Hermes, OpenClaw, Claw Code):

RN 可以在聊天对话中自动识别人名并提示你录入。将 `skills/AGENTS.md` 加载到你的 AI Agent 中：

```bash
# Hermes
cp skills/AGENTS.md ~/.hermes/skills/relationship-network/SKILL.md

# OpenClaw
cp skills/AGENTS.md /path/to/openclaw/skills/relationship-network/SKILL.md

# One-click setup (all platforms) / 一键配置
./scripts/install.sh
```

After setup, your agent will automatically:
配置后，Agent 会自动：

- 🔍 Search RN whenever a name is mentioned / 对话中提到人名时自动查 RN
- ❓ Ask to add new contacts / 新人出现时询问是否录入
- 🔄 Ask to update when new info appears / 发现新信息时询问是否更新

---

## Who is this for? / 谁适合用？

- **Founders & VCs** — track your investor/startup network
- **Sales & BD** — never lose a lead again
- **Recruiters** — tag candidates by skill, location, seniority
- **Anyone who networks** — if you meet people, you need this

- **创业者/投资人** — 管理你的投资人/创业项目人脉
- **销售/BD** — 再也不丢客户线索
- **猎头/HR** — 按技能、地点、级别标记候选人
- **所有需要社交的人** — 只要你认识人，你就需要这个

---

## License / 许可

MIT — see [LICENSE](LICENSE)
