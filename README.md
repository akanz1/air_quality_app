# air_quality_app

New users can run the `new_user.bat/.sh` file to quickly set up the project and the environment.


## Add your project description here



## Project Organization

```
├── AUTHORS.rst             <- List of developers and maintainers
├── CHANGELOG.rst           <- Changelog to keep track of new features and fixes
├── LICENSE.txt             <- License as chosen on the command-line
├── README.md               <- The top-level README for developers
├── configs                 <- Directory for configurations of model & application
├── data
│   ├── export              <- Exported files, e.g. results
│   ├── external            <- Data from third party sources
│   ├── processed           <- The final, preprocessed data sets for modeling
│   └── raw                 <- The original, immutable data dump
├── docs                    <- Directory for Sphinx documentation in rst or md
├── environment.yml         <- The conda environment file for reproducibility
├── models                  <- Trained and serialized models, model predictions, or model summaries
├── notebooks               <- Jupyter notebooks. Naming convention is "initials-version-Notebook_Title.ipynb"
│                              e.g. `xy-01a-data_loading.ipynb`
├── references              <- Data dictionaries, manuals, and all other materials
├── reports                 <- Generated analysis as HTML, PDF, LaTeX, etc.
│   ├── yyyymmdd_call       <- Create a directory for each Call with the customer
│   └── figures             <- Generated plots and figures for reports go here, pick and move the ones you 
|                              need to the respective "call" folder
├── scripts                 <- Analysis and production scripts which import the
│                              actual Python Package (i.e. from air_quality_app     import module)
├── setup.cfg               <- Declarative configuration of your project
├── setup.py                <- Use `pip install -e .` to install for development or
│                              create a distribution with `python setup.py sdist 
│                              bdist_wheel`
│── src
│   └── air_quality_app            <- Modules with the main functionality belong here
├── tests                   <- Unit tests which can be run with `py.test`
├── .coveragerc             <- Configuration for coverage reports of unit tests
├── .isort.cfg              <- Configuration for sorting imports
└── .pre-commit-config.yaml <- Configuration of pre-commit git hooks
```


# Best Practices

## Project setup

- use the anacision project [template](readme.md)

## Notebooks:

- Use the default notebook: `notebook_template.ipynb`  and naming conventions
- ***Do not put any complex code in the notebooks***. Put everything in the modules 
- Use the notebook markdown cells to explain intent and outcomes and structure the notebook
- Set up a dedicted notebook for each presentation you make, importing the required functions and datasets to generate and export figures and results.

## Coding: 

- Rembember: **Good design is easier to change than bad design**
- Use **separate python modules** for constants, utils, mapping and naming conventions, i.e. constants.py, utils.py, ...
- Use [**type hints**](https://docs.python.org/3/library/typing.html) when writing functions
- Write  **tests** for edge-cases alongside functions
  - PyTest
- Write numpy or google style [**docstrings**](https://www.datacamp.com/community/tutorials/docstrings-python). State what the class/method/function does but not how it does it

##  Data

- Save minimally processed raw data in an efficient format (i.e. parquet, arrow, hdf5, ...)
  - Parquet and arrow require pyarrow ```conda install -c conda-forge pyarrow```
  - Hdf5 requires ```conda install h5py```

## Version Control:

- Do not push into the master
- Work on **dedicated feature branches** or agree on a git workflow within your team
- Commit often (with descriptive messages)
- **Push regularly**
- Occasionally **pull changes from the master branch** into your feature branch
        - Checkout master, pull, checkout feature, pull, ```git merge master```
- **Merge your work at least once a week** into the master branch
        - Checkout feature, pull, checkout master, pull, ```git merge feature-branch```
- **Delete unused branches**
        - ```git branch -d feature-branch``` delete local branch
            - ```git push origin --delete feature-branch``` delete remote branch
            - ```git remote prune origin``` remove local branches that have been deleted in the remote (e.g. by others)

- Consider setting up precommit-hooks and basic CI to automate formatting and testing

## Folder Structure:

- **Define naming conventions** for column names, files and so on
- **Write minimal functions to apply these rules** to raw imports (examples all_lowercase, underscore instead of ":", " ", ...) --> see anacision/internal_projects/snippets/utils.py --> clean_column_names()
- **Add useful functions to the "snippets" repo** with minimal example and docstring
- **Define project architecture upfront** as far as possible with team members
    - Folder structure (update template where necessary)
    - Files, filenames, ..
    - Rules for archiving unused and outdated files
    - ...

## Environment:

- install packages using `conda` where possible
- if you need a faster drop-in replacement for `conda` use `mamba`  (`conda install mamba`)
- Create and use a **dedicated conda environment**
    - ```conda create -n myenvname python=3.8``` (add any required packages now or manually later, pip, numpy, etc.)
    - ```conda activate myenvname```
- Periodically update the `environment.yml`
    - ```conda env export > environment.yml --no-builds```
    - ```conda env update -f environment.yml``` (update current env from environment.yml w/o removing currently installed packages)
    - ```conda env update -f environment.yml --prune``` (gets you exactly the environment.yml, i.e., removes packages not defined in environment.yml)
    - When reaching milestones it is recommended to perform an export using ```conda env export > environment.lock.MS1.yml --no-builds``` where "MS1" can be replaced with a version number or similar to allow for a perfect reproducibility.

## Team:

- Communicate
