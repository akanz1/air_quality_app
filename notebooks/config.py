import sys
from pathlib import Path


base_dir = Path.cwd().parent

module_path = Path.joinpath(base_dir, "src")
if not Path(module_path).is_dir():
    sys.path.append(module_path)

# Folders
## Data
data_dir = Path.joinpath(base_dir, "data/raw")

## Exports
export_dir = Path.joinpath(base_dir, "data/export")

## Figures
figures_dir = Path.joinpath(base_dir, "reports/figures")


# Plotting
import matplotlib as mpl
import seaborn as sns

sns.set_context("talk")
sns.set(rc={"figure.figsize": (16, 10)})
sns.set_style("whitegrid")


# Data Wrangling
import numpy as np
import pandas as pd

pd.set_option("display.max_rows", 120)
pd.set_option("display.max_columns", 120)


print("Python: {}\n".format(sys.version))
print("The following packages have been imported:\n")
print("sys, pathlib.Path")
print("matplotlib as mpl: {}".format(mpl.__version__))
print("numpy as np: {}".format(np.__version__))
print("pandas as pd: {}".format(pd.__version__))
print("seaborn as sns: {}".format(sns.__version__))

print("\nThe following directories have been imported:")
print(f" data_dir -> {data_dir}")
print(f" export_dir -> {export_dir}")
print(f" figures_dir -> {figures_dir}")
