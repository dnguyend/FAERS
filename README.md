# Analysis of FDA Adverse Event Reporting System (FAERS) Data

The TXT format Adverse Event data published by the FDA on their webpage is contained in seven files according to the following Entity Relationship Diagram:

![FAERS](https://github.com/dnguyend/FAERS/blob/master/FAERS_ERD.PNG)

We analyzed the data in this project and share open-source code used in the analysis. Code is written in python, using pandas as the main data library, numpy as the main computation library, jupyter notebook as the main UI. Pandas data frame maps pretty well with R data frame so we expect the conversion to R is easy if necessary.

As part of the project we:
* Develop python scripts to automatically pull and extract data to a data directory under the current directory.
* Provide some library functions to be shared by programs in the project, between notebooks and stand-alone scripts.
* Provide some library functions to help load the downloaded text files to data frames to be used in the analysis. Provide some typical links between the data frames, as well as a few potentially useful functions.
* Show the distribution of adverse events (reaction) by drug by country (reporter country as well as occurrence country). Provide a basic GUI where the user can select a drug and see reported events by country.
* Show distribution of reaction by disease.  We also provide a GUI where the user can select a drug, see the indication point (where the drug is used for treatment), and then show the reaction by drug and indication point.
* Show the top pairs of drugs often used together. For each drug, we provide a dropdown box showing the list of top drugs used together with it (we currently ignore therapy period; this could be addressed).
* Enriching the data to convert weight, dosage, daily frequency to uniformed units to provide a Logistic Regression trying to link the severity of outcome to patient's age, weight and daily dosage. As part of this, we pull data related to units of those fields from PDF form to txt file, usable by codes.
* Logistic regression links age to the severity of outcome. Weight or dosage has a small effect. This observation is tested with data over several quarters. 
 # Organization of files:
 * faers_lib contains the library modules.  We place several functions in faers_lib so the main notebook does not get too long.
    * fayers_lib/download.py: modules with functions to download/extract files
    * fayers_lib/analyze.py: modules to load files to data frames, and do a few basic aggregation.
 * cfg contains several supporting files providing additional information to a number of fields, mainly explaining the abbreviations and providing unit conversion:
    * cfg/convert.txt: Unit conversion.
    * cfg/extra.json: Explanation of abbreviations.
 * Main work book is [DEMO.ipynb](DEMO.ipynb). This is a jupyter notebook that could be open in google colab and run directly on the cloud without the need to download it to a home machine. Users can also download to their machines and run if they have a python 3 installation, together with required packages (numpy, pandas, matplotlib, sklearn, bokeh).
 * We also provide a few example scripts. The examples are all related to DEMO.ipynb but in stand-alone python scripts that could be run on the command line.
 # Organization of data:
 The seven data files are read to a dictionary all_frames (one frame per quarter). Operations involve merging the table to get the required fields and running various aggregation functions (groupby, crosstab) to provide different data views.
 # Where to start:
 Open DEMO.ipynb <a href="https://colab.research.google.com/github/dnguyend/FAERS/blob/master/DEMO.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="DEMO.ipynb"/></a> in colab then run cell by cell.
