from setuptools import setup, find_packages

setup(
    name="DisplayManagement",
    version="0.0.1",
    description="A library for managing the Displays connected to EvoCount's PDM",
    url="https://gitlab.com/evocount/display-management",
    author="EvoCount",
    packages=["displaymanagement", "displaymanagement/model_descriptors"],
    python_requires=">=3.0",
    install_requires=["pydantic", "python-xlib"],
)
