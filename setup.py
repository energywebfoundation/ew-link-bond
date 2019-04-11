"""
https://pypi.org/
https://pypi.org/classifiers/
"""
import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="energyweb",
    version="0.4.1",
    author="github.com/cerealkill",
    author_email="paul.depraz@energyweb.org",
    description="Energy utility data interface for blockchain smart contracts",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/energywebfoundation/ew-link-bond",
    packages=setuptools.find_packages(exclude=["docs", "tests"]),
    install_requires=['web3>=4.8.0,<5.0.0', 'colorlog>=3.1.4', 'base58>=1.0.3'],
    keywords=['ethereum', 'blockchain', 'energy-web', 'energy', 'smart-energy_meter'],
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
