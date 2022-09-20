def identify_rows(self) -> Tuple(dict, pd.DataFrame):
    """
    Identifies rest of world (RoW) regions of the LCA database.
    
    @follow-up what is the connection from LCA to IO databases?

    Args:
        N/A

    Returns:
        dictRoW: a dictionary in which unique RoW regions are identified in terms of countries they include
        PRO_f: metadata of the LCA database processes, with a new column 'io_geography' corresponding to XXX?
    """

    return dictRoW, PRO_f


def identify_rows(self):
    """ Method to identify the various unique Rest of the World (RoW) regions of the LCA database

    Returns:
    --------
        The updated self.dictRoW in which unique RoW regions are identified in terms of countries they include

    """
    

    unique_activities_using_row = list(set(
        self.PRO_f.activityNameId[[i for i in self.PRO_f.index if self.PRO_f.io_geography[i] == 'RoW']].tolist()))
    RoW_activities = defaultdict(list)
    tupl = [i for i in zip(self.PRO_f.activityNameId.loc[[i for i in self.PRO_f.index if self.PRO_f.activityNameId[
        i] in unique_activities_using_row]],
                            self.PRO_f.io_geography.loc[[i for i in self.PRO_f.index if self.PRO_f.activityNameId[
                                i] in unique_activities_using_row]])]
    for activity, geography in tupl:
        RoW_activities[activity].append(geography)
    # remove RoW
    RoW_activities = {k: [v1 for v1 in v if v1 != 'RoW'] for k, v in RoW_activities.items()}
    # delete from RoW_activities processes which had only RoW as geography and are thus empty now
    for key in [i for i in list(RoW_activities.keys()) if RoW_activities[i] == []]:
        del RoW_activities[key]
    # put every element to the same level (elements that are lists are transformed to lists of lists)
    for values in list(RoW_activities.values()):
        for i in range(0, len(values)):
            if values[i] in self.countries_per_regions.keys():
                values[i] = self.countries_per_regions[values[i]]
    # for elements that are lists of lists stemming from the replacement of ['RER'] by [['AT','BE',...]],
    # add all of the together in a single list
    for keys in RoW_activities.keys():
        for item in RoW_activities[keys]:
            if isinstance(item, list):
                RoW_activities[keys] = sum_elements_list(RoW_activities[keys])
    # remove duplicates inside the elements
    for keys in list(RoW_activities.keys()):
        RoW_activities[keys] = list(set(RoW_activities[keys]))
    # need to sort to identify duplicates whose elements would be ordered differently and thus be treated as not
    # duplicated
    for keys in RoW_activities.keys():
        RoW_activities[keys].sort()
    # identify the combination of countries that are NOT inside the residual of each process
    dictactrow = {}
    residual_geo_IO_to_remove = ['WA', 'WE', 'WF', 'WL', 'WM']
    for keys in RoW_activities.keys():
        dictactrow[keys] = list(set(self.listcountry) - set(RoW_activities[keys]) - set(residual_geo_IO_to_remove))
    unique_RoWs = []
    for keys in dictactrow.keys():
        if dictactrow[keys] not in unique_RoWs:
            unique_RoWs.append(dictactrow[keys])
    # create name for the values of the different RoW
    listname = []
    for i in range(0, len(unique_RoWs)):
        listname.append('RoW' + '(' + str(i) + ')')
    # put all of that in dictRoW
    for i in range(0, len(unique_RoWs)):
        self.dictRoW[listname[i]] = unique_RoWs[i]
    try:
        # if RoWs are empty because processes from ecoinvent are too described
        del [[k for k in self.dictRoW.keys() if len(self.dictRoW[k]) == 0][0]]
    except IndexError:
        pass
    for keys in dictactrow:
        for keys2 in self.dictRoW:
            if dictactrow[keys] == self.dictRoW[keys2]:
                dictactrow[keys] = keys2
    RoW_matrix = pd.DataFrame(list(dictactrow.values()), index=list(dictactrow.keys()), columns=['RoW_geography'])
    self.PRO_f = self.PRO_f.merge(RoW_matrix, left_on='activityNameId', right_on=RoW_matrix.index, how='outer')
    self.PRO_f.index = self.PRO_f.activityId + '_' + self.PRO_f.productId
    self.PRO_f = self.PRO_f.reindex(self.processes_in_order)
    self.PRO_f.io_geography.update(self.PRO_f.RoW_geography[self.PRO_f.io_geography == 'RoW'])
    self.PRO_f = self.PRO_f.drop('RoW_geography', axis=1)
    # might be some RoW or empty lists left in PRO_f
    self.PRO_f.io_geography[self.PRO_f.io_geography == 'RoW'] = 'GLO'
    self.PRO_f.io_geography.loc[[i for i in self.PRO_f.index if type(self.PRO_f.io_geography[i]) == list]] = 'GLO'
