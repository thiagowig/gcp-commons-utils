import os.path
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="gcp-commons-utils",
    version="0.1.0",
    description="Utils to be used along Google Cloud Platform components",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/thiagowig/gcp-commons-utils",
    author="Thiago Fonseca",
    author_email="dev.thiago@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=["google-cloud-firestore"],
)
