#!/usr/bin/env python3
"""Relationship Network - 命令行工具

提供 add / search / list / remove / path / recommend / relation / tagcloud 子命令。

用法:
    rn add "张三,投资人,深圳,通过会议认识"
    rn search 投资
    rn list
    rn path 张三 李四
    rn recommend 深圳投资
"""

import argparse
import sys
import textwrap
from pathlib import Path

from .network import (
    RelationshipNetwork,
    Person,
    Relationship,
    _parse_tags,
)


def _format_person(person: Person, index: int = 0) -> str:
    """格式化联系人信息为可读字符串。"""
    if index > 0:
        header = f"\n{'='*40}\n#{index}\n{'='*40}"
    else:
        header = ""
    parts = [header, f"姓名: {person.name}"]
    if person.nickname:
        parts.append(f"昵称: {person.nickname}")
    if person.tags:
        parts.append(f"标签: {', '.join(person.tags)}")
    if person.bio:
        parts.append(f"简介: {person.bio}")
    if person.met_how:
        parts.append(f"认识方式: {person.met_how}")
    if person.relationship:
        parts.append(f"与我的关系: {person.relationship}")
    if person.notes:
        parts.append(f"备注: {person.notes}")
    return "\n".join(parts)


def _parse_add_args(args: list[str]) -> tuple:
    """解析 add 命令的参数。

    支持两种格式:
    1. "姓名,标签1,标签2,认识方式" (简写)
    2. --name 姓名 --tags 标签 --met-how 认识方式 (完整)
    """
    if not args:
        return None

    text = " ".join(args)

    # 如果包含 -- 参数，用 argparse 解析
    if any(a.startswith("--") for a in args):
        parser = argparse.ArgumentParser()
        parser.add_argument("--name", required=True)
        parser.add_argument("--nickname", default="")
        parser.add_argument("--tags", default="")
        parser.add_argument("--bio", default="")
        parser.add_argument("--met-how", default="")
        parser.add_argument("--relationship", default="")
        parser.add_argument("--notes", default="")
        ns, _ = parser.parse_known_args(args)
        return Person(
            name=ns.name,
            nickname=ns.nickname,
            tags=_parse_tags(ns.tags),
            bio=ns.bio,
            met_how=ns.met_how,
            relationship=ns.relationship,
            notes=ns.notes,
        )

    # 简写格式: "姓名,标签,标签,认识方式"
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if not parts:
        return None
    name = parts[0]
    # 尝试从后面的参数中区分标签和认识方式
    # 如果parts长度>=3，中间的是标签最后一个是认识方式
    tags = []
    met_how = ""
    relationship = ""
    if len(parts) >= 2:
        # 看最后是否包含 "通过"/"经" 字样的认识方式
        last = parts[-1]
        if any(kw in last for kw in ["通过", "经", "在", "朋友介绍"]):
            met_how = last
            if len(parts) >= 3:
                tags = parts[1:-1]
        else:
            # 尝试看是否有"与我的关系:xxx"格式
            found_rel = False
            for i, p in enumerate(parts[1:], 1):
                if p.startswith("关系:") or p.startswith("rel:"):
                    relationship = p.split(":", 1)[1].strip()
                    found_rel = True
                    break
            if found_rel:
                rel_idx = parts.index(p)
                tags = parts[1:rel_idx]
            else:
                tags = parts[1:]
    return Person(name=name, tags=tags, met_how=met_how, relationship=relationship)


def cmd_add(net: RelationshipNetwork, args: list[str]) -> None:
    """添加联系人。"""
    person = _parse_add_args(args)
    if person is None:
        print("错误: 请提供联系人信息，例如: rn add \"张三,投资人,深圳\"")
        sys.exit(1)

    try:
        if net.add_person(person):
            print(f"✓ 已添加联系人: {person.name}")
        else:
            # 已存在，询问是否更新
            print(f"联系人 '{person.name}' 已存在，自动合并更新。")
            net.add_or_update_person(person)
            print(f"✓ 已更新联系人: {person.name}")
    except ValueError as e:
        print(f"错误: {e}")
        sys.exit(1)


def cmd_search(net: RelationshipNetwork, args: list[str]) -> None:
    """搜索联系人。"""
    keyword = " ".join(args) if args else ""
    results = net.search(keyword)

    if not results:
        if keyword:
            print(f"未找到匹配 '{keyword}' 的联系人。")
        else:
            print("人脉列表为空。")
        return

    print(f"找到 {len(results)} 个联系人:\n")
    for i, person in enumerate(results, 1):
        print(_format_person(person, i))
        print()


def cmd_list(net: RelationshipNetwork, args: list[str]) -> None:
    """列出所有联系人。"""
    cmd_search(net, [])


def cmd_remove(net: RelationshipNetwork, args: list[str]) -> None:
    """删除联系人。"""
    if not args:
        print("错误: 请提供要删除的姓名，例如: rn remove 张三")
        sys.exit(1)
    name = " ".join(args)
    if net.remove_person(name):
        print(f"✓ 已删除联系人: {name}")
    else:
        print(f"联系人 '{name}' 不存在。")


def cmd_path(net: RelationshipNetwork, args: list[str]) -> None:
    """查找两个人之间的连接路径。"""
    if len(args) < 2:
        print("错误: 请提供两个姓名，例如: rn path 张三 李四")
        sys.exit(1)

    name_a, name_b = args[0], args[1]
    path = net.find_path(name_a, name_b)

    if path is None:
        print(f"未找到 '{name_a}' 与 '{name_b}' 之间的连接路径（最多3步）。")
        print("提示: 可以使用 rn relation <姓名> 查看已有关系。")
        return

    print(f"找到连接路径 ({len(path)-1} 步):")
    for i, name in enumerate(path):
        if i == 0:
            print(f"  {name}")
        else:
            # 获取关系描述
            rels = []
            for r in net._relations:
                if (r.person_a == path[i-1] and r.person_b == name) or \
                   (r.person_a == name and r.person_b == path[i-1]):
                    rels.append(r.description)
                    break
            desc = f" —— {rels[0] if rels else '认识'} ——> " if i > 0 else " ——> "
            print(f"  {desc}{name}")


def cmd_recommend(net: RelationshipNetwork, args: list[str]) -> None:
    """智能推荐联系人。"""
    query = " ".join(args) if args else ""
    results = net.recommend(query)

    if not results:
        if query:
            print(f"未找到匹配 '{query}' 的推荐人选。")
        else:
            print("人脉列表为空。")
        return

    print(f"按场景 '{query}' 推荐 {len(results)} 个联系人:\n")
    for i, person in enumerate(results, 1):
        print(_format_person(person, i))
        print()


def cmd_relation(net: RelationshipNetwork, args: list[str]) -> None:
    """管理关系或查看某人的关系网络。"""
    if not args:
        print("错误: 请提供子命令或姓名。")
        print("用法:")
        print("  rn relation <姓名>          查看某人的关系网络")
        print("  rn relation add <A> <B> [描述]  添加关系")
        sys.exit(1)

    if args[0] == "add" and len(args) >= 3:
        name_a, name_b = args[1], args[2]
        desc = " ".join(args[3:]) if len(args) > 3 else ""
        try:
            net.add_relation(Relationship(name_a, name_b, desc))
            print(f"✓ 已添加关系: {name_a} <-> {name_b}")
            if desc:
                print(f"  描述: {desc}")
        except ValueError as e:
            print(f"错误: {e}")
            sys.exit(1)
        return

    # 查看某人的关系网络
    name = " ".join(args)
    relations = net.get_relations(name)

    if not relations:
        person = net.get_person(name)
        if person is None:
            print(f"联系人 '{name}' 不存在。")
        else:
            print(f"'{name}' 暂无关系记录。")
        return

    print(f"'{name}' 的关系网络:\n")
    for other, desc in relations:
        d = f" —— {desc}" if desc else ""
        print(f"  {name}{d} ——> {other}")


def cmd_tagcloud(net: RelationshipNetwork, args: list[str]) -> None:
    """显示标签云统计。"""
    cloud = net.tag_cloud()
    if not cloud:
        print("暂无标签数据。")
        return

    print("标签云（按使用频率排序）:\n")
    max_count = max(cloud.values()) if cloud else 1
    for tag, count in cloud.items():
        bar_length = int(count / max_count * 20)
        bar = "█" * bar_length
        print(f"  {tag:20s} {bar} {count}")


def cmd_stats(net, args: list[str]) -> None:
    """显示数据库统计信息 (SQLite 模式)。"""
    if not hasattr(net, 'stats'):
        print("stats 命令仅支持 SQLite 模式 (--db)。")
        print("JSONL 模式请直接查看数据文件: ~/.rn/persons.jsonl")
        return
    s = net.stats()
    print(f"数据库: {s['db_path']}")
    print(f"联系人数量: {s['person_count']}")
    print(f"关系数量: {s['relation_count']}")
    print(f"标签种类: {s['tag_count']}")


def main() -> None:
    """命令行入口函数。"""
    parser = argparse.ArgumentParser(
        prog="rn",
        description="Relationship Network - 人脉网络管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            使用示例:
              rn add "张三,投资人,深圳,通过会议认识"
              rn add --name 李四 --tags 设计师,北京 --met-how 朋友介绍
              rn search 投资
              rn list
              rn remove 张三
              rn path 张三 李四
              rn recommend 深圳投资
              rn relation 张三
              rn relation add 张三 李四 合作伙伴
              rn tagcloud
        """),
    )
    parser.add_argument(
        "--data",
        default="",
        help="JSONL 数据文件路径（默认: ~/.rn/persons.jsonl）",
    )
    parser.add_argument(
        "--db",
        default="",
        help="SQLite 数据库路径（默认: ~/.rn/network.db）。使用此参数将切换到 SQLite 模式。",
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 为了兼容无子命令的直接参数调用，保留 parse_known_args
    # 但子命令方式优先

    # 注册所有子命令（用于 --help 显示）
    for cmd, help_text in [
        ("add", "添加联系人"),
        ("search", "搜索联系人"),
        ("list", "列出所有联系人"),
        ("remove", "删除联系人"),
        ("path", "查找两人之间的连接路径"),
        ("recommend", "按场景推荐联系人"),
        ("relation", "管理关系网络"),
        ("tagcloud", "显示标签云"),
        ("stats", "数据库统计信息 (SQLite 模式)"),
    ]:
        sp = subparsers.add_parser(cmd, help=help_text)

    # 解析参数
    known, unknown = parser.parse_known_args()

    # 初始化网络 — JSONL 或 SQLite
    if known.db:
        from .database import SqliteNetwork
        net = SqliteNetwork(db_path=known.db if known.db else None)
    else:
        net = RelationshipNetwork(data_path=known.data if known.data else None)

    # 执行命令
    command_map = {
        "add": cmd_add,
        "search": cmd_search,
        "list": cmd_list,
        "remove": cmd_remove,
        "path": cmd_path,
        "recommend": cmd_recommend,
        "relation": cmd_relation,
        "tagcloud": cmd_tagcloud,
        "stats": cmd_stats,
    }

    if known.command:
        command_map[known.command](net, unknown)
    else:
        # 如果没有子命令，尝试将位置参数当作 add 命令处理
        # 或者显示帮助
        if unknown:
            cmd_add(net, unknown)
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
