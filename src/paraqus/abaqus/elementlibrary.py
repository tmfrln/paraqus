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
Abaqus element library for paraqus.

The module constant `ABQ_ELEMENT_LIBRARY` maps the abaqus element names to
integer vtk element types.

"""

# Identifiers:
# 3: First-order line
# 4: Second-order line
# 5: First-order tri
# 9: First-order quad
# 10: First-order tet
# 12: First-order hex
# 13: First-order prism
# 14: First-order pyramid
# 22: Second-order tri
# 23: Second-order quad
# 24: Second-order tet
# 25: Second-order hex
# 26: Second-order prism
# 28: Bi-quadratic quad

# We copied all the elements from the abaqus element library here. Note that
# not all elements are actually tested.

ABQ_ELEMENT_LIBRARY = {

# =============================================================================
#
#
#                   CONTINUUM ELEMENTS
#
#
# =============================================================================


#%% 1d solid elements
# -----------------------------------------------------------------------------

    # Diffusive heat transfer elements
    "DC1D2": 3,
    "DC1D3": 4,

    # Forced convection heat transfer elements
    "DCC1D2": 3,
    "DCC1D2D": 3,

    # Coupled thermal-electrical elements
    "DC1D2E": 3,
    "DC1D3E": 3,

    # Acoustic elements
    "AC1D2": 3,
    "AC1D3": 3,


#%% 2d solid elements
# -----------------------------------------------------------------------------

    # Plane strain elements
    "CPE3": 5,
    "CPE3H": 5,
    "CPE4": 9,
    "CPE4H": 9,
    "CPE4I": 9,
    "CPE4IH": 9,
    "CPE4R": 9,
    "CPE4RH": 9,
    "CPE6": 22,
    "CPE6H": 22,
    "CPE6M": 22,
    "CPE6MH": 22,
    "CPE8": 23,
    "CPE8H": 23,
    "CPE8R": 23,
    "CPE8RH": 23,

    # Plane stress elements
    "CPS3": 5,
    "CPS4": 9,
    "CPS4I": 9,
    "CPS4R": 9,
    "CPS6": 22,
    "CPS6M": 22,
    "CPS8": 23,
    "CPS8R": 23,

    # Generalized plane strain elements
    "CPEG3": 5,
    "CPEG3H": 5,
    "CPEG4": 9,
    "CPEG4H": 9,
    "CPEG4I": 9,
    "CPEG4IH": 9,
    "CPEG4R": 9,
    "CPEG4RH": 9,
    "CPEG6": 22,
    "CPEG6H": 22,
    "CPEG6M": 22,
    "CPEG6MH": 22,
    "CPEG8": 23,
    "CPEG8H": 23,
    "CPEG8R": 23,
    "CPEG8RH": 23,

    # Coupled temperature-displacement plane strain elements
    "CPE3T": 5,
    "CPE4T": 9,
    "CPE4HT": 9,
    "CPE4RT": 9,
    "CPE4RHT": 9,
    "CPE6MT": 22,
    "CPE6MHT": 22,
    "CPE8T": 23,
    "CPE8HT": 23,
    "CPE8RT": 23,
    "CPE8RHT": 23,

    # Coupled temperature-displacement plane stress elements
    "CPS3T": 5,
    "CPS4T": 9,
    "CPS4RT": 9,
    "CPS6MT": 22,
    "CPS8T": 23,
    "CPS8RT": 23,

    # Coupled temperature-displacement generalized plane strain elements
    "CPEG3T": 5,
    "CPEG3HT": 5,
    "CPEG4T": 9,
    "CPEG4HT": 9,
    "CPEG4RT": 9,
    "CPEG4RHT": 9,
    "CPEG6MT": 22,
    "CPEG6MHT": 22,
    "CPEG8T": 23,
    "CPEG8HT": 23,
    "CPEG8RHT": 23,

    # Diffusive heat transfer or mass diffusion elements
    "DC2D3": 5,
    "DC2D4": 9,
    "DC2D6": 22,
    "DC2D8": 23,

    # Forced convection/diffusion elements
    "DCC2D4": 5,
    "DCC2D4D": 5,

    # Coupled thermal-electrical elements
    "DC2D3E": 5,
    "DC2D4E": 9,
    "DC2D6E": 22,
    "DC2D8E": 23,

    # Pore pressure plane strain elements
    "CPE4P": 9,
    "CPE4PH": 9,
    "CPE4RP": 9,
    "CPE4RPH": 9,
    "CPE6MP": 22,
    "CPE6MPH": 22,
    "CPE8P": 23,
    "CPE8PH": 23,
    "CPE8RP": 23,
    "CPE8RPH": 23,

    # Coupled temperature–pore pressure plane strain elements
    "CPE4PT": 9,
    "CPE4PHT": 9,
    "CPE4RPT": 9,
    "CPE4RPHT": 9,

    # Acoustic elements
    "AC2D3": 5,
    "AC2D4": 9,
    "AC2D4R": 9,
    "AC2D6": 22,
    "AC2D8": 23,

    # Piezoelectric plane strain elements
    "CPE3E": 5,
    "CPE4E": 9,
    "CPE6E": 22,
    "CPE8E": 23,
    "CPE8RE": 23,

    # Piezoelectric plane stress elements
    "CPS3E": 5,
    "CPS4E": 9,
    "CPS6E": 22,
    "CPS8E": 23,
    "CPS8RE": 23,

    # Electromagnetic elements
    "EMC2D3": 5,
    "EMC2D4": 9,


#%% 3d solid elements
# -----------------------------------------------------------------------------

    # Stress/displacement elements
    "C3D4": 10,
    "C3D4H": 10,
    "C3D5": 14,
    "C3D5H": 14,
    "C3D6": 13,
    "C3D6H": 13,
    "C3D8": 12,
    "C3D8H": 12,
    "C3D8I": 12,
    "C3D8IH": 12,
    "C3D8R": 12,
    "C3D8RH": 12,
    "C3D8S": 12,
    "C3D8HS": 12,
    "C3D10": 24,
    "C3D10H": 24,
    "C3D10HS": 24,
    "C3D10M": 24,
    "C3D10MH": 24,
    "C3D15": 26,
    "C3D15H": 26,
    "C3D20": 25,
    "C3D20H": 25,
    "C3D20R": 25,
    "C3D20RH": 25,
    "CSS8": 12,

    # Coupled temperature-displacement elements
    "C3D4T": 10,
    "C3D6T": 13,
    "C3D6HT": 13,
    "C3D8T": 12,
    "C3D8HT": 12,
    "C3D8RT": 12,
    "C3D8RHT": 12,
    "C3D10T": 24,
    "C3D10HT": 24,
    "C3D10MT": 24,
    "C3D10MHT": 24,
    "C3D20T": 25,
    "C3D20HT": 25,
    "C3D20RT": 25,
    "C3D20RHT": 25,

    # Coupled thermal-electrical-structural elements
    "Q3D4": 10,
    "Q3D6": 13,
    "Q3D8": 12,
    "Q3D8H": 12,
    "Q3D8R": 12,
    "Q3D8RH": 12,
    "Q3D10M": 24,
    "Q3D10MH": 24,
    "Q3D20": 25,
    "Q3D20H": 25,
    "Q3D20R": 25,
    "Q3D20RH": 25,

    # Diffusive heat transfer or mass diffusion elements
    "DC3D4": 10,
    "DC3D5": 14,
    "DC3D6": 13,
    "DC3D8": 12,
    "DC3D8R": 12,
    "DC3D10": 24,
    "DC3D15": 26,
    "DC3D20": 25,

    # Forced convection/diffusion elements
    "DCC3D8": 12,
    "DCC3D8D": 12,

    # Coupled thermal-electrical elements
    "DC3D4E": 10,
    "DC3D6E": 13,
    "DC3D8E": 12,
    "DC3D10E": 24,
    "DC3D15E": 26,
    "DC3D20E": 25,

    # Pore pressure elements
    "C3D4P": 10,
    "C3D4PH": 10,
    "C3D6P": 13,
    "C3D6PH": 13,
    "C3D8P": 12,
    "C3D8PH": 12,
    "C3D8RP": 12,
    "C3D8RPH": 12,
    "C3D10P": 24,
    "C3D10PH": 24,
    "C3D10MP": 24,
    "C3D10MPH": 24,
    "C3D20P": 25,
    "C3D20PH": 25,
    "C3D20RP": 25,
    "C3D20RPH": 25,

    # Coupled temperature–pore pressure elements
    "C3D4PT": 10,
    "C3D4PHT": 10,
    "C3D6PT": 13,
    "C3D8PT": 12,
    "C3D8PHT": 12,
    "C3D8RPT": 12,
    "C3D8RPHT": 12,
    "C3D10MPT": 24,
    "C3D10PT": 24,
    "C3D10PHT": 24,

    # Acoustic elements
    "AC3D4": 10,
    "AC3D5": 14,
    "AC3D6": 13,
    "AC3D8": 12,
    "AC3D8R": 12,
    "AC3D10": 24,
    "AC3D15": 26,
    "AC3D20": 25,

    # Poroelastic acoustic elements
    "C3D4A": 10,
    "C3D6A": 13,
    "C3D8A": 12,

    # Piezoelectric elements
    "C3D4E": 10,
    "C3D6E": 13,
    "C3D8E": 12,
    "C3D10E": 24,
    "C3D15E": 26,
    "C3D20E": 25,
    "C3D20RE": 25,

    # Electromagnetic elements
    "EMC3D4": 10,
    "EMC3D6": 13,
    "EMC3D8": 12,

    # Coupled Eulerian Lagrangian elements - mechanical only
    "EC3D8R": 12,

    # Coupled Eulerian Lagrangian elements - thermomechanical
    "EC3D8RT": 12,

#%% Axisymmetric solid elements

    # Stress/displacement elements without twist
    "CAX3": 5,
    "CAX3H": 5,
    "CAX4": 9,
    "CAX4H": 9,
    "CAX4I": 9,
    "CAX4IH": 9,
    "CAX4R": 9,
    "CAX4RH": 9,
    "CAX6": 22,
    "CAX6H": 22,
    "CAX6M": 22,
    "CAX6MH": 22,
    "CAX8": 23,
    "CAX8H": 23,
    "CAX8R": 23,
    "CAX8RH": 23,

    # Stress/displacement elements with twist
    "CGAX3": 5,
    "CGAX3H": 5,
    "CGAX4": 9,
    "CGAX4H": 9,
    "CGAX4R": 9,
    "CGAX4RH": 9,
    "CGAX6": 22,
    "CGAX6H": 22,
    "CGAX6M": 22,
    "CGAX6MH": 22,
    "CGAX8": 23,
    "CGAX8H": 23,
    "CGAX8R": 23,
    "CGAX8RH": 23,

    # Diffusive heat transfer or mass diffusion elements
    "DCAX3": 5,
    "DCAX4": 9,
    "DCAX6": 22,
    "DCAX8": 23,

    # Forced convection/diffusion elements
    "DCCAX2": 3,
    "DCCAX2D": 3,
    "DCCAX4": 9,
    "DCCAX4D": 9,

    # Coupled thermal-electrical elements
    "DCAX3E": 5,
    "DCAX4E": 9,
    "DCAX6E": 22,
    "DCAX8E": 23,

    # Coupled temperature-displacement elements without twist
    "CAX3T": 5,
    "CAX4T": 9,
    "CAX4HT": 9,
    "CAX4RT": 9,
    "CAX4RHT": 9,
    "CAX6MT": 22,
    "CAX6MHT": 22,
    "CAX8T": 23,
    "CAX8HT": 23,
    "CAX8RT": 23,
    "CAX8RHT": 23,

    # Coupled temperature-displacement elements with twist
    "CGAX3T": 5,
    "CGAX3HT": 5,
    "CGAX4T": 9,
    "CGAX4HT": 9,
    "CGAX4RT": 9,
    "CGAX4RHT": 9,
    "CGAX6MT": 22,
    "CGAX6MHT": 22,
    "CGAX8T": 23,
    "CGAX8HT": 23,
    "CGAX8RT": 23,
    "CGAX8RHT": 23,

    # Pore pressure elements
    "CAX4P": 9,
    "CAX4PH": 9,
    "CAX4RP": 9,
    "CAX4RPH": 9,
    "CAX6MP": 22,
    "CAX6MPH": 22,
    "CAX8P": 23,
    "CAX8PH": 23,
    "CAX8RP": 23,
    "CAX8RPH": 23,

    # Coupled temperature–pore pressure elements
    "CAX4PT": 9,
    "CAX4RPT": 9,
    "CAX4RPHT": 9,

    # Acoustic elements
    "ACAX3": 5,
    "ACAX4R": 9,
    "ACAX4": 9,
    "ACAX6": 22,
    "ACAX8": 23,

    # Piezoelectric elements
    "CAX3E": 5,
    "CAX4E": 9,
    "CAX6E": 22,
    "CAX8E": 23,
    "CAX8RE": 23,


# =============================================================================
#
#
#                   STRUCTURAL ELEMENTS
#
#
# =============================================================================


#%% Truss elements
# -----------------------------------------------------------------------------

    # 2D stress/displacement truss elements
    "T2D2": 3,
    "T2D2H": 3,
    "T2D3": 4,
    "T2D3H": 4,

    # 3D stress/displacement truss elements
    "T3D2": 3,
    "T3D2H": 3,
    "T3D3": 4,
    "T3D3H": 4,

    # 2D coupled temperature-displacement truss elements
    "T2D2T": 3,
    "T2D3T": 4,

    # 3D coupled temperature-displacement truss elements
    "T3D2T": 3,
    "T3D3T": 4,

    # 2D piezoelectric truss elements
    "T2D2E": 3,
    "T2D3E": 4,

    # 3D piezoelectric truss elements
    "T3D2E": 3,
    "T3D3E": 4,


#%% Beam elements
# -----------------------------------------------------------------------------

    # Beams in a plane
    "B21": 3,
    "B21H": 3,
    "B22": 4,
    "B22H": 4,
    "B23": 3,
    "B23H": 3,
    "PIPE21": 3,
    "PIPE21H": 3,
    "PIPE22": 4,
    "PIPE22H": 4,

    # Beams in space
    "B31": 3,
    "B31H": 3,
    "B32": 4,
    "B32H": 4,
    "B33": 3,
    "B33H": 3,
    "PIPE31": 3,
    "PIPE31H": 3,
    "PIPE32": 4,
    "PIPE32H": 4,

    # Open-section beams in space
    "B31OS": 3,
    "B31OSH": 3,
    "B32OS": 4,
    "B32OSH": 4,


#%% Frame elements
# -----------------------------------------------------------------------------

    # Frame in a plane
    "FRAME2D": 3,

    # Frame in space
    "FRAME3D": 4,


#%% Elbow elements
# -----------------------------------------------------------------------------

    "ELBOW31": 3,
    "ELBOW32": 4,
    "ELBOW31B": 3,
    "ELBOW31C": 3,


#%% Shear panel elements
# -----------------------------------------------------------------------------

    "SHEAR4": 12,


#%% 3d conventional shell elements
# -----------------------------------------------------------------------------

    # Stress/displacement elements
    "STRI3": 5,
    "S3": 5,
    "S3R": 5,
    "S3RS": 5,
    "STRI65": 22,
    "S4": 9,
    "S4R": 9,
    "S4RS": 9,
    "S4RSW": 9,
    "S4R5": 9,
    "S8R": 23,
    "S8R5": 23,
    "S9R5": 28,

    # Heat transfer elements
    "DS3": 5,
    "DS4": 9,
    "DS6": 22,
    "DS8": 23,

    # Coupled temperature-displacement elements
    "S3T": 5,
    "S3RT": 5,
    "S4T": 9,
    "S4RT": 9,
    "S8RT": 23,


#%% Continuum shell elements
# -----------------------------------------------------------------------------

    # Stress/displacement elements
    "SC6R": 13,
    "SC8R": 12,

    # Coupled temperature-displacement elements
    "SC6RT": 13,
    "SC8RT": 12,


#%% Axisymmetric shell elements
# -----------------------------------------------------------------------------

    # Stress/displacement elements
    "SAX1": 3,
    "SAX2": 4,

    # Heat transfer elements
    "DSAX1": 3,
    "DSAX2": 4,


# =============================================================================
#
#
#                   Inertial, rigid, capacitance elements
#
#
# =============================================================================


#%% Rigid elements
# -----------------------------------------------------------------------------

    # 2D rigid elements
    "R2D2": 3,
    "RAX2": 3,
    "RB2D2": 3,

    # 3D rigid elements
    "R3D3": 5,
    "R3D4": 9,
    "RB3D2": 3,

}
