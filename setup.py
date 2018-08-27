"""
https://pypi.org/
https://pypi.org/classifiers/
"""
import setuptools

setuptools.setup(
    name="ew-link-bond",
    version="0.2.1",
    author="Jean Paul Depraz",
    author_email="paul.depraz@energyweb.org",
    description="Energy data interface for blockchain smart contracts",
    long_description="Library designed to support the creation of interfaces for reading, parsing and writing energy \
    industry related data to and from the blockchain. \n\
    Please visit https://github.com/energywebfoundation/ew-link-bond for more.",
    long_description_content_type="text/markdown",
    url="https://github.com/energywebfoundation/ew-link-bond",
    packages=setuptools.find_packages(exclude=["docs", "tests"]),
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