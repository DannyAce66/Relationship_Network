"""Relationship Network - 人脉网络管理工具

一个轻量级的个人人脉管理工具，支持标签系统、关系搜索、人脉推荐。
纯 Python 标准库实现，零外部依赖。

Two storage backends / 两种存储模式:
    - JSONL (default): plain text, human-readable, git-friendly
    - SQLite: faster queries, richer relational features

用法示例:
    from rn import RelationshipNetwork, SqliteNetwork, Person, Relationship

    # JSONL mode (default) / 默认 JSONL 模式
    net = RelationshipNetwork()
    net.add_person(Person(name="张三", tags=["投资人", "深圳:#location"]))

    # SQLite mode / SQLite 模式
    net = SqliteNetwork()
    net.add_person(Person(name="John Smith", tags=["investor", "NYC:#location"]))
"""

from .network import Person, Relationship, RelationshipNetwork
from .database import SqliteNetwork

__all__ = ["Person", "Relationship", "RelationshipNetwork", "SqliteNetwork"]
__version__ = "0.3.0"
