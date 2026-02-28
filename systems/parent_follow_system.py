from ecs.world import ECSWorld
from components.parent_follow import ParentFollow
from components.transform import Transform
from ecs.query import Query
from components.tags import DirtyMatrices

def system_parent_follow(world: 'ECSWorld', dt: float):
    follow = world.store(ParentFollow)
    tr = world.store(Transform)
    
    for eid, i_tr, i_f in Query(world, (Transform, ParentFollow)):
        p_eid = int(follow.parent[i_f])
        
        if p_eid <= 0:
            continue
        
        if not world.has(p_eid, Transform):
            continue
        
        i_parent = tr.dense_index(p_eid)
        
        tr.pos[i_tr] = tr.pos[i_parent] + follow.offset[i_f]
        
        tr.rot[i_tr] = tr.rot[i_parent]
        
        world.tag_add(eid, DirtyMatrices)
        
        