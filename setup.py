from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='imagearchive',
    version='0.1.0',
    description='Image Archive',
    long_description=readme,
    author='Colton Grainger',
    author_email='colton.grainger@gmail.com',
    url='https://github.com/coltongrainger/imagearchive',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

