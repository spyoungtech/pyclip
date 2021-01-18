from setuptools import setup
from io import open
import sys
test_requirements = ['pytest']
extras = {'test': test_requirements}

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

if sys.platform == 'win32':
    install_requires = ['pywin32']
else:
    install_requires = []

setup(
    name='pyperclip3',
    version='0.1.0',
    url='https://github.com/spyoungtech/pyperclip3',
    description='Cross-platform clipboard utilities supporting both binary and text data.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='spencer.young@spyoung.com',
    author='Spencer Young',
    packages=['pyperclip3'],
    install_requires=install_requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    tests_require=test_requirements,
)
