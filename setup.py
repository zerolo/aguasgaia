from setuptools import setup, find_namespace_packages

setup(
    name="aguasgaia",
    version="0.0.20",
    python_requires='>=3',
    package_dir={'': '.'},
    packages=find_namespace_packages(where='.'),
    install_requires=[
        'python-dateutil'
    ]
)
