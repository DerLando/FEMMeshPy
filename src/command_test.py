from proxy import Proxy, CommandBuilder
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import rhinoscriptsyntax as rs
import rhino_proxy


def square_command():
    proxy = Proxy()

    for i in range(6):

        proxy.execute_command(CommandBuilder().house(10.0).build())
        cmd = CommandBuilder().orient(i).subdivide(1).transfer().build()
        mesh = rhino_proxy.mesh_from_buffer(proxy.execute_command(cmd))
        sc.doc.Objects.AddMesh(mesh)

        print("Added house {}".format(i + 1))

    # cmd = CommandBuilder().polygon(radius=10.0, n_sides=7).subdivide(2).build()
    # proxy.execute_command(cmd)
    # result = proxy.receive()
    # mesh = rhino_proxy.mesh_from_buffer(result)
    # sc.doc.Objects.AddMesh(mesh)

    sc.doc.Views.Redraw()
    proxy.close()


if __name__ == "__main__":
    square_command()
