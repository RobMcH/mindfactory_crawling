from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name='mindfactory_crawling',
    version='1.0.4',
    author="Robert McHardy",
    author_email="robert@robertmchardy.de",
    description="A crawler for mindfactory.de",
    url="https://github.com/RobMcH/mindfactory_crawling",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={'scrapy': ['settings = mindfactory.settings']}, install_requires=['scrapy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
