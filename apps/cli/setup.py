#!/usr/bin/env python3
"""Setup configuration for CloudGuardian CLI"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cloudguardian-cli",
    version="1.0.0",
    author="CloudGuardian Team",
    author_email="support@cloudguardian.io",
    description="Command-line interface for CloudGuardian security scanning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudguardian/cloudguardian",
    py_modules=["cloudguardian_cli"],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.28.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cloudguardian=cloudguardian_cli:main",
            "cloudguardian-cli=cloudguardian_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
    keywords="security scanning secrets terraform compliance devops",
    project_urls={
        "Bug Tracker": "https://github.com/cloudguardian/cloudguardian/issues",
        "Documentation": "https://docs.cloudguardian.io",
        "Source Code": "https://github.com/cloudguardian/cloudguardian",
    },
)
