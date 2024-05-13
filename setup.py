from setuptools import setup, find_namespace_packages

setup(
    name="aguasgaia",
    version="0.0.11",
    python_requires='>=3',
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    install_requires=[
        'python-dateutil',
        'aiohttp'
    ]
)
