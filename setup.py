# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name='mindfactory',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = mindfactory.settings']}, install_requires=['scrapy']
)
