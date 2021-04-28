@ECHO OFF
ECHO ====================================================
ECHO Data Science Project Template - anacision GmbH, 2021
ECHO ====================================================

ECHO.
ECHO Setting up environment: air_quality_app
ECHO.
CALL conda env create --file environment.yml
ECHO.
ECHO Installing packages and dependencies into conda environment: air_quality_app
ECHO.
ECHO Activating Environment
CALL conda activate air_quality_app

ECHO Installing air_quality_app locally:
call python -m pip install -e .
ECHO.
ECHO Installing Jupyter-Kernel
CALL python -m ipykernel install --user --name air_quality_app --display-name "conda:air_quality_app"
CALL conda activate air_quality_app
