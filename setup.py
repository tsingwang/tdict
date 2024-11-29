from pathlib import Path
from setuptools import setup, find_packages


def get_version():
    with open(Path(__file__).parent / 'tdict/VERSION') as version_file:
        return version_file.read().strip()

setup(
    name="tdict",
    version=get_version(),
    author="Tsing Wang",
    author_email="tsing.nix@qq.com",
    description="Text dictionary for command line",
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tsingwang/tdict",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "td = tdict.main:main",
        ],
    },
    install_requires=[
        "httpx",
        "lxml",
        "cssselect",
        "SQLAlchemy",
        "rich",
        "textual",
        "playsound",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
