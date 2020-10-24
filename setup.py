from setuptools import setup

VERSION = open("VERSION", "r").read()

setup(
    name='rl-routing',
    packages=['rl_routing'],
    version=VERSION,
    description='reinforcement learning routing environment',
    long_description=open("README.md", "r").read(),
    long_description_content_type='text/markdown',
    include_package_data=True,
    url='https://github.com/lukewood/rl-routing',
    author='Luke Wood',
    author_email='lukewoodcs@gmail.com',
)
