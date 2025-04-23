#!/usr/bin/env python3
from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gpt-clip',
    version='0.1.0',
    description='Send clipboard content to OpenAI Chat API and copy response back to clipboard.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='',
    author_email='',
    url='',
    py_modules=['cli'],
    install_requires=[
        'openai',
        'pyperclip',
    ],
    entry_points={
        'console_scripts': [
            'gpt-clip=cli:main',
        ],
    },
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Operating System :: OS Independent',
    ],
)