import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ew-link-bond",
    version="0.2.0",
    author="Jean Paul Depraz",
    author_email="paul.depraz@energyweb.org",
    description="Energy data interface for blockchain smart contracts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/energywebfoundation/ew-link-bond",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Intended Audience :: Science/Research",
        "Environment :: Console",
        "Development Status :: 2 - Pre-Alpha"
    ],
)