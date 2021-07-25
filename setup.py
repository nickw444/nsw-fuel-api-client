import os
from setuptools import setup

readme_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)),
    'README.md',
)
long_description = open(readme_path).read()

setup(
    name='nsw-fuel-api-client',
    packages=['nsw_fuel'],
    author="Nick Whyte",
    author_email='nick@nickwhyte.com',
    description="API Client for NSW Government Fuel",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nickw444/nsw-fuel-api-client',
    zip_safe=False,
    install_requires=['requests'],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
    test_suite="nsw_fuel_tests",
    tests_require=['requests-mock']
)
