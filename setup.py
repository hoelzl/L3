from setuptools import setup, find_packages

setup(
    name='l3',
    version='0.0.1',
    url='https://github.com/hoelzl/l3.git',
    author='Dr. Matthias Hölzl',
    author_email='tc@xantira.com',
    description='Simple game examples for online trainings',
    packages=find_packages(),    
    install_requires=['pygame >= 2.0.1', 'cytoolz >= 0.11.0'],
)
