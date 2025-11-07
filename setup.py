#!/usr/bin/env python3
"""
ClaudeCode-Cola - Claude Code Manager
A smart session manager for Claude Code on macOS + iTerm2
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    # Filter out development dependencies
    requirements = [req for req in requirements if not any(dev in req for dev in ['pytest', 'black', 'pylint', 'mypy'])]

setup(
    name="claude-code-cola",
    version="1.0.0",
    author="ClaudeCode-Cola Team",
    author_email="",
    description="A smart session manager for Claude Code on macOS + iTerm2",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ClaudeCode-Cola",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "claude-code-manager=core.main:main",
            "cccl=core.main:main",
        ],
    },
    package_data={
        "": ["*.json", "*.plist", "*.applescript"],
    },
)