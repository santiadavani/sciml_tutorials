from dolfin import *


def solve_thermal_problem(mesh_file, boundary_file, output_file, top_temp=100.0, left_temp=50.0, bottom_temp=25.0, num_segments=4):
    # Load mesh and boundary markers
    mesh = Mesh()
    with XDMFFile(mesh_file) as xdmf:
        xdmf.read(mesh)

    mvc = MeshValueCollection("size_t", mesh, mesh.topology().dim() - 1)
    with XDMFFile(boundary_file) as xdmf:
        xdmf.read(mvc, "tags")
    boundary_markers = MeshFunction("size_t", mesh, mvc)

    # Define function space
    V = FunctionSpace(mesh, "CG", 1)  # Continuous Galerkin (P1 elements)

    # Define boundary conditions

    bc_bottom = [DirichletBC(V, Constant(bottom_temp), boundary_markers, i)
                 for i in range(1, num_segments + 1)]
    bc_top = DirichletBC(V, Constant(top_temp),
                         boundary_markers, num_segments+2)  # Top edge
    bc_left = DirichletBC(V, Constant(left_temp),
                          boundary_markers, num_segments + 3)  # Left edge
    bcs = [bc_top, bc_left] + bc_bottom

    # Define the problem
    u = TrialFunction(V)
    v = TestFunction(V)
    kappa = Constant(1.0)  # Thermal conductivity

    a = kappa * dot(grad(u), grad(v)) * dx
    ds = Measure("ds", subdomain_data=boundary_markers)
    L = Constant(0.0) * v * ds(7)  # Source term 

    # Solve the problem
    u_sol = Function(V)
    solve(a == L, u_sol, bcs)

    # Save results to VTK
    with XDMFFile(output_file) as xdmf:
        xdmf.write(u_sol)

    return u_sol
