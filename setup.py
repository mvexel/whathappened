from setuptools import setup

setup(
    name='whathappened',
    packages=['whathappened'],
    include_package_data=True,
    install_requires=[
        'flask',
        'requests'
    ],
)
