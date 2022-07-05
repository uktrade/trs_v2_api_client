import os
from setuptools import find_packages, setup
from trade_remedies_client import __author__, __email__
from trade_remedies_client.version import __version__

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='v2-api-client',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='An API client for V2 of the Trade Remedies API',
    url='https://github.com/uktrade/trade-remedies-client',
    author=__author__,
    author_email=__email__,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    install_requires=[
        'django',
        'requests',
        'django-cache-memoize',
    ]
)
