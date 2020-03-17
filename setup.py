from setuptools import setup, find_packages

setup(
    name="DisplayManagement",
    version="0.0.1",
    description="A library for managing the Displays connected to EvoCount's PDM",
    url="https://gitlab.com/evocount/display-management",
    author="EvoCount",
    package_dir={"": "displaymanagement"},
    packages=find_packages(where="displaymanagement"),
    python_requires=">=3.0",
    install_requires=["pydantic", "python-xlib"],
)
