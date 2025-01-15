import gmsh
import json
import meshio

def create_msh(length=1.0,
               width=0.5,
               num_segments=4,  # Number of segments for the bottom edge
               mesh_size=0.1,  # Characteristic length for mesh elements
               mesh_file = "mesh/square_mesh.msh"): 
    # Initialize GMSH
    gmsh.initialize()
    gmsh.model.add("Parameterized Square with Segmented Bottom Edge")

    # Create points for the bottom edge (segmented)
    bottom_points = [gmsh.model.geo.addPoint(
        i * (length / num_segments), 0, 0, mesh_size) for i in range(num_segments + 1)]

    # Create the remaining points
    p_top_right = gmsh.model.geo.addPoint(length, width, 0, mesh_size)
    p_top_left = gmsh.model.geo.addPoint(0, width, 0, mesh_size)

    # Create the bottom segmented lines
    bottom_lines = [
        gmsh.model.geo.addLine(bottom_points[i], bottom_points[i + 1])
        for i in range(num_segments)
    ]

    # Create the remaining lines
    right_line = gmsh.model.geo.addLine(bottom_points[-1], p_top_right)
    top_line = gmsh.model.geo.addLine(p_top_right, p_top_left)
    left_line = gmsh.model.geo.addLine(p_top_left, bottom_points[0])

    # Create a curve loop and plane surface
    all_lines = bottom_lines + [right_line, top_line, left_line]
    curve_loop = gmsh.model.geo.addCurveLoop(all_lines)
    surface = gmsh.model.geo.addPlaneSurface([curve_loop])

    # Synchronize and generate mesh
    gmsh.model.geo.synchronize()
    # Tag bottom edge segments for future customization
    # Create a dictionary for number tags and name tags
    tags_dict = {}
    for i, line in enumerate(bottom_lines):
        gmsh.model.addPhysicalGroup(1, [line], i + 1)
        gmsh.model.setPhysicalName(1, i + 1, f"Segment {i + 1}")
        tags_dict[i + 1] = f"Segment {i + 1}"

    # Add physical groups for right, top, and left edges
    gmsh.model.addPhysicalGroup(1, [right_line], num_segments + 1)
    gmsh.model.setPhysicalName(1, num_segments + 1, "Right Edge")
    tags_dict[num_segments + 1] = "Right Edge"

    gmsh.model.addPhysicalGroup(1, [top_line], num_segments + 2)
    gmsh.model.setPhysicalName(1, num_segments + 2, "Top Edge")
    tags_dict[num_segments + 2] = "Top Edge"

    gmsh.model.addPhysicalGroup(1, [left_line], num_segments + 3)
    gmsh.model.setPhysicalName(1, num_segments + 3, "Left Edge")
    tags_dict[num_segments + 3] = "Left Edge"

    # Write the dictionary to a JSON file
    with open("mesh/tags.json", "w") as json_file:
        json.dump(tags_dict, json_file, indent=4)

    

    # Add a physical group for the surface
    gmsh.model.addPhysicalGroup(2, [surface], 1)
    gmsh.model.setPhysicalName(2, 1, "Square Surface")

    # Synchronize and generate mesh
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)

    # Save the mesh to a file
    
    gmsh.write(mesh_file)

    # Finalize
    gmsh.finalize()


def convert_mesh_to_xdmf(mesh_file, output_mesh_file, output_line_file):
    mesh = meshio.read(mesh_file)
    points, cell, cell_data, field_data = mesh.points, mesh.cells, mesh.cell_data, mesh.field_data

    meshio.write(output_mesh_file, meshio.Mesh(
        points=points[:,:2],
        cells={"triangle": cell['triangle']},
    ))
    meshio.write(output_line_file, meshio.Mesh(
        points=points[:,:2],
        cells={"line": cell['line']},
        cell_data={"line": {"tags": cell_data['line']['gmsh:physical']}},
    ))