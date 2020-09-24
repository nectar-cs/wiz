import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name="nectwiz",
  version="0.0.226",
  author="Nectar Cloud Software",
  author_email="xavier@codenectar.com",
  description="App Wizard",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/nectar-cs/nectwiz",
  packages = setuptools.find_packages(exclude=[
    "nectwiz.tests.*", "nectwiz.tests"
  ]),
  install_requires=[
    'flask>=1.1',
    'flask-cors',
    'k8kat>=0.0.205',
    'requests',
    'cachetools>=3.1',
    'redis>=3',
    'rq',
    'validators'
  ],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6'
)
