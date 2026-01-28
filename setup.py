"""
Setup configuration for DraftShift package.
Enables installation and CLI entry point.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="draftshift",
    version="0.1.0",
    description="Litigation document automation platform for California civil pleadings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Taurin Robinson",
    author_email="trobinson@draftshiftlaw.com",
    license="Proprietary",
    packages=find_packages(),
    package_data={
        "draftshift": [
            "formats/*.yaml",
            "tests/fixtures/*.json",
        ],
    },
    python_requires=">=3.8",
    install_requires=[
        "python-docx>=0.8.11",
        "pyyaml>=5.4.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "draftshift=draftshift.pleadings.cli:build_from_json",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Law",
    ],
    keywords="litigation documents pleadings california law",
)
