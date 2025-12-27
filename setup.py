from setuptools import find_packages, setup

NAME = "netapp.santricity"
VERSION = "1.1"


# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 2.5.0", "certifi", "python-dateutil"]

setup(
    name=NAME,
    version=VERSION,
    description="Python SDK for accessing NetApp Santricity Web Services",
    author="scaleoutsean",
    license="The Clear BSD License",
    author_email="",
    url="https://github.com/scaleoutsean/santricity-webapi-pythonsdk",
    keywords=["Swagger", "NetApp", "Santricity"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.14",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3.15",
    ],
    long_description="""\
    NetApp E-Series SANtricity Python SDK for Web Services
    """,
)
