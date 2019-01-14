from setuptools import setup, find_packages
try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements
import os

requirements_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
install_requires = parse_requirements(requirements_path, session='hack')
install_requires = [str(ir.req) for ir in install_requires]

setup(
    name='facebook_page_crawler',
    version='0.0.1',
    description='The crawler of Facebook pages.',
    url='https://github.com/chenjr0719/Facebook-Page-Crawler',
    author='Jacob Chen',
    author_email='chenjr0719@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests', 'Results']),
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'facebook_page_crawler = facebook_page_crawler.__main__:main'
        ]
    },
)
