from setuptools import setup, find_packages

setup(
    name="displaymanagement",
    version="0.0.1",
    description="A library for managing the Displays connected to EvoCount's PDM",
    url="https://github.com/evocount/display-management",
    author="EvoCount GmbH",
    packages=["displaymanagement", "displaymanagement/model_descriptors"],
    python_requires=">=3.6",
    install_requires=["pydantic", "python-xlib", "pyedid"],
)
