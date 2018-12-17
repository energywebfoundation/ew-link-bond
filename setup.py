"""
https://pypi.org/
https://pypi.org/classifiers/
"""
import setuptools

setuptools.setup(
    name="energyweb",
    version="0.3.6",
    author="github.com/cerealkill",
    author_email="paul.depraz@energyweb.org",
    description="Energy utility data interface for blockchain smart contracts",
    long_description="Library designed to support the creation of applications for reading, parsing and writing \
    electrical utility related data to and from the blockchain. \n\
    Please visit https://github.com/energywebfoundation/ew-link-bond for more.",
    url="https://github.com/energywebfoundation/ew-link-bond",
    packages=setuptools.find_packages(exclude=["docs", "tests"]),
    install_requires=['web3>=4.8.0,<5.0.0', 'colorlog>=3.1.4'],
    keywords=['ethereum', 'blockchain', 'energy-web', 'energy', 'smart-meter'],
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
