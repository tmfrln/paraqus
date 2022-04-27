# Paraqus

Paraqus is a python package developed to export simulation results to the .vtk-format. 

Currently, paraqus is still under development and not yet ready to use.

## Installation

Paraqus can be installed from the python package index.

```bash
pip install paraqus
```

When the package is used in the software Abaqus, add it to the system path.
```python
import sys
sys.path.append('DIR-TO-PARAQUS-PACKAGE')
```

Afterwards, the package can be imported in Abaqus. The dependecies should be already installed in recent Abaqus versions.


## License

Paraqus is released under the [GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/) license.
