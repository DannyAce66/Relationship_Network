"""Relationship Network — SQLite storage backend

Provides the same API as the JSONL-based RelationshipNetwork, backed by SQLite.
SQLite is part of Python's standard library — still zero external dependencies.

Usage:
    from rn.database import SqliteNetwork
    net = SqliteNetwork()                              # default: ~/.rn/network.db
    net = SqliteNetwork(db_path="mydata/contacts.db")  # custom path
"""

import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .network import Person, Relationship, _normalize_name

_DEFAULT_DB_DIR = Path.home() / ".rn"
_DEFAULT_DB_FILE = _DEFAULT_DB_DIR / "network.db"


def _get_db_path(db_path: Optional[str] = None) -> Path:
    if db_path:
        return Path(db_path)
    return _DEFAULT_DB_FILE


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    nickname TEXT DEFAULT '',
    tags TEXT DEFAULT '[]',
    bio TEXT DEFAULT '',
    met_how TEXT DEFAULT '',
    relationship TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT DEFAULT '',
    updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_a TEXT NOT NULL,
    person_b TEXT NOT NULL,
    relation_type TEXT DEFAULT '',
    context TEXT DEFAULT '',
    created_at TEXT DEFAULT '',
    FOREIGN KEY (person_a) REFERENCES persons(name) ON DELETE CASCADE,
    FOREIGN KEY (person_b) REFERENCES persons(name) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_relations_a ON relations(person_a);
CREATE INDEX IF NOT EXISTS idx_relations_b ON relations(person_b);
"""


class SqliteNetwork:
    """SQLite-backed relationship network with the same API as RelationshipNetwork."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = _get_db_path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def close(self):
        self._conn.close()

    # ── helpers ────────────────────────────────────

    def _now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _tags_to_json(self, tags: List[str]) -> str:
        return json.dumps(tags or [], ensure_ascii=False)

    def _tags_from_json(self, raw: str) -> List[str]:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

    def _row_to_person(self, row: sqlite3.Row) -> Person:
        return Person(
            name=row["name"],
            nickname=row["nickname"] or "",
            tags=self._tags_from_json(row["tags"]),
            bio=row["bio"] or "",
            met_how=row["met_how"] or "",
            relationship=row["relationship"] or "",
            notes=row["notes"] or "",
        )

    # ── CRUD ───────────────────────────────────────

    def add_person(self, person: Person) -> bool:
        name = person.name
        if not name:
            raise ValueError("姓名不能为空")

        existing = self._conn.execute(
            "SELECT name FROM persons WHERE name = ?", (name,)
        ).fetchone()
        if existing:
            return False

        now = self._now()
        self._conn.execute(
            """INSERT INTO persons (name, nickname, tags, bio, met_how, relationship, notes, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, person.nickname, self._tags_to_json(person.tags),
             person.bio, person.met_how, person.relationship,
             person.notes, now, now),
        )
        self._conn.commit()
        return True

    def add_or_update_person(self, person: Person) -> bool:
        name = person.name
        if not name:
            raise ValueError("姓名不能为空")

        existing = self._conn.execute(
            "SELECT * FROM persons WHERE name = ?", (name,)
        ).fetchone()

        now = self._now()
        if existing:
            # merge tags
            old_tags = self._tags_from_json(existing["tags"])
            merged_tags = sorted(set(old_tags) | set(person.tags))
            # merge notes
            merged_notes = existing["notes"] or ""
            if person.notes:
                merged_notes = (merged_notes + "\n" + person.notes).strip()

            self._conn.execute(
                """UPDATE persons SET nickname=?, tags=?, bio=?, met_how=?,
                   relationship=?, notes=?, updated_at=?
                 WHERE name=?""",
                (person.nickname or existing["nickname"],
                 self._tags_to_json(merged_tags),
                 person.bio or existing["bio"],
                 person.met_how or existing["met_how"],
                 person.relationship or existing["relationship"],
                 merged_notes,
                 now, name),
            )
            self._conn.commit()
            return False
        else:
            self._conn.execute(
                """INSERT INTO persons (name, nickname, tags, bio, met_how, relationship, notes, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, person.nickname, self._tags_to_json(person.tags),
                 person.bio, person.met_how, person.relationship,
                 person.notes, now, now),
            )
            self._conn.commit()
            return True

    def get_person(self, name: str) -> Optional[Person]:
        row = self._conn.execute(
            "SELECT * FROM persons WHERE name = ?", (_normalize_name(name),)
        ).fetchone()
        if row:
            return self._row_to_person(row)
        return None

    def search(self, keyword: str = "") -> List[Person]:
        if not keyword or not keyword.strip():
            rows = self._conn.execute("SELECT * FROM persons ORDER BY name").fetchall()
            return [self._row_to_person(r) for r in rows]

        kw = f"%{keyword.strip()}%"
        rows = self._conn.execute(
            """SELECT * FROM persons
               WHERE name LIKE ? OR nickname LIKE ? OR tags LIKE ?
                  OR bio LIKE ? OR met_how LIKE ? OR relationship LIKE ?
                  OR notes LIKE ?
               ORDER BY name""",
            (kw, kw, kw, kw, kw, kw, kw),
        ).fetchall()
        return [self._row_to_person(r) for r in rows]

    def remove_person(self, name: str) -> bool:
        name = _normalize_name(name)
        row = self._conn.execute(
            "SELECT name FROM persons WHERE name = ?", (name,)
        ).fetchone()
        if not row:
            return False
        self._conn.execute("DELETE FROM relations WHERE person_a = ? OR person_b = ?", (name, name))
        self._conn.execute("DELETE FROM persons WHERE name = ?", (name,))
        self._conn.commit()
        return True

    def list_all(self) -> List[Person]:
        rows = self._conn.execute("SELECT * FROM persons ORDER BY name").fetchall()
        return [self._row_to_person(r) for r in rows]

    # ── tag system ─────────────────────────────────

    def tag_cloud(self) -> Dict[str, int]:
        counter: Counter = Counter()
        rows = self._conn.execute("SELECT tags FROM persons").fetchall()
        for row in rows:
            for tag in self._tags_from_json(row["tags"]):
                counter[tag] += 1
        return dict(counter.most_common())

    def search_by_tags(self, tag_keywords: List[str]) -> List[Person]:
        if not tag_keywords:
            return self.list_all()

        results = []
        rows = self._conn.execute("SELECT * FROM persons").fetchall()
        for row in rows:
            tags = self._tags_from_json(row["tags"])
            tag_text = " ".join(tags).lower()
            if all(kw.lower() in tag_text for kw in tag_keywords):
                results.append(self._row_to_person(row))
        return results

    # ── relations ──────────────────────────────────

    def add_relation(self, relation: Relationship) -> bool:
        a = relation.person_a
        b = relation.person_b

        # verify both exist
        for name in [a, b]:
            exists = self._conn.execute(
                "SELECT name FROM persons WHERE name = ?", (name,)
            ).fetchone()
            if not exists:
                raise ValueError(f"联系人 '{name}' 不存在")

        self._conn.execute(
            """INSERT INTO relations (person_a, person_b, relation_type, context, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (a, b, relation.description, "", self._now()),
        )
        self._conn.commit()
        return True

    def get_relations(self, name: str) -> List[Tuple[str, str]]:
        name = _normalize_name(name)
        rows = self._conn.execute(
            "SELECT person_a, person_b, relation_type FROM relations WHERE person_a = ? OR person_b = ?",
            (name, name),
        ).fetchall()
        result = []
        for r in rows:
            other = r["person_b"] if r["person_a"] == name else r["person_a"]
            result.append((other, r["relation_type"] or ""))
        return result

    def find_path(self, name_a: str, name_b: str, max_depth: int = 3) -> Optional[List[str]]:
        name_a = _normalize_name(name_a)
        name_b = _normalize_name(name_b)

        if name_a == name_b:
            return [name_a]

        # verify both exist
        for name in [name_a, name_b]:
            exists = self._conn.execute(
                "SELECT name FROM persons WHERE name = ?", (name,)
            ).fetchone()
            if not exists:
                return None

        # build adjacency list from SQLite
        adj: Dict[str, Set[str]] = defaultdict(set)
        rows = self._conn.execute("SELECT person_a, person_b FROM relations").fetchall()
        for r in rows:
            adj[r["person_a"]].add(r["person_b"])
            adj[r["person_b"]].add(r["person_a"])

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

    # ── recommend ──────────────────────────────────

    def recommend(self, query: str) -> List[Person]:
        if not query.strip():
            return self.list_all()

        keywords = re.findall(r"[\w\u4e00-\u9fff]+", query)
        if not keywords:
            return []

        scored: List[Tuple[int, Person]] = []
        rows = self._conn.execute("SELECT * FROM persons").fetchall()

        for row in rows:
            person = self._row_to_person(row)
            person_text = " ".join([
                person.name, person.nickname,
                " ".join(person.tags), person.bio, person.relationship,
            ]).lower()
            score = sum(1 for kw in keywords if kw.lower() in person_text)
            if score > 0:
                scored.append((score, person))

        scored.sort(key=lambda x: -x[0])
        return [p for _, p in scored]

    # ── extra: stats ───────────────────────────────

    def stats(self) -> Dict:
        """Return database statistics."""
        person_count = self._conn.execute(
            "SELECT COUNT(*) FROM persons"
        ).fetchone()[0]
        relation_count = self._conn.execute(
            "SELECT COUNT(*) FROM relations"
        ).fetchone()[0]
        return {
            "db_path": str(self.db_path),
            "person_count": person_count,
            "relation_count": relation_count,
            "tag_count": len(self.tag_cloud()),
        }
