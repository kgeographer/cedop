

Place2Vec (the foundational paper)
Yan, B., Janowicz, K., Mai, G., & Gao, S. (2017). From ITDL to Place2Vec: Reasoning about place type similarity and relatedness by learning embeddings from augmented spatial contexts. Proceedings of the 25th ACM SIGSPATIAL International Conference on Advances in Geographic Information Systems (SIGSPATIAL '17), Article 35, 1–10.
DOI: https://doi.org/10.1145/3139958.3140054
hex2vec
Woźniak, S., & Szymański, P. (2021). hex2vec: Context-aware embedding H3 hexagons with OpenStreetMap tags. Proceedings of the 4th ACM SIGSPATIAL International Workshop on AI for Geographic Knowledge Discovery (GeoAI '21), 61–71. arXiv
arXiv: https://arxiv.org/abs/2111.00970
ACM DOI: https://doi.org/10.1145/3486635.3491076
GeoVeX (hex2vec's successor, worth knowing about)
Donghi, D., et al. (2023). GeoVeX: Geospatial vectors with hexagonal convolutional autoencoders. Proceedings of the 6th ACM SIGSPATIAL International Workshop on AI for Geographic Knowledge Discovery (GeoAI '23). OpenReview
OpenReview: https://openreview.net/forum?id=7bvWopYY1H
A very recent comprehensive survey that just appeared and would give you a systematic map of this entire field:
Representation learning for geospatial data (2025). Annals of GIS / International Journal of Digital Earth (Tandfonline). Taylor & Francis Online
https://www.tandfonline.com/doi/full/10.1080/19475683.2025.2552157
— This is worth reading carefully. It categorizes the whole field along spatial vs. semantic dimensions and explicitly discusses location encoders, which is structurally what EDOP is, though applied to the natural environment rather than the built one.

A critical observation about the whole family: all of these — Place2Vec, hex2vec, GeoVeX, and the S2Vec Google paper that just came out — are working on the built environment: POI types, OSM tags, land use, urban functions. Their validation methods (downstream socioeconomic prediction, human judgment triplet tests, region typology clustering) are all calibrated to that context. EDOP is doing the structurally identical operation on the natural environment, which is actually underrepresented in this literature. That's worth noting explicitly in any positioning document — it's a gap you're filling, not a niche you're crowding into.
For the validation methodology question specifically, the triplet evaluation in Place2Vec (human judges rank which of three POI types is most dissimilar) and the downstream task benchmarking in GeoVeX/S2Vec are the most directly applicable methodological models. Your Mantel test approach is arguably more rigorous than either for your purposes, since you have an independent cultural similarity matrix rather than a proxy prediction task.