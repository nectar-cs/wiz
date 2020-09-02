import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name="nectwiz",
  version="0.0.16",
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
    'k8-kat>=0.0.156',
    'kubernetes>=10.0.1',
    'requests',
    'urllib3>=1.25',
    'cachetools>=3.1',
    'rsa>=4.0',
    'validators',
    'six>=1.12.0',
    'inflection'
  ],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6'
)
