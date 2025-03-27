# %%
import bw2data as bd
import bw2calc as bc
ei = bd.Database('ecoinvent-3.10-apos')
lca = bc.LCA( 
    demand={ei.random(): 100}, 
    method = ('ecoinvent-3.10', 'CML v4.8 2016', 'climate change', 'global warming potential (GWP100)')
)
lca.lci()