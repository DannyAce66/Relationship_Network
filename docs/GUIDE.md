# Relationship Network — User Guide / 使用指南

> English · 中文

---

## Table of Contents / 目录

1. [Installation / 安装](#installation--安装)
2. [Core Concepts / 基本概念](#core-concepts--基本概念)
3. [Common Scenarios / 常用场景](#common-scenarios--常用场景)
4. [All Commands / 全部命令](#all-commands--全部命令)
5. [Tag System / 标签系统](#tag-system--标签系统)
6. [Relationship Network / 关系网络](#relationship-network--关系网络)
7. [Tips & Tricks / 小技巧](#tips--tricks--小技巧)
8. [FAQ / 常见问题](#faq--常见问题)

---

## Installation / 安装

```bash
# Clone the repo / 克隆项目
git clone https://github.com/your-username/Relationship_Network.git
cd Relationship_Network

# Install (zero dependencies — pure Python stdlib)
# 安装（零依赖 — 纯 Python 标准库）
pip install -e .
```

**Verify / 验证：**
```bash
rn --help
```

**Requirements / 环境要求：** Python 3.8+

That's it. No database, no Docker, no API keys. Just Python.
就这些。不需要数据库、不需要 Docker、不需要 API Key。只要 Python。

---

## Core Concepts / 基本概念

RN stores each contact as a record with these fields:
RN 把每个人脉存为一个联系人记录，包含以下字段：

| Field / 字段 | Required / 必填 | Description / 说明 | Example / 示例 |
|------|------|------|------|
| Name / 姓名 | ✅ | Full name / 全名 | John Smith / 张三 |
| Nickname / 昵称 | — | How you call them / 你怎么称呼他 | Johnny / 三哥 |
| Tags / 标签 | — | Comma-separated, core feature / 逗号分隔（核心功能） | investor, NYC, fintech |
| Bio / 简介 | — | One-line description / 一句话描述 | Early-stage VC at a16z |
| Met How / 认识方式 | — | How you met / 怎么认识的 | Met at TechCrunch 2024 |
| Relationship / 与我的关系 | — | Your relationship to them / 你和他的关系 | Advisor / 投资顾问 |
| Notes / 备注 | — | Anything else / 补充信息 | Prefers email, slow on WhatsApp |

---

## Common Scenarios / 常用场景

### Scenario 1: Just met someone — save them / 刚认识一个人 — 记下来

```bash
# English
rn add "John Smith,investor,NYC,met at TechCrunch"

# 中文
rn add "张三,投资人,深圳,创业大会认识"
```

### Scenario 2: Need to find someone — search / 想找人 — 搜一下

```bash
rn search investor     # Find all investors / 找所有投资人
rn search NYC          # Find everyone in NYC / 找纽约的
rn search fintech      # Find fintech people / 找金融科技的
rn search John         # Search by name / 按名字搜
```

### Scenario 3: Need a specific type of person — recommend
### 需要特定类型的人 — 智能推荐

```bash
rn recommend "NYC investor"        # Find NYC-based investors / 找纽约投资人
rn recommend "lawyer startup"      # Find startup lawyers / 找创业律师
rn recommend "深圳 投资"            # Find Shenzhen investors / 找深圳投资人
```

### Scenario 4: Want to meet someone — find the path
### 想认识某人 — 找谁能搭线

```bash
rn path "John Smith" "Jane Doe"
# Output / 输出:
#   Found path (2 hops) / 找到路径 (2 步):
#     John Smith
#      —— client ——> Bob Lee
#      —— coworker ——> Jane Doe

rn path 张三 李四
# 输出:
#   找到路径 (2 步):
#     张三
#      —— 客户 ——> 王五
#      —— 同事 ——> 李四
```

### Scenario 5: See your network at a glance / 查看人脉全貌

```bash
rn tagcloud          # Tag distribution / 标签分布
rn list              # Everyone you know / 列出所有人
```

---

## All Commands / 全部命令

### `rn add` — Add a contact / 添加联系人

```bash
# Short format (recommended) / 简写格式（推荐）
rn add "John Smith,investor,NYC,met at conference"
rn add "张三,投资人,深圳,创业大会认识"

# Full format / 完整格式
rn add --name "Jane Doe" --tags designer,SF --met-how "friend intro" --relationship "former colleague"

# With relationship in short format / 带关系的简写
rn add "Bob Lee,engineer,rel:partner,Seattle"
rn add "王五,创业者,关系:合作伙伴,北京"
```

### `rn search` — Search contacts / 搜索联系人

Searches name, nickname, tags, and bio. / 搜索范围：姓名、昵称、标签、简介。

```bash
rn search investor
rn search NYC
rn search 投资
```

### `rn list` — List all contacts / 列出所有联系人

```bash
rn list
```

### `rn remove` — Remove a contact / 删除联系人

```bash
rn remove "John Smith"
rn remove 张三
# Asks for confirmation / 会要求确认
```

### `rn path` — Find connection path / 查找连接路径

Finds the shortest chain of people connecting two contacts (BFS, max 3 hops).
用 BFS 算法找出两人之间最短人脉链条（最多3步）。

```bash
rn path "John Smith" "Jane Doe"
rn path 张三 李四
```

### `rn recommend` — Recommend by scenario / 按场景推荐

```bash
rn recommend "NYC investor"
rn recommend "startup lawyer SF"
rn recommend 深圳投资人
```

### `rn relation` — Manage relationships / 管理关系

```bash
# View someone's relations / 查看某人关系
rn relation "John Smith"
rn relation 张三

# Add a relation / 添加关系
rn relation add "John" "Jane" partner "co-founded a startup together"
rn relation add 张三 李四 合作伙伴 "一起做过项目"
```

### `rn tagcloud` — Tag cloud / 标签云

```bash
rn tagcloud
# Output / 输出:
#   investor              ████████████████████ 3
#   NYC:#location         ████████████████████ 3
#   SF:#location          █████████████ 2
#   ...
```

---

## Tag System / 标签系统

Tags are the most powerful feature of RN. Use them well, and finding people becomes instant.
标签是 RN 最核心的功能。用好了标签，找人就是一秒钟的事。

### Tag Format / 标签格式

```
tag_name:#category
标签名:#类别
```

Examples / 示例：
```
investor              ← plain tag / 普通标签
NYC:#location         ← location tag / 地点标签
fintech:#industry     ← industry tag / 行业标签
Python:#skill         ← skill tag / 技能标签
angel:#investor_type  ← sub-type tag / 子类型标签
```

### Recommended Tags Per Person / 每人建议加 2-5 个标签

1. **Role / 职业标签**: investor, lawyer, designer, founder / 投资人、律师、设计师、创业者
2. **Location / 地点标签**: NYC:#location, SF:#location, London:#location / 深圳:#location、北京:#location
3. **Industry / 行业标签**: fintech, SaaS, biotech / 金融科技、企业服务、生物医药
4. **Skill / 技能标签**: Python:#skill, public-speaking:#skill
5. **Resource / 资源标签**: has-funds, well-connected, legal-expert / 有资金、有人脉、懂法务

---

## Relationship Network / 关系网络

### Direction / 方向

Relationships in RN are **directed** — "I know John" and "John knows me" are two separate edges.
RN 中的关系是**有方向的**——"我认识张三"和"张三认识我"是两条不同的关系。

### Path Finding / 路径查找

Uses BFS (Breadth-First Search), expanding outward layer by layer, max 3 hops.
使用 BFS（广度优先搜索），逐层扩展，最多搜索 3 层。

If no path is found within 3 hops, these two people have no direct connection in your network.
如果 3 层内找不到连接，说明这两个人在你的人脉网里没有直接交集。

### Relationship Types / 关系类型建议

- Colleague / Former colleague — 同事/前同事
- Partner / Co-founder — 合伙人/联合创始人
- Friend — 朋友
- Mentor / Mentee — 导师/学员
- Client / Vendor — 客户/供应商
- Investor / Founder — 投资人/创业者
- Met through [Name] — 通过[某人]认识
- Industry peer — 同行

---

## Tips & Tricks / 小技巧

### 1. Batch import old contacts / 批量导入旧数据

If you have contacts in Excel, CSV, or another format, use a Python script:
如果你有 Excel/通讯录的旧数据，用 Python 脚本批量导入：

```python
from rn import RelationshipNetwork

net = RelationshipNetwork()

# Import from your old data source / 从你的旧数据源导入
contacts = [
    {"name": "John Smith", "tags": ["investor", "NYC"], "met_how": "conference 2023"},
    {"name": "张三", "tags": ["投资人", "深圳"], "met_how": "2023年认识"},
]
for c in contacts:
    net.add_person(**c)
```

### 2. Backup / 数据备份

Your data is just one file. Copy it to back up.
数据文件就一个，复制它就是备份。

```bash
cp ~/.rn/persons.jsonl ~/backup/network_$(date +%Y%m%d).jsonl
```

### 3. Version control with git / 用 git 管理数据

```bash
cd ~/.rn
git init
git add persons.jsonl
git commit -m "Network backup $(date +%Y-%m-%d)"
```

### 4. Multiple data files / 多数据文件

```bash
# Separate personal and work networks / 分开个人和工作人脉
rn --data ~/.rn/personal.jsonl list
rn --data ~/.rn/work.jsonl search investor
```

---

## FAQ / 常见问题

**Q: Where is my data stored? / 数据存在哪？**
A: Default: `~/.rn/persons.jsonl`. Plain text, open with any editor.
默认: `~/.rn/persons.jsonl`。纯文本，随时可打开编辑。

**Q: Is my data private? / 数据安全吗？**
A: 100% local. No cloud, no servers, no telemetry. The file lives on your machine.
完全本地。没有云、没有服务器、不上传任何数据。文件就在你电脑上。

**Q: Can I share a network with my team? / 能团队共用吗？**
A: Put the JSONL file on a shared drive, or use git. Each person uses `--data` to point to it.
把 JSONL 放共享盘或用 git 同步，每人用 `--data` 指向同一个文件。

**Q: Can I import from LinkedIn/WeChat? / 能导入LinkedIn/微信吗？**
A: Export from those platforms, then use a Python script to convert to JSONL format.
先从那些平台导出，然后用 Python 脚本转成 JSONL 格式。

**Q: What if I want to edit data directly? / 想直接编辑数据？**
A: Just open `~/.rn/persons.jsonl` in any text editor. It's human-readable JSON.
直接用记事本打开 `~/.rn/persons.jsonl` 编辑就行。

**Q: Does search work in multiple languages? / 搜索支持多语言吗？**
A: Yes. Search is substring-based — it works in any language. Tags are free-form text.
支持。搜索基于子串匹配，任何语言都可以。标签也是自由文本。
