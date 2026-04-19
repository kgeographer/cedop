# Statistical-Methodology Reading List for EDOPS Characterization

A short, targeted list organized by the methodological issue it addresses. Canonical references first, accessible secondary sources where useful. Not comprehensive — targeted at the specific findings in the Task 1 log.

---

## 1. Compositional Data Analysis

*Relevant to: F1.3 (clay/silt/sand sum-constrained to 100%); any future work with PNV shares or land-cover fractions.*

**Canonical**

- Aitchison, J. (1986). *The Statistical Analysis of Compositional Data*. Chapman and Hall. The foundational text. Dense but clear. The key concept is the log-ratio transform (alr, clr, ilr) that moves compositional data from the constrained simplex to unconstrained real space where standard multivariate techniques work.
- Pawlowsky-Glahn, V., Egozcue, J. J., & Tolosana-Delgado, R. (2015). *Modeling and Analysis of Compositional Data*. Wiley. The modern standard, more accessible than Aitchison.

**Accessible entry points**

- van den Boogaart, K. G., & Tolosana-Delgado, R. (2013). *Analyzing Compositional Data with R*. Springer. Practical, with the `compositions` R package.
- Greenacre, M. (2021). *Compositional Data Analysis in Practice*. CRC Press. Short and practical.

**Key concept to know by name**: the isometric log-ratio (ilr) transform — the one you'd apply to the clay/silt/sand triple before putting it into PCA.

---

## 2. MAUP and Scale Effects in Spatial Analysis

*Relevant to: F1.10 (ecoregion counts driven by basin polygon size); the whole scale-sensitivity task; the methods paper's likely first empirical contribution.*

**Canonical**

- Openshaw, S. (1984). *The Modifiable Areal Unit Problem*. CATMOG 38, Geo Books. The original monograph. Short and foundational.
- Fotheringham, A. S., & Wong, D. W. S. (1991). "The modifiable areal unit problem in multivariate statistical analysis." *Environment and Planning A*, 23(7), 1025–1044. The paper that demonstrated how severely MAUP distorts multivariate results. This is the one most directly relevant to what you're doing.

**For current practice**

- Wong, D. (2009). "The Modifiable Areal Unit Problem (MAUP)." In Fotheringham & Rogerson (eds.), *The SAGE Handbook of Spatial Analysis*. A good mid-length review of remediation approaches.
- Manley, D. (2021). "Scale, aggregation, and the modifiable areal unit problem." In *Handbook of Regional Science*. For the current state of the debate.

**GIScience-specific framing**

- Goodchild, M. F. (2011). "Scale in GIS: An overview." *Geomorphology*, 130(1–2), 5–9. Your diss advisor on this specific topic — worth citing if only for the lineage.

---

## 3. Log-Transformation and Heavy-Tailed Distributions

*Relevant to: F1.2 (slope right-skew), F1.6 (discharge extreme skew), and most hydrological variables.*

This is well-trodden ground and doesn't need a deep reading list. The general toolkit:

- Box, G. E. P., & Cox, D. R. (1964). "An analysis of transformations." *JRSS B*, 26(2), 211–252. The Box-Cox transformation — a family including log as a special case. Useful when you want to be principled about the choice.
- For hydrological variables specifically: most hydrology texts (Chow, Maidment & Mays; or Dingman) handle discharge distributions as a standard topic. A log-Pearson III or log-normal distribution is the usual assumption for river discharge.

**The practical move**: `np.log1p()` before any PCA/clustering for discharge-like variables. Document the transformation; it's standard but worth naming.

---

## 4. Zero-Inflation and Sparse Variables

*Relevant to: F1.7 (karst, permafrost, wetlands as >50% zero); any variable where the zero represents "absent" rather than "small."*

**Canonical**

- Lambert, D. (1992). "Zero-inflated Poisson regression, with an application to defects in manufacturing." *Technometrics*, 34(1), 1–14. The paper that introduced the zero-inflated modeling framework.
- Agresti, A. (2013). *Categorical Data Analysis* (3rd ed.). Wiley. Chapter on zero-inflated models. A standard reference.

**For spatial/environmental contexts**

- Welsh, A. H., Cunningham, R. B., Donnelly, C. F., & Lindenmayer, D. B. (1996). "Modelling the abundance of rare species: statistical models for counts with extra zeros." *Ecological Modelling*, 88(1–3), 297–308. Ecology-flavored treatment that parallels your situation well.

**The practical move for your case**: decide per-variable whether zero means "absent" (treat separately) or "effectively zero but on a continuum" (log1p and keep). For karst and permafrost, "absent" is almost certainly right — two-tier analysis.

---

## 5. Mixture Models and Bimodal Distributions

*Relevant to: F1.4 (temperature bimodality); probably to aridity and other climate variables once examined; methodological fork for Task 5 clustering.*

**Canonical**

- McLachlan, G. J., & Peel, D. (2000). *Finite Mixture Models*. Wiley. The standard reference.
- McLachlan, G. J., Lee, S. X., & Rathnayake, S. I. (2019). "Finite mixture models." *Annual Review of Statistics and its Application*, 6, 355–378. A condensed update.

**More accessible**

- Bishop, C. M. (2006). *Pattern Recognition and Machine Learning*. Springer. Chapter 9 on mixture models and EM. Standard graduate text, freely available as a PDF from Bishop's website.

**For your specific case**: Gaussian mixture models via `sklearn.mixture.GaussianMixture` will let you confirm the bimodality quantitatively and assign each basin a posterior probability of cold-regime vs. warm-regime membership — which becomes a stratification variable for downstream analysis.

---

## 6. Multivariate Methods — PCA and Clustering for Spatial Data

*Relevant to: Task 4 (correlation structure) and Task 5 (pre-clustering).*

**Standard multivariate references**

- Everitt, B., & Hothorn, T. (2011). *An Introduction to Applied Multivariate Analysis with R*. Springer. Accessible, practical, covers PCA and clustering in sequence.
- Jolliffe, I. T. (2002). *Principal Component Analysis* (2nd ed.). Springer. The canonical PCA text — dense but comprehensive.
- Everitt, B., Landau, S., Leese, M., & Stahl, D. (2011). *Cluster Analysis* (5th ed.). Wiley. The standard reference for clustering methods.

**For HDBSCAN specifically**

- Campello, R. J. G. B., Moulavi, D., & Sander, J. (2013). "Density-based clustering based on hierarchical density estimates." *PAKDD 2013 proceedings*. The HDBSCAN paper.
- McInnes, L., Healy, J., & Astels, S. (2017). "hdbscan: Hierarchical density based clustering." *Journal of Open Source Software*, 2(11), 205. Software paper, practical.

**For clustering with geographic data specifically**

- Grubesic, T. H., Wei, R., & Murray, A. T. (2014). "Spatial clustering overview and comparison: accuracy, sensitivity, and computational expense." *Annals of the AAG*, 104(6), 1134–1156. Useful for choosing between methods.

---

## 7. Spatial Autocorrelation and Its Consequences

*Relevant to: §7 of the prospectus (acknowledged challenge); any correlation or regression claim you eventually make across basins.*

Not specifically surfaced in Task 1 findings but will become relevant quickly.

**Canonical**

- Cliff, A. D., & Ord, J. K. (1981). *Spatial Processes: Models and Applications*. Pion. The foundational text on spatial autocorrelation statistics.
- Anselin, L. (1995). "Local indicators of spatial association — LISA." *Geographical Analysis*, 27(2), 93–115. Introduced local Moran's I, widely used.
- Getis, A. (2008). "A history of the concept of spatial autocorrelation: a geographer's perspective." *Geographical Analysis*, 40(3), 297–309. Historical framing.

**For practical use**

- Bivand, R. S., Pebesma, E., & Gómez-Rubio, V. (2013). *Applied Spatial Data Analysis with R* (2nd ed.). Springer. The practical reference.
- PySAL documentation (pysal.org). The Python ecosystem.

---

## 8. Mantel Test and Matrix-Correlation Methods

*Relevant to: the planned D-PLACE correspondence experiment — this is the specific test you committed to in the prospectus.*

**Canonical**

- Mantel, N. (1967). "The detection of disease clustering and a generalized regression approach." *Cancer Research*, 27(2), 209–220. The original paper.
- Legendre, P., & Legendre, L. (2012). *Numerical Ecology* (3rd ed.). Elsevier. Chapter 10 on matrix correlations is the standard reference for how to do this carefully in practice, including partial Mantel tests.

**Current debates worth knowing about**

- Guillot, G., & Rousset, F. (2013). "Dismantling the Mantel tests." *Methods in Ecology and Evolution*, 4(4), 336–344. Critique of uncritical Mantel test use. Worth reading so you can anticipate reviewer concerns.
- Legendre, P., Fortin, M.-J., & Borcard, D. (2015). "Should the Mantel test be used in spatial analysis?" *Methods in Ecology and Evolution*, 6(11), 1239–1247. Response to the above; nuances the critique.

---

## 9. Dataset Characterization / Profiling as a Named Practice

*Relevant to: the framing question about what "exploration" vs. "evaluation" is.*

This is less a statistical topic than a vocabulary one — useful for how you write up the phase.

- Dasu, T., & Johnson, T. (2003). *Exploratory Data Mining and Data Cleaning*. Wiley. Older but still the clearest treatment of pre-analytical data characterization as a structured practice with its own standards.
- Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley. The original EDA text. Tukey's framing of the distinction between confirmatory and exploratory analysis is the intellectual ancestor of what you're doing now.

---

## Priority for Immediate Reading

If I were sequencing this for near-term usefulness to the characterization work:

1. **Fotheringham & Wong 1991** — short, paper-length, directly relevant to F1.10 and the scale-sensitivity work generally. Read first.
2. **A compositional data intro** (Greenacre 2021 or the shorter bits of Pawlowsky-Glahn 2015) — needed before Task 5 if soil variables are in the PCA.
3. **Bishop 2006 Ch. 9** — needed to handle F1.4's bimodality quantitatively.
4. **Legendre & Legendre 2012 Ch. 10** — needed before the D-PLACE correspondence experiment, not now.

Everything else can wait until the specific finding that triggers it.

---

A small suggestion for how to use this list: add a top-level `docs/edop/method_references.md` or similar to the project, copy this into it, and as you read something, annotate inline with a one-line "what I took from this" note. That way the references become working knowledge attached to specific findings rather than a reading list you intend to get to — and the annotations become part of the methods paper's citation scaffold.