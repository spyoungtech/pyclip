from setuptools import setup
from io import open
import sys
test_requirements = ['pytest']
extras = {'test': test_requirements}

with open('docs/README.md', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pyclip',
    version='0.6.0',
    license='Apache',
    url='https://github.com/spyoungtech/pyclip',
    description='Cross-platform clipboard utilities supporting both binary and text data.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='spencer.young@spyoung.com',
    author='Spencer Young',
    packages=['pyclip'],
    install_requires=[
        'pywin32 >= 1.0 ; platform_system=="Windows"',
        'pasteboard == 0.3.3 ; platform_system=="Darwin"',
    ],
    extras_require=extras,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': ['pyclip = pyclip.cli:main']
    },
    tests_require=test_requirements,
    keywords='pyperclip clipboard cross-platform binary bytes files'
)
