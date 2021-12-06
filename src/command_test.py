from proxy import CommandBuilder
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import rhinoscriptsyntax as rs
import rhino_proxy


def square_command():
    # cmd = CommandBuilder().polygon(n_sides=5).subdivide(4).transfer().build()
    cmd = CommandBuilder().house().subdivide(3).transfer().build()

    mesh = rhino_proxy.extract_cmd_results(cmd)
    sc.doc.Objects.AddMesh(mesh)

    sc.doc.Views.Redraw()


if __name__ == "__main__":
    square_command()
