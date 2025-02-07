# Datalab Project - The Link Between Company Description and Funding

## Overview
A brief description of your project, its purpose, and goals.

## Table of Contents
- [Datalab Project - The Link Between Company Description and Funding](#datalab-project---the-link-between-company-description-and-funding)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [App](#app)
    - [Data Imputation](#data-imputation)
    - [App Only Installation](#app-only-installation)
  - [Data](#data)
  - [Running the App](#running-the-app)

## Installation
The project was tested on a Fedora 41 machine, and the following instructions are for a Linux environment. The project should work on other operating systems as well, but the installation process might differ.
### App
To install the required Python packages, run the following command in your terminal:
```bash
pip install -r requirements.txt
```
Make sure you are using python version **3.12.8**, we recommend using a virtual environment or a conda environment to avoid conflicts with other projects.

### Data Imputation
Data imputation was performed via spark for added scalability. The spark environment was set up based
on the https://github.com/cnoam/spark-course repository. Our version is attached in the privately provided
OneDrive link alongside the data.
After running the docker container, you can assign it as the remote Jupyter kernel in your IDE
and use it to run the data imputation notebook.

Alternatively, you can try to run the notebook on Databricks, but that would require tweaking the code
to properly read the data, which you would have to upload to the Databricks workspace.

### App Only Installation
If you want to run the app without any other code, you can install the docker image from the following commands:
```bash
sudo docker build -t datalab-app .
```
After the image is built, you can run the app with the following command:
```bash
sudo docker run --rm -p 8501:8501 datalab-app
```

## Data
As per the project requirements, the data is not publicly available. The data will be
provided in a privately shared OneDrive link. In the link each data folder
will be named in a format data-{path}, where the path is where to put the data folder in the project
(and rename it to just "data").

## Running the App
To run the app from the main directory of the repository, run the following command:
```bash
streamlit run "Description Improver"/desc-improver-app/app.py
```