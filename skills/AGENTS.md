# AGENTS.md — Relationship Network Agent Behavior

> Load this file into your AI agent's system prompt or skills directory.
> The agent will then automatically manage your relationship network during conversations.
>
> 将此文件加载到 AI Agent 的系统提示或 skills 目录中。
> Agent 会在对话中自动管理你的人脉网络。

---

## Trigger Rules / 触发规则 (HARD CONSTRAINT / 硬约束)

Whenever a **person's name** appears in conversation, the agent MUST:

1. **Search RN first** — check if this person exists in the network
2. **Report findings** — if found, briefly mention who they are
3. **Ask to add** — if NOT found, ask: "Want me to add [Name] to your Relationship Network?"
4. **Ask to update** — if found but new info is mentioned, ask: "[Name] is in your network. Want me to update their info?"

对话中提到任何人名时，Agent 必须：
1. 先查 RN — 检查此人是否已存在
2. 报告结果 — 如已存在，简述此人是谁
3. 询问添加 — 如不存在，问："要把 [姓名] 加入你的人脉网络吗？"
4. 询问更新 — 如已存在但有新信息，问："[姓名] 已在人脉中，要更新信息吗？"

---

## How to Use RN Commands / 如何使用 RN 命令

The agent uses the `rn` CLI to interact with the network:

```bash
# Search for a person
rn search "John Smith"

# Add a new person
rn add "John Smith,investor,NYC,met at conference"

# Add with full details
rn add --name "John Smith" --tags "investor,NYC" --met-how "TechCrunch 2024" --relationship "advisor"

# Find connection path
rn path "John Smith" "Jane Doe"

# Recommend people for a scenario
rn recommend "NYC investor fintech"

# View someone's relations
rn relation "John Smith"

# Add a relation
rn relation add "John Smith" "Jane Doe" "coworker"

# List all contacts
rn list

# Show tag cloud
rn tagcloud
```

---

## Data Format / 数据格式

When adding a person, the agent should collect these fields:
添加联系人时，Agent 应收集以下字段：

| Field | Required | Example |
|-------|----------|---------|
| Name | ✅ | John Smith |
| Tags | Recommended | investor, NYC:#location, fintech |
| Bio | Optional | Early-stage VC at a16z |
| How we met | Optional | TechCrunch 2024 |
| Relationship | Optional | Advisor |
| Notes | Optional | Prefers email over WhatsApp |

Data is stored at `~/.rn/persons.jsonl` (plain text, human-readable).

---

## Name Recognition / 人名识别

The agent should recognize names in conversation using these patterns:
Agent 应通过以下模式识别对话中的人名：

- "I met [Name] yesterday" → 我昨天见了[姓名]
- "[Name] is a [role] at [company]" → [姓名]是[公司]的[职位]
- "Talked to [Name] about [topic]" → 和[姓名]聊了[话题]
- "Do you know [Name]?" → 你认识[姓名]吗
- "[Name] introduced me to [Name2]" → [姓名]介绍我认识了[姓名2]

---

## Privacy / 隐私

- RN data is **100% local** — stored on the user's machine only
- The agent should NEVER share RN data with external services
- Users can see their data anytime: `cat ~/.rn/persons.jsonl`
