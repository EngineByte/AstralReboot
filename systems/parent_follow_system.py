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
        if p_eid < 0:
            continue
        
        if not world.has_component(p_eid, Transform):
            continue
        
        i_parent = tr.dense_index(p_eid)
        
        tr.px[i_tr] = tr.px[i_parent] + follow.ox[i_f]
        tr.py[i_tr] = tr.py[i_parent] + follow.oy[i_f]
        tr.pz[i_tr] = tr.pz[i_parent] + follow.oz[i_f]
        
        tr.yaw[i_tr] = tr.yaw[i_parent]
        tr.pitch[i_tr] = tr.pitch[i_parent]
        tr.roll[i_tr] = tr.roll[i_parent]
        
        world.add_tag(eid, DirtyMatrices)
        
      