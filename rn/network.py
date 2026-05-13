"""Relationship Network - 核心模块

一个轻量级的个人人脉管理工具，支持标签系统、关系搜索、人脉推荐。
纯 Python 标准库实现，零外部依赖。
"""

import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


_DEFAULT_DATA_DIR = Path.home() / ".rn"
_DEFAULT_DATA_FILE = _DEFAULT_DATA_DIR / "persons.jsonl"


def _get_data_path(data_path: Optional[str] = None) -> Path:
    """获取数据文件路径，如果未指定则使用默认路径。"""
    if data_path:
        return Path(data_path)
    return _DEFAULT_DATA_FILE


def _ensure_data_dir(path: Path) -> None:
    """确保数据文件所在目录存在。"""
    path.parent.mkdir(parents=True, exist_ok=True)


def _normalize_name(name: str) -> str:
    """标准化姓名：去除首尾空格。"""
    return name.strip()


def _parse_tags(tag_str: str) -> List[str]:
    """将逗号分隔的标签字符串解析为标签列表。"""
    if not tag_str or not tag_str.strip():
        return []
    tags = [t.strip() for t in tag_str.split(",") if t.strip()]
    return tags


def _match_keyword(text: str, keyword: str) -> bool:
    """检查文本是否匹配关键词（模糊匹配）。"""
    if not keyword:
        return True
    return keyword.lower() in text.lower()


class Person:
    """表示一个联系人。"""

    def __init__(
        self,
        name: str,
        nickname: str = "",
        tags: Optional[List[str]] = None,
        bio: str = "",
        met_how: str = "",
        relationship: str = "",
        notes: str = "",
    ):
        self.name = _normalize_name(name)
        self.nickname = nickname.strip()
        self.tags = tags or []
        self.bio = bio.strip()
        self.met_how = met_how.strip()
        self.relationship = relationship.strip()
        self.notes = notes.strip()

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "nickname": self.nickname,
            "tags": self.tags,
            "bio": self.bio,
            "met_how": self.met_how,
            "relationship": self.relationship,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Person":
        return cls(
            name=d.get("name", ""),
            nickname=d.get("nickname", ""),
            tags=d.get("tags", []),
            bio=d.get("bio", ""),
            met_how=d.get("met_how", ""),
            relationship=d.get("relationship", ""),
            notes=d.get("notes", ""),
        )

    def __repr__(self) -> str:
        return f"<Person: {self.name}>"

    def __str__(self) -> str:
        parts = [f"姓名: {self.name}"]
        if self.nickname:
            parts.append(f"昵称: {self.nickname}")
        if self.tags:
            parts.append(f"标签: {', '.join(self.tags)}")
        if self.bio:
            parts.append(f"简介: {self.bio}")
        if self.met_how:
            parts.append(f"认识方式: {self.met_how}")
        if self.relationship:
            parts.append(f"与我的关系: {self.relationship}")
        if self.notes:
            parts.append(f"备注: {self.notes}")
        return "\n".join(parts)


class Relationship:
    """记录两个人之间的关系。"""

    def __init__(self, person_a: str, person_b: str, description: str = ""):
        self.person_a = _normalize_name(person_a)
        self.person_b = _normalize_name(person_b)
        self.description = description.strip()

    def to_dict(self) -> Dict:
        return {
            "person_a": self.person_a,
            "person_b": self.person_b,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Relationship":
        return cls(
            person_a=d.get("person_a", ""),
            person_b=d.get("person_b", ""),
            description=d.get("description", ""),
        )

    def __repr__(self) -> str:
        return f"<Relationship: {self.person_a} <-> {self.person_b}>"


class RelationshipNetwork:
    """人脉网络管理器，提供人脉 CRUD、标签管理、关系路径搜索和推荐功能。"""

    def __init__(self, data_path: Optional[str] = None):
        self.data_path = _get_data_path(data_path)
        self.rels_data_path = self.data_path.parent / (
            self.data_path.stem + "_relations.jsonl"
        )
        self._persons: Dict[str, Person] = {}
        self._relations: List[Relationship] = []
        self._load()

    # ── 数据持久化 ──────────────────────────────────

    def _load(self) -> None:
        """从 JSONL 文件加载联系人数据。"""
        self._persons = {}
        self._relations = []

        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            d = json.loads(line)
                            p = Person.from_dict(d)
                            self._persons[p.name] = p
                        except json.JSONDecodeError:
                            continue

        if self.rels_data_path.exists():
            with open(self.rels_data_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            d = json.loads(line)
                            self._relations.append(Relationship.from_dict(d))
                        except json.JSONDecodeError:
                            continue

    def save(self) -> None:
        """将联系人数据保存到 JSONL 文件。"""
        _ensure_data_dir(self.data_path)
        with open(self.data_path, "w", encoding="utf-8") as f:
            for person in self._persons.values():
                f.write(json.dumps(person.to_dict(), ensure_ascii=False) + "\n")

        with open(self.rels_data_path, "w", encoding="utf-8") as f:
            for rel in self._relations:
                f.write(json.dumps(rel.to_dict(), ensure_ascii=False) + "\n")

    # ── 人脉 CRUD ──────────────────────────────────

    def add_person(self, person: Person) -> bool:
        """添加一个联系人。如果已存在则返回 False。"""
        name = person.name
        if not name:
            raise ValueError("姓名不能为空")
        if name in self._persons:
            return False
        self._persons[name] = person
        self.save()
        return True

    def add_or_update_person(self, person: Person) -> bool:
        """添加或更新联系人。新增返回 True，更新返回 False。"""
        name = person.name
        if not name:
            raise ValueError("姓名不能为空")
        is_new = name not in self._persons
        if is_new:
            self._persons[name] = person
        else:
            existing = self._persons[name]
            existing.nickname = person.nickname or existing.nickname
            existing.bio = person.bio or existing.bio
            existing.met_how = person.met_how or existing.met_how
            existing.relationship = person.relationship or existing.relationship
            # 合并标签（去重）
            existing_tags = set(existing.tags)
            existing_tags.update(person.tags)
            existing.tags = sorted(existing_tags)
            # 追加备注
            if person.notes:
                if existing.notes:
                    existing.notes += "\n" + person.notes
                else:
                    existing.notes = person.notes
        self.save()
        return is_new

    def get_person(self, name: str) -> Optional[Person]:
        """根据姓名获取联系人。"""
        return self._persons.get(_normalize_name(name))

    def search(self, keyword: str = "") -> List[Person]:
        """搜索联系人，支持模糊匹配姓名、昵称、标签、简介、备注等。"""
        if not keyword:
            return list(self._persons.values())

        results = []
        kw = keyword.strip()
        for person in self._persons.values():
            if _match_keyword(person.name, kw):
                results.append(person)
                continue
            if _match_keyword(person.nickname, kw):
                results.append(person)
                continue
            if _match_keyword(person.bio, kw):
                results.append(person)
                continue
            if _match_keyword(person.relationship, kw):
                results.append(person)
                continue
            if _match_keyword(person.notes, kw):
                results.append(person)
                continue
            for tag in person.tags:
                if _match_keyword(tag, kw):
                    results.append(person)
                    break
        return results

    def remove_person(self, name: str) -> bool:
        """删除联系人。成功返回 True，不存在返回 False。"""
        name = _normalize_name(name)
        if name in self._persons:
            del self._persons[name]
            # 同时删除与该人相关的关系
            self._relations = [
                r
                for r in self._relations
                if r.person_a != name and r.person_b != name
            ]
            self.save()
            return True
        return False

    def list_all(self) -> List[Person]:
        """列出所有人脉。"""
        return list(self._persons.values())

    # ── 标签系统 ──────────────────────────────────

    def tag_cloud(self) -> Dict[str, int]:
        """统计所有标签的使用频率，返回标签云。"""
        counter: Counter = Counter()
        for person in self._persons.values():
            for tag in person.tags:
                counter[tag] += 1
        return dict(counter.most_common())

    def search_by_tags(self, tag_keywords: List[str]) -> List[Person]:
        """按标签关键词搜索联系人（多个关键词取交集）。"""
        if not tag_keywords:
            return self.list_all()

        results = []
        for person in self._persons.values():
            person_tag_text = " ".join(person.tags).lower()
            if all(kw.lower() in person_tag_text for kw in tag_keywords):
                results.append(person)
        return results

    # ── 关系网络 ──────────────────────────────────

    def add_relation(self, relation: Relationship) -> bool:
        """添加两个人之间的关系。"""
        # 验证双方都存在
        if relation.person_a not in self._persons:
            raise ValueError(f"联系人 '{relation.person_a}' 不存在")
        if relation.person_b not in self._persons:
            raise ValueError(f"联系人 '{relation.person_b}' 不存在")
        self._relations.append(relation)
        self.save()
        return True

    def get_relations(self, name: str) -> List[Tuple[str, str]]:
        """获取某人的关系网络，返回 (对方姓名, 关系描述) 列表。"""
        name = _normalize_name(name)
        result = []
        for r in self._relations:
            if r.person_a == name:
                result.append((r.person_b, r.description))
            elif r.person_b == name:
                result.append((r.person_a, r.description))
        return result

    def find_path(self, name_a: str, name_b: str, max_depth: int = 3) -> Optional[List[str]]:
        """使用 BFS 查找两人之间的连接路径，最多 max_depth 步。

        返回路径上的姓名列表，如果找不到则返回 None。
        """
        name_a = _normalize_name(name_a)
        name_b = _normalize_name(name_b)

        if name_a not in self._persons:
            return None
        if name_b not in self._persons:
            return None
        if name_a == name_b:
            return [name_a]

        # 构建邻接表
        adj: Dict[str, Set[str]] = defaultdict(set)
        for r in self._relations:
            adj[r.person_a].add(r.person_b)
            adj[r.person_b].add(r.person_a)

        # BFS
        visited = {name_a}
        queue: List[Tuple[str, List[str]]] = [(name_a, [name_a])]

        while queue:
            current, path = queue.pop(0)
            if len(path) - 1 >= max_depth:
                continue
            for neighbor in adj.get(current, set()):
                if neighbor == name_b:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    # ── 智能推荐 ──────────────────────────────────

    def recommend(self, query: str) -> List[Person]:
        """按场景推荐人选，基于标签匹配。

        例如："深圳投资" 会推荐标签中包含"深圳"和"投资"相关关键词的人。
        """
        if not query.strip():
            return self.list_all()

        # 提取查询中的关键词
        keywords = re.findall(r"[\w\u4e00-\u9fff]+", query)
        if not keywords:
            return []

        # 计算每个人的匹配分数
        scored: List[Tuple[int, Person]] = []
        for person in self._persons.values():
            score = 0
            person_text = " ".join([
                person.name,
                person.nickname,
                " ".join(person.tags),
                person.bio,
                person.relationship,
            ]).lower()
            for kw in keywords:
                if kw.lower() in person_text:
                    score += 1
            if score > 0:
                scored.append((score, person))

        scored.sort(key=lambda x: -x[0])
        return [p for _, p in scored]
