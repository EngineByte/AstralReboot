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
    vox: npt.NDArray[np.uint8], size: int, solid_threshold: int = 1, method='default'
) -> tuple[FloatArray, IndexArray]:
    
    size = int(size)
    if vox.ndim != 1 or vox.shape[0] != size**3:
        raise ValueError('vox must be 1D of length size^3')

    def idx(x: int, y: int, z: int) -> int:
        return x + size * (y + size * z)

    def solid(x: int, y: int, z: int) -> bool:
        if x < 0 or y < 0 or z < 0 or x >= size or y >= size or z >= size:
            return False
        return int(vox[idx(x,y,z)]) >= solid_threshold

    def default_mesher(vcount, size):
        verts = []
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
        
        return verts


    def cube_mesh_at(x: int, y: int, z: int) -> list[list[float]]:
        verts = np.ndarray((0, 8), dtype=np.float32)
        _cpos = [
            [1.0, 1.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            
            [0.0, 1.0, 1.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 1.0, 1.0],
            
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
            
            [1.0, 1.0, 1.0],
            [1.0, 0.0, 1.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 1.0],
            
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 0.0]
        ]
        _cnorm = [
            [0.0, 0.0, -1.0],
            [0.0, 0.0, 1.0],
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0]
        ]
        _cuv = [
            [0.0, 1.0],
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0]
        ]
        
        for c in range(24):
            f = c // 4
            m = c % 4
            
            vpos = np.array(_cpos[c], dtype=np.float32) + np.array([x, y, z], dtype=np.float32)
                
            vnorm = np.array(_cnorm[f], dtype=np.float32)
            vuv = np.array(_cuv[m], dtype=np.float32)
            
            v = np.hstack((vpos, vnorm, vuv), dtype=np.float32)
            verts = np.vstack((verts, v))
        
        return verts

        
                    
        

    def naive_mesher(size):
        verts = np.ndarray((0, 8), dtype=np.float32)
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    if solid(x, y, z):
                        vert = cube_mesh_at(x, y, z)
                        verts = np.vstack((verts, vert))
                        
        return verts

    if method == 'default':
        verts = default_mesher(size)
    elif method == 'naive':
        verts = naive_mesher(size)
        
    inds = np.array([], dtype=np.uint32)
    face_count = verts.shape[0] // 4
    elem = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
    for f in range(face_count):
        inds = np.hstack((inds, elem + 4 * f))
    
    return verts, inds