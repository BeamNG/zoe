from setuptools import setup

from Zoe import __name__, __version__, __author__, __author_email__, __description__, __url__, __name__

setup(
  name = __name__,
  version = __version__,  
  description = __description__,
  url = __url__,
  author = __author__,
  author_email = __author_email__,
  license = 'MIT',
  packages = [__name__],
  readme = "README.md",
  install_requires = [
    'coloredlogs',
    'python-dotenv',
    'websocket-client',
    'psutil',
    'appdirs',
    'msgpack',
    'gputil',
    'pyadl',
    'wmi;platform_system=="Windows"',
  ],
  extras_require={
  },
  classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Testing',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Microsoft :: Windows',
    'Programming Language :: Python :: 3',
  ],
)
