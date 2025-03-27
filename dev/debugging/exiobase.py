# %%
import bw2io as bi
ex = bi.importers.Exiobase3MonetaryImporter("/Users/michaelweinold/data/IOT_2020_ixi.zip", "exio_test_1")
ex.apply_strategies()
ex.write_database()