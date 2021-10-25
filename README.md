# S7 Programming and Simulation FEM-ready mesh implementation

For the Semester Programm *Programming and Simulation* we are developing a *FEM-ready* mesh class to run some simple simulations.

## Design thoughts

A mesh face should be subdividable, with custom *-maybe multiple different-* subdivision algorithms. This could allow for design iterations and design evaluations.
For *FEM*, we need to be able to efficiently query node-edge-face connections and also find neighbours for all nodes / edges / faces.
The mesh should support *CRUD* operations on Nodes, Edges and Faces

## Implemented

Keeping track of what is already implemented, and what is still left do be desired

### Buffers

Buffers are collections of mesh elements that need to be kept in sync.

 - [x] `OneToManyConnectionTable` -> Convenience one-to-many mapping
 - [x] `NodeBuffer` -> Collection of nodes in space
   - [x] `self.add_vertex()`
   - [x] `self.remove_vertex()`
   - [x] `self.remove_node()`
   - [x] re-write vertex->node dict, to use indices as keys, so we don't have key overlap.

### Kernel

The `Kernel` stores all buffers and allows for operations that have to touch multiple buffers, like adding a new face from it's vertices.

The methods we need to implement on `Kernel` are as follows:

 - [x] `self.add_new_face()` -> Add a new face from it's corner vertices
 - [ ] `self.remove_face()` -> Remove a given face
 - [x] `self.face_center()` -> Calculates the center for a given face
 - [ ] `self.subdivide_face_constant_quads()` -> A subdivision strategy that recursively subdivides a face into quads, by splitting it's edges

### Mesh

The `Mesh` wraps the `Kernel` producing a safe interface to it, so no topology can be broken.