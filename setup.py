from setuptools import setup

setup(name="dave",
      version="0.0.1",
      packages=["dave"],
      entry_points={
          'console_scripts': [
              'dave-server = dave.server:main'
          ]
      },
      )
