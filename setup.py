import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="v2-api-client",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="An API client for V2 of the Trade Remedies API",
    url="https://github.com/uktrade/trs_v2_api_client",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.0",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=[
        "django",
        "requests",
        "api-client",
        "django-cache-memoize",
        "dotwiz",
        "python-dateutil",
        "phonenumbers",
        "pikepdf==7.2.0",
        "openpyxl",
        "lxml",
    ],
)
