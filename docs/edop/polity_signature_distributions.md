# Polity Environmental Signatures: Distributions vs. Monolithic Values

## The Problem

Any polity contains multiple sub-basins varying considerably in their own environmental signatures. A single monolithic weighted-mean signature for a polity is much less informative than the full set of basin signatures it contains. This makes global comparative queries problematic, as each polity has in fact a *distribution of* signatures rather than a single value. The Northern Song aridity maps make this visually evident — the arid north and wet south are collapsed into a single average that describes neither region well.

Beyond comparison, there are questions about internal variation, and what we might call "environmental enhancement" — as Northern Song expands southward, it doesn't just get a different signature, it gains access to a fundamentally different environmental portfolio.

How might comparison of signature sets work across polities?

## Possible Approaches

### Distributional comparison
Instead of a single weighted mean, represent each polity-time-slice as a distribution per variable. Compare polities using something like the **Wasserstein distance** (earth mover's distance) between their basin distributions — "how much work does it take to reshape the environmental distribution of the Roman Empire into that of the Han Dynasty?" This respects internal heterogeneity rather than averaging it away.

### Summary statistics beyond the mean
Keep the weighted mean but supplement it with **variance, skewness, range, and quantiles** (25th, 75th). A polity with high internal variance in aridity (like Northern Song, spanning arid north to wet south) is fundamentally different from one with uniformly moderate aridity, even if the means match. The variance *is* information — it tells you about the diversity of environmental niches a polity governs.

### Multivariate signatures as point clouds
Each polity is a **cloud of basin-points in n-dimensional signature space**. Compare clouds using Hausdorff distance, or compute convex hulls and measure overlap. Two polities with similar means but different shapes in signature space are governing different kinds of environmental portfolios.

### Typological approach using existing basin clusters
Cluster the basins within each polity (using the existing k=20 basin clusters from the full 190k basin analysis), then represent each polity as a **histogram over cluster types**. For example: "Northern Song at 962 was 60% cluster-7 (warm semi-arid) and 25% cluster-12 (temperate lowland)" vs. at 980 "35% cluster-7, 20% cluster-12, 30% cluster-3 (subtropical wet)." This makes comparison tractable — you're comparing discrete distributions over a shared vocabulary of environmental types.

### Environmental enhancement as a research question
The "enhancement" pattern observed in Northern Song (expanding territory brings dramatically different environmental resources) is itself a testable hypothesis across the whole Cliopatria corpus: **as polities expand, do they generally diversify environmentally, or do they expand into similar territory?** This requires the distributional representation to answer — a mean-only approach would miss the diversification signal entirely.

## Considerations

- All approaches are computationally feasible with existing EDOP data (190k basins, 47 signature fields, Cliopatria temporal geometries)
- The epistemic caveat applies: environmental data is modern; Bands B–C are proxies for relative spatial variation, not reconstructions of past conditions. Band A (physiographic) is genuinely stable over historical timescales. Band D (Anthropocene markers) is relevant only for modern polities.
- The choice of representation should be driven by the kinds of queries historians and spatial humanities researchers actually want to ask
- These approaches are not mutually exclusive — summary stats are cheap, distributional comparisons add depth, the typological approach provides interpretability

---

*Generated during CEDOP development session, 08 Feb 2026. To be discussed with ISHI (Pitt) and Seshat collaborators regarding applicability and methods.*
