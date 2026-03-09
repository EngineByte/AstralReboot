from __future__ import annotations

from dataclasses import dataclass
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

    def naive_mesher(size: int) -> np.ndarray[np.float32]:
        verts = np.ndarray((0, 8), dtype=np.float32)
        for x in range(size):
            for y in range(size):
                for z in range(size):
                    if solid(x, y, z):
                        vert = cube_mesh_at(x, y, z)
                        verts = np.vstack((verts, vert))
                        
        return verts
    
    @dataclass
    class Quad:
        m0: int
        n0: int
        m1: int
        n1: int


    def greedy_mesher(size: int) -> np.ndarray[np.float32]:
        def get_slicemap(dir: str, slc):
            slicemap = np.empty((size, size), dtype=np.uint8)
            
            for m in range(size):
                for n in range(size):
                    if dir == 'xy':
                        x = m
                        y = n
                        z = slc
                        slicemap[m, n] = vox[idx(x, y, z)]
                    elif dir == 'zy':
                        z = m
                        y = n
                        x = slc
                        slicemap[m, n] = vox[idx(x, y, z)]
                    elif dir == 'xz':
                        x = n
                        z = m
                        y = slc
                        slicemap[n, m] = vox[idx(x, y, z)]
            
            return slicemap
        

        
        def slicemap_mesh(dir, slc, mp, rev=False):

            
            slicemap = mp.copy()

            directionals = {
                ('xy', False): (
                    np.array([0.0, 0.0, -1.0], dtype=np.float32),
                    np.array([
                        [1.0, 1.0, 0.0, 1.0],
                        [1.0, 0.0, 0.0, 1.0],
                        [0.0, 0.0, 0.0, 1.0],
                        [0.0, 1.0, 0.0, 1.0]    
                    ], dtype=np.float32)
                ),
                ('xy', True): (
                    np.array([0.0, 0.0, 1.0], dtype=np.float32),
                    np.array([
                        [0.0, 1.0, 0.0, 1.0],
                        [0.0, 0.0, 0.0, 1.0],
                        [1.0, 0.0, 0.0, 1.0],
                        [1.0, 1.0, 0.0, 1.0]    
                    ], dtype=np.float32)
                ),
                ('zy', False): (
                    np.array([-1.0, 0.0, 0.0], dtype=np.float32),
                    np.array([
                        [0.0, 1.0, 0.0, 1.0],
                        [0.0, 0.0, 0.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0],
                        [0.0, 1.0, 1.0, 1.0]    
                    ], dtype=np.float32)
                ),
                ('zy', True): (
                    np.array([1.0, 0.0, 0.0], dtype=np.float32),
                    np.array([
                        [0.0, 1.0, 1.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0],
                        [0.0, 0.0, 0.0, 1.0],
                        [0.0, 1.0, 0.0, 1.0]    
                    ], dtype=np.float32)
                ),
                ('xz', False): (
                    np.array([0.0, -1.0, 0.0], dtype=np.float32),
                    np.array([
                        [0.0, 0.0, 1.0, 1.0],
                        [0.0, 0.0, 0.0, 1.0],
                        [1.0, 0.0, 0.0, 1.0],
                        [1.0, 0.0, 1.0, 1.0]    
                    ], dtype=np.float32)
                ),
                ('xz', True): (
                    np.array([0.0, 1.0, 0.0], dtype=np.float32),
                    np.array([
                        [0.0, 0.0, 0.0, 1.0],
                        [0.0, 0.0, 1.0, 1.0],
                        [1.0, 0.0, 1.0, 1.0],
                        [1.0, 0.0, 0.0, 1.0]    
                    ], dtype=np.float32)
                )
            }
            
            vn_, vpos_ = directionals[(dir, rev)]

            def clear_slicemap(quad: Quad):
                for m_ in range(quad.m0, quad.m1+1):
                    for n_ in range(quad.n0, quad.n1+1):
                        slicemap[m_, n_] = 0
            
            def mesh_quad(quad: Quad):
                mm = quad.n0
                nn = quad.m0
                sm = quad.n1 - quad.n0 + 1
                sn = quad.m1 - quad.m0 + 1
                
                
                S = np.identity(4, dtype=np.float32)
                T = np.identity(4, dtype=np.float32)
                if dir == 'xy':
                    S[0, 0], S[1, 1] = sn, sm
                    T[:3, 3] = (nn, mm, slc)
                elif dir == 'zy':
                    S[2, 2], S[1, 1] = sn, sm
                    T[:3, 3] = (slc, mm, nn)
                elif dir == 'xz':
                    S[0, 0], S[2, 2] = sn, sm
                    T[:3, 3] = (nn, slc, mm)
                
                vpos = (T @ S @ vpos_.T).T[:,:3]
                uv = np.array([
                    [0.0, 1.0],
                    [0.0, 0.0],
                    [1.0, 0.0],
                    [1.0, 1.0]    
                ], dtype=np.float32)
                vnorm = np.vstack((vn_ , vn_, vn_, vn_))
                quad_mesh = np.hstack((vpos, vnorm, uv))
                
                return quad_mesh
            
            def quad_pop(txtr, m0, n0):
                m1 = -1
                n1 = -1
                
                def find_n1():
                    for n in range(n0+1, size):
                        t_range = slicemap[m0:m1+1,n]
                        if all([t == txtr for t in t_range]):
                            if n == size - 1:
                                n1 = n
                                break
                            continue
                        
                        n1 = n - 1
                        break
                    return n1
                
                if m0 == size - 1:
                    m1 = m0
                else:
                    for m in range(m0+1, size):
                        t = slicemap[m, n0]
                        
                        if t == txtr:
                            if m == size - 1:
                                m1 = m
                                break
                            continue
                        
                        m1 = m - 1
                        break
                    
                if n0 == size - 1:
                    n1 = n0
                else:
                    n1 = find_n1()       
                    
                return Quad(m0, n0, m1, n1)
             
            slice_mesh = np.ndarray((0, 8), dtype=np.float32)
            for m in range(size):
                for n in range(size):
                    txtr = slicemap[m, n]
                    if txtr > 0:
                        quad: Quad = quad_pop(txtr, m, n)
                        
                        clear_slicemap(quad)
                        
                        quad_mesh = mesh_quad(quad)
                        slice_mesh = np.vstack((slice_mesh, quad_mesh))
                        
            return slice_mesh
                        
            
        
        def get_greedy_slices(dir: str):
            mesh = np.ndarray((0, 8), dtype=np.float32)
            for slc in range(size+1):
                if slc > 0 and slc < size:
                    slcmap0 = get_slicemap(dir, slc-1)
                    slcmap1 = get_slicemap(dir, slc)
                elif slc == 0:
                    slcmap1 = get_slicemap(dir, slc)
                    slcmap0 = np.zeros((slcmap1.shape), dtype=np.uint8)
                elif slc == size:
                    slcmap0 = get_slicemap(dir, slc-1)
                    slcmap1 = np.zeros((slcmap0.shape), dtype=np.uint8)
                
                def mask_slicemaps(map0, map1):
                    for m in range(size):
                        for n in range(size):
                            if map0[m, n] > 0 and map1[m, n] > 0:
                                map0[m, n] = 0
                                map1[m, n] = 0
                    
                    return map0, map1
                
                slcmap0, slcmap1 = mask_slicemaps(slcmap0, slcmap1)
                           
                slicemesh0 = slicemap_mesh(dir, slc, slcmap0, True)
                slicemesh1 = slicemap_mesh(dir, slc, slcmap1)
                
                mesh = np.vstack((mesh, slicemesh0, slicemesh1))
            
            return mesh
        
        vertsxy = get_greedy_slices('xy')
        vertszy = get_greedy_slices('zy')
        vertsxz = get_greedy_slices('xz')
        
        verts = np.vstack((vertsxy, vertszy, vertsxz), dtype=np.float32)
        
        return verts
        
    if method == 'default':
        verts = default_mesher(size)
    elif method == 'naive':
        verts = naive_mesher(size)
    elif method == 'greedy':
        verts = greedy_mesher(size)
        
    inds = np.array([], dtype=np.uint32)
    face_count = verts.shape[0] // 4
    elem = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
    for f in range(face_count):
        inds = np.hstack((inds, elem + 4 * f))
    
    return verts, inds