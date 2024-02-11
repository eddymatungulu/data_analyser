from setuptools import find_packages, setup

with open("app/README.md", "r") as f:
    long_description = f.read()

setup(
    name="analyser",
    version="0.0.1",
    description="Allow a group of analysts to make sense of the signal data",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eddymatungulu/data_analyser/tree/main",
    author="Eddy Matungulu",
    author_email="eddymatcisco@gmail.com",
    license="Apache License",
    classifiers=[
        "License :: OSI Approved :: Apache License",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "statistics"],
    extras_require={
        "dev": ["pytest>=7.0", "twine>=4.0.2"],
    },
    python_requires=">=3.11",
)