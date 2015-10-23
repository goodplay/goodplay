# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


install_requires = [
    'ansible>=2.0.0',
    'cached-property>=1.2.0',
    'docker-py>=1.4.0',
    'pytest>=2.5',
    'sarge>=0.1.4',
]

readme_path = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme_path, 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='goodplay',
    version=__import__('goodplay').__version__,
    description='A py.test plugin for testing ansible roles and playbooks.',
    long_description=long_description,

    author='Benjamin Schwarze',
    author_email='benjamin.schwarze@mailboxd.de',
    maintainer='Benjamin Schwarze',
    maintainer_email='benjamin.schwarze@mailboxd.de',

    url='https://goodplay.io/',
    license='Apache License 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],

    entry_points={
        'pytest11': [
            'goodplay = goodplay.plugin',
        ]
    },

    packages=find_packages(),
    package_data={
        '': ['ansible_support/callback_plugin/goodplay.py'],
    },

    install_requires=install_requires,
    zip_safe=False,
)
