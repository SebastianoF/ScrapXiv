#!/usr/bin/env python3

import pathlib

import pkg_resources
from setuptools import find_packages, setup

with pathlib.Path("requirements.txt").open() as requirements_txt:
    requirements = [
        str(requirement)
        for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]


setup(
    name="scrapxiv",
    version="v0.0.0",
    description="Scraping information form arxiv.",
    author="sebastiano ferraris",
    author_email="sebastiano.ferraris@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    license="None",
    python_requires=">=3.7",
    url="https://github.com/SebastianoF/scrapxiv",
    packages=find_packages(include=["scapxiv"], exclude=["examples", "tests"]),
    install_requires=requirements,
    entry_points={"console_scripts": ["scrapxiv=scrapxiv.cli:cli"]},
)
