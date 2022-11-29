from setuptools import setup, find_packages

setup(
    name="tdict",
    version="0.1.0",
    author="Tsing Wang",
    author_email="tsing.nix@outlook.com",
    description="Text dictionary for command line",
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/tsingwang/tdict",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "td = tdict.main:main",
        ],
    },
    install_requires=[
        "httpx",
        "lxml",
        "cssselect",
        "rich",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
