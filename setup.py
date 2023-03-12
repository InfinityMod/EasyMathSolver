import os
from setuptools import setup, find_packages

_cdir = os.path.dirname(__file__)

with open(os.path.join(_cdir, "requirements.txt")) as f:
    install_reqs = f.read().splitlines()

find_packages(include=('module*',))

setup(
    name='easycalc',
    version='1.0',
    description='Calculate formulas in an easy way!',
    author='David Ziegler',
    author_email='david.ziegler@tum.de',
    package_dir={"easycalc": "src"},
    include_package_data=True,
    packages=['easycalc'],    #same as name
    install_requires=list(set(install_reqs)))    #external packages as dependencies
