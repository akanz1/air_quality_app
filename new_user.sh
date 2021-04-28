echo ====================================================
echo Data Science Project Template - anacision GmbH, 2021
echo ====================================================

export CONDA_ALWAYS_YES="true"

echo setup environment air_quality_app
conda env create --file environment.yml
eval "$(conda shell.bash hook)"
conda activate air_quality_app
echo install package air_quality_app
pip install -e .
echo install jupyter kernel air_quality_app
python -m ipykernel install --user --name air_quality_app --display-name "conda:air_quality_app"
unset CONDA_ALWAYS_YES