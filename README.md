# Task Manager

## Pre-requisites
Following packages are required before we proceed.
1. Brew
2. Conda

## Setup Steps
1. Clone this repo and go inside the root directory. 
2. Create conda environment: `conda create -n task_manager python=3.10`
3. Install postgres: `brew install postgresql`
4. Start postgres: `brew services start postgresql`
5. Activate the environment using `conda activate task_manager`
6. Install all the packages: `pip install -r requirements.txt`
7. Start the app: `python app.py`

