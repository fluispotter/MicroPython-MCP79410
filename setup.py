import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='MicroPython-MCP79410',
    version='0.0.1',
    author='Fluispotter',
    description='MicroPython driver for the MCP79410 real-time clock IC',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fluispotter/MicroPython-MCP79410',
    license='ISC',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Topic :: System :: Hardware'
    ],
    python_requires='>=3.9',
)
