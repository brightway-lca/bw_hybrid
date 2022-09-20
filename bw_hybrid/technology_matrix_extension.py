# data science
import numpy as np
import scipy as sp
# type hints
import scipy.sparse.coo_matrix as coo_matrix


def extend_inventory(
    A: coo_matrix,
    activities_to_hybridize: list,
    activities_market: list
) -> coo_matrix:
    """
    Given an LCA technology matrix, and lists of process ids, returns a new LCA technology matrix
    in which the inputs of processes not to hybridize are added to the unit process inventories of each LCA process to hybridize.

    Scientific literature:
    Compare section 2 in the Supplementary Information of Agez et al., 2020 (https://doi.org/10.1111/jiec.12979)
    Compare section 3.2.3 in Agez et al., 2020 (https://doi.org/10.1111/jiec.12979)

    Args:
        A (scipy.sparse.coo_matrix): LCA technology matrix
        activities_to_hybridize (list): list of process ids of activities to hybridise
        activities_market (list): list of process ids of activities that are market activities

    Returns:
        coo_matrix: _description_
    """


    # matrix of non-hybridized processes
        ANT = self.A_ff.copy()
        ANT = pd.DataFrame(ANT.todense(), self.PRO_f.index, self.PRO_f.index)
    # sets all dataframe rows to zero where the process ID matches the one in list_to_hyb 
    ANT.loc[self.list_to_hyb] = 0
    ANT.fillna(0,inplace=True)

    # matrix of production processes
    Amarket = self.A_ff.copy()
    Amarket = pd.DataFrame(
        data = Amarket.todense(),
        index = self.PRO_f.index,
        columns = self.PRO_f.index
    )

    # sets all dataframe rows to zero where the process ID matches the one in listmarket 
    Amarket.loc[self.listmarket] = 0
    Amarket.fillna(0,inplace=True)

    self.A_ff_processed = Amarket.values.dot( #pd.DataFrame.values returns a Numpy representation of the DataFrame
        np.linalg.inv(
            np.eye(len(ANT.values)) - ANT.values #np.eye returns a 2-D array with ones on the diagonal and zeros elsewhere
        )
    )

    # the inversion brings a lot of noise which falsely contributes to double counting which is why it is removed
    self.A_ff_processed[self.A_ff_processed < 10 ** -16] = 0
    self.A_ff_processed = back_to_sparse(self.A_ff_processed)

    return A
