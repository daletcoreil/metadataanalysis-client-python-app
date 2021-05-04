# coding: utf-8

"""
    Dalet Media Metadata Analysis App
    OpenAPI spec version: 1.2.0
    Contact: cortexsupport@dalet.com
"""

from setuptools import setup, find_packages  # noqa: H301

NAME = "metadataanalysis-client-app"
VERSION = "1.2.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "boto3 >= 1.9.153",
    "botocore >= 1.12.153",
    "certifi",
    "docutils",
    "jmespath",
    "python-dateutil",
    "s3transfer",
    "six",
    "urllib3"
]

DEPENDENCY_LINKS = []

setup(
    name=NAME,
    version=VERSION,
    description="Dalet Media Metadata Analysis App",
    author_email="cortexsupport@dalet.com",
    url="",
    keywords=["Dalet Metadata Analysis", "Dalet Media Metadata Analysis App"],
    install_requires=REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    packages=find_packages(),
    include_package_data=True,
    long_description=""
)