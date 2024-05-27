
## Overview
This repository contains the source code and testing script associated with the Master's thesis titled: **Gentoo Linux as Software Product Line: An Analysis** submitted by **Sarvech** to **Chair of Software Engineering** at **University of Saarland** . The thesis explores the translation of Gentoo packages to feature models, as well as analysis to boost future work in exploring Gentoo repositories.

This repository serves as a companion to the aforementioned Master's thesis. Consulting the thesis document will provide a deeper understanding of the research context, methodology, and expected outcomes of the feature modeling approach.

#### Contents:
> gentoo_feature_modelling.py

This Python script embodies the core logic for converting Gentoo packages into corresponding feature models. It includes functions for parsing package information, constructing feature model elements, and handling various specific scenarios.

> run_gentoo_feature_modelling.ipynb

This Jupyter Notebook serves as a testing and demonstration environment. It showcases how to utilize the gentoo_feature_modelling.py script to convert Gentoo packages and generate feature models. The notebook likely step-by-step code examples.


#### Purpose:
This repository aims to provide transparency and reproducibility for the research presented in the thesis. Facilitate further exploration and potential enhancements of the proposed Gentoo package feature modeling approach. Offering a starting point for researchers interested in bridging the gap between software engineering and the Gentoo Linux community through feature models.


## Getting Started

#### Prerequisites: 
This repository needs to run within Gentoo Linux as it utilizes the [Portage API](https://dev.gentoo.org/~zmedico/portage/doc/api/portage.dbapi.html) to access the repository. 

I have also used [vara-feature](https://github.com/se-sic/vara-feature) to create the feature models. Make sure it is installed by heading to the link above, it contains detailed instructions for installing as well as compiling the package.  

You should also have [Jupyter](https://jupyter.org/) installed if you want to run the test script as is, or else you can simply extract the python code from the notebook and run it as a .py file (which I wont recommend as it runs over the entire repository). 

For dependencies, I used the following packages throughout the code(s):
- os 
- logging
- nest_asyncio
- datetime 
- collections

These are common packages that are often bundled in when installing Python. You can test them by running `import packageName`  to make sure everything is already installed. Alternatively, run `pip install packageName` for any missing via the commandline.


#### Future Work:
This reseach lays the groundwork for further exploration in several areas which are discussed thoroughly in the thesis itself and include: 
- creating a large-scale feature model with all packages as a feature with cross tree constraints
- analysing inter dependecies of packages within the Gentoo repository
- analysing the repository over time
- and more

I welcome any contributions to this project. Feel free to submit pull requests for bug fixes, enhancements, or alternative approaches to any of the process steps.




## Housekeeping
#### Citation:
If you utilize any part of this code or the research findings in your own work, please cite the following reference:
___ insert the reference from SE website once published ___

#### Contact:
For any inquiries or feedback, please reach out to here or on LinkedIn/sarvech76.