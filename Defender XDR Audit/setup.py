#!/usr/bin/env python3
"""
Setup script for Defender XDR Audit Tool
"""

from setuptools import setup, find_packages

with open("README_XDR.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="defender-xdr-audit",
    version="1.0.0",
    author="Security Team",
    description="Microsoft Defender XDR security audit and reporting tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "azure-identity>=1.12.0",
        "azure-mgmt-subscription>=3.1.1",
        "azure-core>=1.26.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "defender-xdr-audit=defender_xdr_audit:main",
        ],
    },
)