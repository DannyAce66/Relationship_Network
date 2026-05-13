"""Relationship Network - 人脉网络管理工具

一个轻量级的个人人脉管理工具，支持标签系统、关系搜索、人脉推荐。
纯 Python 标准库实现，零外部依赖。

用法示例:
    from rn import RelationshipNetwork, Person, Relationship

    net = RelationshipNetwork()
    net.add_person(Person(name="张三", tags=["投资人", "深圳:#location"]))
    net.add_relation(Relationship("张三", "李四", "合作伙伴"))
    results = net.search("投资")
    path = net.find_path("张三", "李四")
"""

from .network import Person, Relationship, RelationshipNetwork

__all__ = ["Person", "Relationship", "RelationshipNetwork"]
__version__ = "0.1.0"
