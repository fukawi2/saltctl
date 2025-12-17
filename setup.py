#!/usr/bin/env python3
"""Setup script for saltctl"""

from setuptools import setup, find_packages

setup(
    name='saltctl',
    version='0.0.0',  # This will be overridden by git tag during GitHub Actions Workflow
    description='Interactive shell for managing Salt minions',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Phillip Smith',
    author_email='fukawi2@gmail.com',
    url='https://github.com/fukawi2/saltctl',
    license='MIT',
    packages=find_packages(),
    py_modules=['saltctl', 'database', 'config'],
    python_requires='>=3.6',
    install_requires=[
        # No external dependencies - uses only stdlib
    ],
    entry_points={
        'console_scripts': [
            'saltctl=saltctl:main',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: System :: Systems Administration',
    ],
)

# vim: set ts=4 sw=4 et:
