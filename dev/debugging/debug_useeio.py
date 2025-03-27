# %%
import bw2io as bi
import bw2data as bd
import bw2calc as bc

# /Users/michaelweinold/data/US_Environmental_Protection_Agency-USEEIO_v2.zip
# bi.useeio20()

bd.projects.set_current(name='USEEIO-1.1')
db = bd.Database('USEEIO-1.1')

node = bd.get_node(id=570)

lca = bc.LCA( 
    demand={node: 100}, 
    method = ('Impact Potential', 'GCC')
)
lca.lci()
lca.lcia()