from simple_proxy import CommandBuilder
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
import rhinoscriptsyntax as rs


def chunker(seq, size):
    return (seq[pos: pos + size] for pos in xrange(0, len(seq), size))


def mesh_from_buffer(buffer):
    mesh = rg.Mesh()
    for chunk in chunker(buffer[0], 3):
        mesh.Vertices.Add(chunk[0], chunk[1], chunk[2])

    for face in buffer[1]:
        if len(face) == 3:
            mesh.Faces.AddFace(face[0], face[1], face[2])
        else:
            mesh.Faces.AddFace(face[0], face[1], face[2], face[3])

    return mesh


def square_command():
    cmd = CommandBuilder().polygon(n_sides=5).subdivide(4).transfer().build()
    buffer = cmd.execute()
    if buffer is None:
        return

    mesh = mesh_from_buffer(buffer)
    sc.doc.Objects.AddMesh(mesh)
    
    sc.doc.Views.Redraw()


if __name__ == "__main__":
    square_command()
