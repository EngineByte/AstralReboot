from __future__ import annotations

import numpy as np
import numpy.typing as npt


FloatArray = npt.NDArray[np.float32]
IndexArray = npt.NDArray[np.uint32]


_FACES = [
    ((-1, 0, 0), (-1, 0, 0), [(0,0,0),(0,1,0),(0,1,1),(0,0,1)]),  
    ((+1, 0, 0), (+1, 0, 0), [(1,0,0),(1,0,1),(1,1,1),(1,1,0)]),  
    ((0,-1, 0), (0,-1, 0), [(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),    
    ((0,+1, 0), (0,+1, 0), [(0,1,0),(0,1,1),(1,1,1),(1,1,0)]),    
    ((0, 0,-1), (0, 0,-1), [(0,0,0),(0,1,0),(1,1,0),(1,0,0)]),    
    ((0, 0,+1), (0, 0,+1), [(0,0,1),(1,0,1),(1,1,1),(0,1,1)]),    
]


def build_surface_mesh_from_voxels(
    vox: npt.NDArray[np.uint8], size: int, solid_threshold: int = 1
) -> tuple[FloatArray, IndexArray]:
    
    size = int(size)
    if vox.ndim != 1 or vox.shape[0] != size**3:
        raise ValueError("vox must be 1D of length size^3")

    verts: list[list[float]] = []
    inds: list[int] = []
    vcount = 0

    def idx(x: int, y: int, z: int) -> int:
        return x + size * (y + size * z)

    def solid(x: int, y: int, z: int) -> bool:
        if x < 0 or y < 0 or z < 0 or x >= size or y >= size or z >= size:
            return False
        return int(vox[idx(x,y,z)]) >= solid_threshold

    for z in range(size):
        for y in range(size):
            for x in range(size):
                if not solid(x,y,z):
                    continue

                for (ddx,ddy,ddz), (nx,ny,nz), corners in _FACES:
                    if solid(x+ddx, y+ddy, z+ddz):
                        continue  

                    base = vcount
                    for (ox,oy,oz) in corners:
                        px = float(x + ox)
                        py = float(y + oy)
                        pz = float(z + oz)

                        u = float(ox if abs(nx)==1 else (ox if abs(nz)==1 else ox))
                        v = float(oy if abs(ny)==1 else (oy if abs(nz)==1 else oy))
                        verts.append([px,py,pz, float(nx),float(ny),float(nz), u, v])
                        vcount += 1

                    inds.extend([base+0, base+1, base+2, base+0, base+2, base+3])

    if not verts:
        return np.zeros((0,8), dtype=np.float32), np.zeros((0,), dtype=np.uint32)

    return np.asarray(verts, dtype=np.float32), np.asarray(inds, dtype=np.uint32)