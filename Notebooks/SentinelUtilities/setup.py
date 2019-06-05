# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import re
import setuptools

INSTALL_REQUIRES = ['azure>=4.0.0']

#with open("README.rst", "r") as f:
#    long_description_text = f.read()
with open("LICENSE.txt", "r") as fh:
    license_txt = fh.read()

setuptools.setup(
    name="Azure-Sentinel-Utilities",
    version="0.1.120",
    author="Azure Sentinel Notebooks Devs",
    author_email="zhzhao@microsoft.com",
    description="AZURE SENTINEL NOTEBOOKS PYTHON TOOLS: This package is developed to support Azure Sentinel Notebooks.  It is in an early preview stage so please provide feedback, report bugs, and suggets for new features.",
    #long_description='',
    #long_description_content_type="text/x-rst",
    license=license_txt,
    url="https://github.com/Azure/Azure-Sentinel",
    python_requires='>=3.6',
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    install_requires=INSTALL_REQUIRES,
    keywords=['security', 'azure', 'sentinel'],
    zip_safe=False,
)
