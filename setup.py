from setuptools import setup, find_packages


def requirements() -> list:
    return [
        'click==6.7',
        'curio==0.8',
        'asks==1.3.6',
        'yarl==0.15.0',
        'lxml==4.1.1',
        'beautifulsoup4==4.6.0',
        'tabulate==0.8.2',
    ]


setup(
    name='igd',
    version='0.1.0',
    description='IGD management CLI tool.',
    long_description=open('README.rst').read(),
    url='https://github.com/povilasb/pyigd',
    author='Povilas Balciunas',
    author_email='balciunas90@gmail.com',
    license='MIT',
    packages=find_packages(exclude=('tests')),
    entry_points={
        'console_scripts': ['igd = igd.__main__:main']
    },
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
    ],
    install_requires=requirements(),
)
