# S7 Programming and Simulation FEM-ready mesh implementation

For the Semester Programm *Programming and Simulation* we are developing a *FEM-ready* mesh class to run some simple simulations.

## Design thoughts

A mesh face should be subdividable, with custom *-maybe multiple different-* subdivision algorithms. This could allow for design iterations and design evaluations.
For *FEM*, we need to be able to efficiently query node-edge-face connections and also find neighbours for all nodes / edges / faces.
The mesh should support *CRUD* operations on Nodes, Edges and Faces

## Implemented

Keeping track of what is already implemented, and what is still left do be desired

### Buffers

 - [x] `OneToManyConnectionTable` -> Convenience one-to-many mapping
 - [ ] `NodeBuffer` -> Collection of nodes in space
  - [x] `self.add_vertex()`
  - [ ] `self.remove_vertex()`
  - [ ] `self.remove_node()`
 - [ ] `FaceBuffer` -> Collection of faces
 - [ ] `EdgeBuffer` -> might not be needed