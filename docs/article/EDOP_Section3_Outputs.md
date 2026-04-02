# 3. Outputs and Analytical Use

EDOP produces environmental signatures as structured, comparable representations of environmental context. These outputs are not limited to raw attribute values but include derived forms that support comparison, aggregation, and exploratory analysis. This section describes what the model produces in practice and the types of analytical operations it enables.

## 3.1 Environmental Signatures as Vectors

At its most fundamental level, an environmental signature is a vector representation of environmental conditions associated with a place or region. These vectors are derived from a set of environmental variables—transformed and, where appropriate, reduced in dimensionality—to enable consistent comparison across locations.

Representing environmental context as a vector allows places to be situated within a continuous environmental space. In this space, similarity between places can be quantified using distance metrics such as cosine similarity. This provides a basis for identifying places that are environmentally similar, even when they are geographically distant.

## 3.2 Derived Representations

In addition to raw or minimally processed attribute sets, EDOP produces derived representations that support analysis:

- **Dimensionality-reduced vectors**, which capture dominant patterns of environmental variation across the dataset  
- **Similarity rankings**, in which places are ordered according to their proximity in environmental space  
- **Clustered groupings**, which may emerge from unsupervised analysis and suggest environmental typologies  

These representations are not fixed classifications but are contingent on the underlying parameterization of the model, including variable selection and transformation choices.

## 3.3 Aggregation Over Regions

While environmental signatures can be generated for individual locations, many research questions concern regions rather than points. EDOP supports the aggregation of environmental signatures over arbitrary spatial extents, including historically defined regions whose boundaries may change over time.

Aggregation can be performed in multiple ways, including simple averaging, area-weighted summaries, or distributional representations that preserve variability within the region. This allows researchers to compare regions not only in terms of central tendencies but also in terms of the spread and structure of environmental conditions.

The ability to generate signatures for temporally varying regions is particularly important for historical analysis, where political or cultural boundaries shift over time. EDOP enables the comparison of environmental context across such changes, supporting the analysis of how environmental conditions may have evolved alongside historical processes.

## 3.4 Comparative Operations

Once environmental signatures are constructed, a range of comparative operations becomes possible:

- **Place-to-place comparison**, identifying locations with similar environmental characteristics  
- **Region-to-region comparison**, enabling the analysis of environmental differences between historical or cultural areas  
- **Temporal comparison**, examining how the environmental context of a region changes as its spatial extent evolves  

These operations allow environmental context to be incorporated into broader analytical workflows, including historical comparison and hypothesis generation.

## 3.5 Sensitivity and Model Variation

Because environmental signatures are the result of parameterized modeling choices, they are inherently sensitive to those choices. Variations in scale, variable selection, neighborhood definition, or the inclusion of relational components (such as upstream influences) can lead to different representations of the same place.

EDOP makes this sensitivity visible rather than concealing it. By allowing users to adjust parameters and observe how outputs change, the framework supports a more exploratory mode of analysis. Differences in resulting signatures and similarity relationships can be interpreted as reflecting alternative assumptions about what constitutes the relevant environmental context.

In this way, EDOP enables not only the comparison of places, but also the comparison of models. Environmental signatures become artifacts of explicit modeling decisions, and their variation provides insight into the role of those decisions in shaping analytical outcomes.
