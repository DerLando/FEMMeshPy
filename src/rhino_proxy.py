import Rhino.Geometry as rg
import logging


def __chunker(seq, size):
    return (seq[pos : pos + size] for pos in xrange(0, len(seq), size))


def mesh_from_buffer(buffer):
    mesh = rg.Mesh()
    for chunk in __chunker(buffer[0], 3):
        mesh.Vertices.Add(chunk[0], chunk[1], chunk[2])

    for face in buffer[1]:
        if len(face) == 3:
            mesh.Faces.AddFace(face[0], face[1], face[2])
        else:
            mesh.Faces.AddFace(face[0], face[1], face[2], face[3])

    return mesh
