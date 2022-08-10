# -*- coding: utf-8 -*-
#
#   Paraqus - A VTK exporter for FEM results.
#
#   Copyright (C) 2022, Furlan and Stollberg
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
Paraqus version constants.

"""

# TODO: this should integrate with PyPI versioning if possible...

PARAQUS_VERSION_MAJOR = 1
PARAQUS_VERSION_MINOR = 0


VTK_VERSION_MAJOR = 1
VTK_VERSION_MINOR = 0


# ----------------------------------------------------------------------
PARAQUS_VERSION_STRING = (str(PARAQUS_VERSION_MAJOR)
                          + "." + str(PARAQUS_VERSION_MINOR))

VTK_VERSION_STRING = str(VTK_VERSION_MAJOR) + "." + str(VTK_VERSION_MINOR)
