from setuptools import setup, find_packages

setup(
    name = 'SimpleDownloader',
    version = '0.1.1',
    url = 'https://github.com/Liumkattan/SimpleDownloader.git',
    license='GPLv3',
    author = 'Lium Kattan',
    author_email = 'liumkattan@gmail.com',
    description = 'Simple and fast python module and command-line downloader.',
    packages = find_packages(),    
    install_requires = ['requests>=2.19.1'],
)