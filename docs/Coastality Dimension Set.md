# EDOP: Coastality Dimension Set

## Overview

This note outlines a proposed **Coastality Dimension Set** for inclusion in EDOP signatures. The aim is to enrich environmental characterization by capturing multiple, distinct relationships to the sea—moving beyond simple distance-to-coast measures toward a more **process-aware, relational model**.

The central idea:

> Proximity to the sea is not a single variable, but a composite of geometric, hydrologic, ecological, and human-access dimensions.

---

## Motivation

### Why Coastality Matters

Across many regions (e.g., Patagonia), environmental and human systems are strongly influenced by marine adjacency. However:

- Marine influence is **not uniform**
- Coastal proximity does **not guarantee productivity or settlement**
- Hydrologic connectivity and oceanographic processes often matter more than distance alone

This motivates a multi-dimensional approach.

---

## Core Conceptual Distinctions

### 1. Geometric vs Relational Proximity

- **Geometric proximity**: straight-line distance to coast
- **Relational proximity**: position within systems connected to the sea (e.g., drainage networks)

These may diverge significantly.

---

### 2. Three Modes of “Coastal Influence”

| Mode | Description | Mechanism |
|------|-------------|----------|
| Hydrologic | Connection via drainage systems | River networks, basin outlets |
| Ecological | Influence of marine productivity | Currents, upwelling, shelf systems |
| Human-access | Practical interaction with sea | Ports, harbors, fisheries |

These should not be conflated.

---

## Proposed Coastality Variables

### A. Geometric Measures

- **Distance to nearest coastline (Euclidean)**
- **Elevation relative to sea level**
- **Slope toward coast**

**Purpose:** Baseline spatial reference

---

### B. Hydrologic Connectivity (Graph-Derived)

Derived from HydroBASINS structure.

#### 1. Distance to Basin Mouth
- Downstream path length to marine outlet
- More meaningful than straight-line distance

#### 2. Topological Depth from Coast
- Number of downstream steps to outlet
- Captures position within drainage hierarchy

#### 3. Basin Outlet Type
- Marine (exorheic)
- Endorheic (closed basin)
- Terminal lake / inland sink

#### 4. Downstream Discharge Proxy
- Magnitude of flow at outlet (if available)
- Proxy for strength of marine linkage

**Conceptual framing:**
> The sea as a terminal node in a hydrologic graph.

---

### C. Coastal Adjacency (Non-Hydrologic)

#### 1. Direct Coastal Contact
- Binary or distance threshold measure

#### 2. Shelf Context
- Continental shelf width (proxy)
- Shallow vs steep coastal margin

#### 3. Estuarine / Delta Presence
- Indicator of nutrient-rich interface zones

---

### D. Oceanographic Context (Optional / Advanced)

These extend beyond basin data but may be incorporated later.

- Upwelling zones
- Major currents (e.g., Malvinas Current)
- Sea surface productivity proxies (chlorophyll)
- Thermal regimes (cold vs warm currents)

---

### E. Human-Relevant Coastality

Bridging environmental and settlement feasibility.

#### 1. Harbor Suitability (proxy)
- Coastal morphology
- Exposure vs shelter

#### 2. Marine Resource Potential
- Fisheries productivity zones (if available)

#### 3. Accessibility Gradient
- Coast reachable vs isolated

---

## Application: Patagonia as Test Case

Patagonia provides a strong validation scenario:

### Key contrasts:
- Rich marine shelf vs sparse terrestrial settlement
- Coastal proximity vs lack of freshwater
- Hydrologic disconnection in many areas

### Hypothesis:
> Coastality dimensions will show that marine richness does not equate to settlement viability without complementary terrestrial conditions.

---

## Analytical Opportunities

### 1. Disentangling Coastality

Test whether:
- Euclidean proximity
- Hydrologic connectivity
- Oceanographic richness

produce distinct environmental signatures.

---

### 2. Settlement Feasibility Framework

Link coastality variables to:

- **Feasibility** (can settlement exist?)
- **Viability** (can it sustain itself?)
- **Attractiveness** (does it attract settlement?)

---

### 3. Threshold Effects

Investigate combinations such as:

- Water + coastal access
- Harbor + marine productivity
- River corridor + ocean outlet

---

## Methodological Notes

### Strengths

- Uses existing HydroBASINS graph structure
- Aligns with EDOP’s relational philosophy
- Moves beyond static spatial descriptors

### Limitations

- Hydrologic connectivity ≠ human accessibility
- Marine influence often not mediated by rivers
- Coastal processes may require external datasets

---

## Suggested Framing (for publication or presentation)

> Coastality is not a scalar distance but a multi-dimensional environmental relation, comprising geometric proximity, hydrologic connectivity, ecological influence, and human accessibility.

Or more concisely:

> The sea is not merely an edge of land, but a terminal attractor within environmental systems.

---

## Next Steps

- Implement hydrologic distance-to-sea from basin graph
- Add categorical outlet types
- Compare geometric vs graph-derived measures
- Test against Patagonia settlement patterns
- Evaluate need for marine-side data integration

---

## Closing Insight

This dimension set supports a broader EDOP goal:

> Representing environment not as static attributes, but as structured relationships within connected systems.