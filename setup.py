# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


install_requires = [
    'ansible>=2.5',
    'cached-property>=1.3.1',
    'docker-compose>=1.22.0',
    'py>=1.4.34',
    'pytest>=3.5.0',
    'sarge>=0.1.5',
]

readme_path = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme_path, 'r') as readme_file:
    long_description = readme_file.read()

setup(
    name='goodplay',
    version=__import__('goodplay').__version__,
    description='goodplay enables you to test your deployments and '
                'distributed software infrastructure by reusing your '
                'existing knowledge of Ansible.',
    long_description=long_description,

    author='Benjamin Schwarze',
    author_email='benjamin.schwarze@mailboxd.de',
    maintainer='Benjamin Schwarze',
    maintainer_email='benjamin.schwarze@mailboxd.de',

    url='https://goodplay.io/',

    license='Apache License 2.0',
    keywords=[
        'goodplay', 'good', 'play', 'test', 'deployment', 'ansible',
        'playbook', 'role', 'integration', 'system', 'tdd', 'configuration',
        'management'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
    ],

    entry_points={
        'console_scripts': [
            'goodplay = goodplay.cli:main',
        ],
        'pytest11': [
            'goodplay = goodplay.plugin',
        ]
    },
    packages=find_packages(),
    package_data={
        '': [
            'ansible_support/callback_plugin/goodplay.py',
            'ansible_support/connection_plugin/goodplaydocker.py',
        ],
    },
    install_requires=install_requires,
    zip_safe=False,
)
