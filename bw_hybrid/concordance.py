import numpy as np
import xarray as xr


def _build_concordance_matrix_attribution_XXX(
    str_location_process: str,
    list_location_sector: list,
    dict_location_correspondence: list,
) -> str:
    r"""
    _summary_

    Generates a _concordance matrix_ between the process system and the sectoral system.

    <img src="https://raw.githubusercontent.com/brightway-lca/bw_hybrid/refs/heads/main/docs/_media/geographic_concordance.svg" width="500">
    
    A geopgraphy matching dictionary of the form:

    ```
    {
        "BE": "BE",
        "CA-AB": "CA",
        "UN-OCEANIA": [
            "AU",
            "WA"
        ],
    }
    ```

    $$
        \mathbf{H} = 
        \begin{bmatrix}
        0.2 & 1 & 0   \\ 
        0.8 & 0 & 0   \\
        0   & 0 & 0.5 \\
        0   & 0 & 0.5 \\
        \end{bmatrix}
    $$

    $$
        \vec{x} = 
        \begin{bmatrix}
        200 \\
        800 \\
        300 \\
        300
        \end{bmatrix}
    $$

    loc(1)='US'
    loc(2)='US'
    loc(3)='US'

    Parameters
    ----------
    list_str_geo_process : list
        _description_
    list_str_geo_sector : list
        _description_

    Returns
    -------
    str
        _description_
    """

    if str_location_process in list_location_sector:
        return str_location_process
    elif str_location_process in dict_location_correspondence.keys():
        if type(dict_location_correspondence[str_location_process]) == str:
            return dict_location_correspondence[str_location_process]
        else:

            # if ecoinvent process location is in exiobase regions (US -> US)
            if geo in list(self.H.index.levels[0]):
                self.H.loc[(geo, sector), col] = 1
            # if it needs some mapping
            elif geo in self.concordance_geos.keys():
                # it's a country, not a region (e.g., AR -> WL)
                if type(self.concordance_geos[geo]) == str:
                    self.H.loc[(self.concordance_geos[geo], sector), col] = 1
                # it's a region (e.g., RNA -> CA + US)
                else:
                    # then we need to do some weighted averages based on production values of the x vector of exiobase
                    self.H.loc[:, col] = (self.io.x.loc(axis=0)[self.concordance_geos[geo], sector] /
                                          self.io.x.loc(axis=0)[self.concordance_geos[geo], sector].sum()).reindex(
                        self.H.index).loc[:, 'indout'].fillna(0)
            # special case for the dynamic region of ecoinvent: RoW
            else:
                covered_geos_for_product = []
                # get all processes producing the reference product (wurst is way faster than bw2.search())
                filtering = ws.get_many(self.ei_wurst, ws.equals('reference product', act.as_dict()['reference product']))
                # extract the location of these processes
                for dataset in filtering:
                    if dataset['code'] in list(self.filter['Hybridized processes'].code):
                        covered_geos_for_product.append(dataset['location'])
                # only keep unique ones
                covered_geos_for_product = set(covered_geos_for_product)
                # remove RoW and GLO from set
                covered_geos_for_product = covered_geos_for_product - {'RoW'} - {'GLO'}
                # convert potential regions in countries
                covered_countries_for_product = [self.concordance_geos[i] for i in covered_geos_for_product]
                # convert potential list of lists as lists
                covered_countries_for_product = [x for xs in covered_countries_for_product for x in xs]
                # apply the weighted average for relevant countries to H
                self.H.loc[:, col] = (self.io.x.loc(axis=0)[[i for i in self.H.index.levels[0] if
                                                        i not in covered_countries_for_product], sector] /
                                      self.io.x.loc(axis=0)[[i for i in self.H.index.levels[0] if
                                                        i not in covered_countries_for_product], sector].sum()).reindex(
                    self.H.index).loc[:, 'indout'].fillna(0)