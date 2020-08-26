import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name="nectwiz",
  version="0.0.04",
  author="Nectar Cloud Software",
  author_email="xavier@codenectar.com",
  description="App Wizard",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/nectar-cs/wiz",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires='>=3.6'
)
