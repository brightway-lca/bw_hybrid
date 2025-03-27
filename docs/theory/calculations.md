# Hybrid Calculations with Brightway

??? Why does the USEEIO A-matrix have zero elements on the diagonal - and why does it have negative values sometimes?
??? When/how are the biosphere parts of the database written?
??? What is the difference between a database that contains the biosphere vs a unique biosphere database?
??? How is the characterization matrix/vector constructed? -> how is this done in pylcaio at the moment?
??? How does the `bw_graph_tools` package traverse the graph? Using the database?

### Construction of Matrices

[`bw2data.compat.prepare_lca_inputs()`](https://github.com/brightway-lca/brightway2-data/blob/551e975d8c530419ad75581f3935c5db44a27e35/bw2data/compat.py#L69) returns:

| Object          | Description                                                                                     |
|------------------|-------------------------------------------------------------------------------------------------|
| `demand`        | A dictionary with the demand for each product                                                  |
| `data_objs`     | A list of [`bw_processing.datapackage.Dataackage`](https://github.com/brightway-lca/bw_processing/blob/cfeb97a84dd84e61be330b90b508d6f09251075e/bw_processing/datapackage.py#L277) objects |
| `remapping_dicts` | A list of dictionaries with the remapping of the indices                                      |
| `method`        | A tuple with the method information                                                            |

[`lca.packages[0]`]

```
'inv_geomapping_matrix' (indices, data)
'biosphere_matrix' (indices, data)
'technosphere_matrix' (indices, data, flip)
```

[`lca.packages[1]`]

```
'impact_category' (indices, data)
```

!!! note

    `Datapackages` can be loaded with [`bw_processing.datapackage.load_datapackage()`](https://github.com/brightway-lca/bw_processing/blob/cfeb97a84dd84e61be330b90b508d6f09251075e/bw_processing/datapackage.py#L1061):

    ```python
    from bw_processing import load_datapackage
    my_dp = load_datapackage(ZipFileSystem("some-path.zip"))
    ```

    The location of the zip file in which a datapackage is stored can be obtained with:

    ```python
    my_dp.fs.zip.filename
    ```

Remapping dicts:

Dict of remapping dictionaries that link Brightway Node ids to (database, code) tuples. remapping_dicts can provide such remapping for any of activity, product, biosphere.

[`bw2calc.lca_base.load_lci_data()`](https://github.com/brightway-lca/brightway2-calc/blob/a51ac18348f22ada859e72f9d6c9a8774a4c0cb3/bw2calc/lca_base.py#L37)

Uses the `data_objs` (=`lca.packages`) to load the "technosphere_matrix" into a [`MappedMatrix`](https://github.com/brightway-lca/matrix_utils/blob/a34841f2dd1fb4839fd849eb3d6f055494741624/matrix_utils/mapped_matrix.py#L14)


`dicts.product`
`dicts.activity`

`dicts.product` determines how the demand vector is constructed!

```python
self.supply_array = self.solve_linear_system()
```

where `self.solve_linear_system()` returns:

```python
spsolve(self.technosphere_matrix, demand)
```

$$

$$

```python
self.inventory = self.biosphere_matrix @ sparse.spdiags(
    [self.supply_array], [0], count, count
)
```

## Matrix Equations

!!! note

    We use the following limits for the matrix coefficient indices:

    | Index   | Description                    |
    |---------|--------------------------------|
    | $N$     | Number of products=activities  |
    | $R$     | Number of biosphere flows      |
    | $L$     | Number of impact categories    |

### Standard Textbook

| Object                  | Symbol        | Dimension   | Source                                                                                                        |
|-------------------------|---------------|-------------|---------------------------------------------------------------------------------------------------------------|
| final demand vector     | $\mathbf{f}$  | $[N\times 1]$ | Def. 4 (P.21) in [Heijungs & Suh (2001)](https://doi.org/10.1007/978-94-015-9900-9)                         |
| technology matrix       | $\mathbf{A}$  | $[N\times N]$ | Eqn.(2.7) and Eqn.(2.40) in [Heijungs & Suh (2001)](https://doi.org/10.1007/978-94-015-9900-9)              |
| biosphere matrix        | $\mathbf{B}$  | $[R\times N]$ | Eqn.(2.7) and Theorem 2 (P.21) in [Heijungs & Suh (2001)](https://doi.org/10.1007/978-94-015-9900-9)        |
| scaling vector          | $\mathbf{s}$  | $[N\times 1]$ | Eqn.(2.12ff.) and Def. 3 (P.21) in [Heijungs & Suh (2001)](https://doi.org/10.1007/978-94-015-9900-9)       |
| inventory vector        | $\mathbf{g}$  | $[R\times 1]$ | Eqn.(2.10) and Def. 5 (P.21) in [Heijungs & Suh (2001)](https://doi.org/10.1007/978-94-015-9900-9)          |
| characterization matrix | $\mathbf{Q}$  | $[L\times R]$ | Eqn.(8.26) in [Errata of Heijungs & Suh (2001)](https://personal.vu.nl/r.heijungs/computational/The%20computational%20structure%20of%20LCA%20-%20Errata.pdf) |
| impact vector           | $\mathbf{h}$  | $[L\times 1]$ | Eqn.(8.27) in [Heijungs & Suh (2001)](https://doi.org/10.1007/978-94-015-9900-9) |

The _"solution to the inventory problem"_ is then given by (Eqn.(2.45) and Eqn.(2.47) in [Heijungs & Suh (2001)](https://doi.org/10.1007/978-94-015-9900-9)):

$$
\begin{align}
    \mathbf{s} &= \mathbf{A}^{-1} \mathbf{f} \\
    [N \times 1] &= [N \times N] [N \times 1] \notag \\
    \mathbf{g} &= \mathbf{B} \mathbf{s} \\
    [R \times 1] &= [R \times N] [N \times 1] \notag \\
    \mathbf{h} &= \mathbf{Q} \mathbf{g} \\
    [L \times 1] &= [L \times R] [R \times 1] \notag
\end{align}
$$

which can be written as:

$$
\begin{align}
    \mathbf{h} &= \mathbf{Q} \mathbf{B} \mathbf{A}^{-1} \mathbf{f} \\
    [L \times 1] &= [L \times R] [R \times N] [N \times N] [N \times 1] \notag
\end{align}
$$

### Brightway `bw2calc` Implementation

!!! warning

    Brightway implements the matrix calculations for the inventory vector $\mathbf{g}$, the characterization matrix $\mathbf{Q}$ and the impact vector $\mathbf{h}$ differently than the standard textbook! Note that these have different dimensions. They are marked with ⚠️ in the table of objects.

| Object | Textbook Equivalent | Dimension | Built by... |
|--------|----------------------|-----------|-------------|
|`lca.demand_array` | ✅ $\mathbf{f}$ | $[N\times 1]$ | [`bw2calc.lca.build_demand_array`](https://github.com/brightway-lca/brightway2-calc/blob/a51ac18348f22ada859e72f9d6c9a8774a4c0cb3/bw2calc/lca.py#L191)|
| `lca.technosphere_matrix` | ✅ $\mathbf{A}$ | $[N\times N]$ | [`bw2calc.lca_base.load_lci_data`](https://github.com/brightway-lca/brightway2-calc/blob/a51ac18348f22ada859e72f9d6c9a8774a4c0cb3/bw2calc/lca_base.py#L37) |
| `lca.biosphere_matrix` | ✅ $\mathbf{B}$ | $[R \times N]$ | [`bw2calc.lca_base.load_lci_data`](https://github.com/brightway-lca/brightway2-calc/blob/a51ac18348f22ada859e72f9d6c9a8774a4c0cb3/bw2calc/lca_base.py#L37) |
| `lca.supply_array` | ✅ $\mathbf{s}$ | $[N \times 1]$ | ... |
| `lca.inventory` | ⚠️ $\mathbf{g}$ | $[R \times N]$ | ... |
| `lca.characterization_matrix` | ⚠️ $\mathbf{Q}$ | $[R \times R]$ | ... |
| `lca.characterized_inventory` | ⚠️ $\mathbf{H}$ | $[R \times N]$ | ... |

$$
\begin{align}
    \mathbf{s} &= \mathbf{A}^{-1} \mathbf{f} \\
    [N \times 1] &= [N \times N] [N \times 1] \notag \\
    \mathbf{G} &= \mathbf{B} \cdot \text{diag} (\mathbf{s}) \\
    [R \times 1] &= [R \times N] [N \times 1] \notag
\end{align}
$$

Here, we do not have an _inventory vector_ $\mathbf{g}$, but an _inventory matrix_ $\mathbf{G}$. This is because the [`bw2calc.lca.LCA.lci_calculation`](https://github.com/brightway-lca/brightway2-calc/blob/a51ac18348f22ada859e72f9d6c9a8774a4c0cb3/bw2calc/lca.py#L287) function uses this convention:

```python
count = len(self.dicts.activity)
self.inventory = self.biosphere_matrix @ sparse.spdiags(
    data=[self.supply_array],
    diags=[0],
    m=count,
    n=count
)
```

This means that:


\begin{align}
    g_{ij} &= \sum_k b_{ik} \delta_{kj} s_{j} \\
    \mathbf{G} &=
    \begin{bmatrix}
        b_{11}s_1 & b_{12}s_2 \\
        b_{21}s_1 & b_{22}s_2 \\
    \end{bmatrix}
\end{align}

where $b_{21}s_1$ is the amount of biosphere flow 2 that is produced by activity 1 per unit of output produced. Summing the rows of $\mathbf{G}$ gives the inventory vector $\mathbf{g}$:

$$
\begin{align}
    g_{i} &= \sum_j g_{ij} \\
    \mathbf{g} &=
    \begin{bmatrix}
        g_1 \\
        g_2 \\
    \end{bmatrix}
\end{align}
$$

where $g_{i}$ is the total amount of biosphere flow $i$ produced by all activities. This is the inventory vector that is used in the impact assessment step.

Note that Brightway uses only [one impact assessment method at a time](https://github.com/brightway-lca/brightway2-calc/blob/cb4439b3c41cb8ddaf84a186385dde410806b977/bw2calc/lca.py#L47). This means that $L=1$. However, the `bd.LCA.characterization_matrix` object is loaded by the [`bw2calc.lca.LCA.load_lcia_data`](https://github.com/brightway-lca/brightway2-calc/blob/a51ac18348f22ada859e72f9d6c9a8774a4c0cb3/bw2calc/lca.py#L219) as a diagonal matrix (`diagonal=True`):

```python
self.characterization_mm = mu.MappedMatrix(
    packages=data_objs or self.packages,
    matrix="characterization_matrix",
    use_arrays=use_arrays,
    use_distributions=use_distributions,
    seed_override=self.seed_override,
    row_mapper=self.biosphere_mm.row_mapper,
    diagonal=True,
    custom_filter=fltr,
)
```

This means that instead of an _impact vector_ $\mathbf{h}$, we have an _impact matrix_ $\mathbf{H}$:

\begin{align}
\mathbf{H} &= \text{diag}(\mathbf{q}) \cdot \mathbf{G} \\
[R \times N] &= [R \times R] [R \times N]
\end{align}

where

\begin{align}
h_{ij} &= \sum_k c_{kk} g_{ik} \\
\mathbf{H} &= \begin{bmatrix}
c_1 (b_{11}s_1) & c_1 (b_{12}s_2) \\
c_2 (b_{21}s_1) & c_2 (b_{22}s_2) \\
\end{bmatrix}
\end{align}

where $c_2 (b_{21}s_1)$ is the impact of biosphere flow 2 that is produced by activity 1. \
The sum of all elements of column 1 is the amount of impact of all biosphere flows produced by activity 1.

The total impact of all biosphere flows produced by all activities which are induced by the final demand vector $\mathbf{f}$ can be calculated by summing all elements of $\mathbf{H}$. \
This is what is done in the [`bw2calc.lca.LCA.score`](https://github.com/brightway-lca/brightway2-calc/blob/a51ac18348f22ada859e72f9d6c9a8774a4c0cb3/bw2calc/lca.py#L330) function.

