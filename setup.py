"""Relationship Network - pip install 配置

纯 Python 标准库实现，零外部依赖。
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rn",
    version="0.3.0",
    description="Relationship Network — A lightweight personal relationship manager. CLI + Python library. Zero dependencies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DannyAce66",
    url="https://github.com/DannyAce66/Relationship_Network",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "rn=rn.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
)
