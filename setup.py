from setuptools import setup

setup(
    name='pychain',
    version='0.0.1',
    description='Blockchain in python',
    author='Tyler Zeller',
    author_email='tylermzeller@gmail.com',
    packages=['pychain'],
    install_requires=['ecdsa', 'msgpack', 'plyvel']
)
