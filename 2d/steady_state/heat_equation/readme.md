# Parameterized Square Mesh with Segmented Bottom Edge

This project generates a parameterized 2D square mesh with a segmented bottom edge using GMSH. The mesh is saved in `.xdmf` format for use in downstream applications. The boundaries are marked in gmsh and then read in FEniCS for further processing.

## Prerequisites

To run this script, you need the following dependencies:

- **Python 3.7 or later**
- **GMSH** (for geometry creation and meshing)
- **Meshio 3.2.7** (for mesh file handling and conversion)
- **FEniCS 2019.1.0** (for finite element simulations)

