# Dyson Sphere Program Network Analysis
### Kai and Nick

## Motivations
The DSP Network Analysis program aims to leverage graph theory and community detection on the variously connected recipes of the game Dyson Sphere Program. Our hope is that through community detection, we will derive an optimal clustering of factories into manufacturing districts, while also providing production planning tools for end-game manufacturing optimization.

## Project Structure
```
dsp_network_analysis/
├── data/
│   ├── raw/          # Original CSV data from Google Sheets
│   ├── processed/    # Cleaned CSV files
│   └── final/        # Structured JSON recipe data (items.json, buildings.json)
├── data_manipulation/  # Recipe parsing tools
│   ├── data_manipulator.py  # Core CSV-to-JSON transformer
│   └── program.py           # Main entry point for data transformation
├── recipe_network/     # Graph analysis and visualization
│   ├── network_builder.py   # igraph-based network construction
│   ├── graph_builder.py     # PyVis/NetworkX graph builder and clustering
│   ├── modularity.py        # Custom modularity maximization implementation
│   └── program.py           # Main entry point for graph generation
├── src/
│   └── item_analysis.py    # Production dependency analysis tool
├── graphs/            # Output directory for interactive HTML visualizations
├── logs/              # Analysis results and debug logs
└── utils/
    └── logging.py     # Shared logging utilities
```

## Program Descriptions

### Data Manipulation Program
The **data_manipulation** program is a **Dyson Sphere Program recipe parser** that converts crafting recipe data from CSV format into structured JSON using the `FuckassDSPDataTransformer` class.

**What it does:**
- Takes CSV files containing item and building recipes (sourced from a Google Sheets database)
- Parses recipe strings like `"1- Particle Collider,1- Processor"` into structured ingredient dictionaries
- Outputs clean JSON files with products and their required ingredients/quantities
- Processes both **items** and **buildings** separately with detailed logging
- Handles weighted ingredient relationships for crafting dependencies

**Input:** CSV files with recipes in format: `Product Name,"quantity- ingredient,quantity- ingredient"`

**Output:** JSON arrays with structured objects:
```json
{
  "product": "Annihilation Constrain Sphere",
  "ingredients": {
    "Particle Collider": 1,
    "Processor": 1
  }
}
```

**Location:** Run `data_manipulation/program.py`

---

### Recipe Network Program
The **recipe_network** program constructs directed graphs from recipe data and performs community detection to identify manufacturing clusters. It supports two graph implementations: **igraph** for analysis and **PyVis/NetworkX** for interactive visualization.

**What it does:**
- **Builds directed graphs** where:
  - Nodes = items/buildings
  - Edges = recipe dependencies (product → ingredients)
  - Edge weights = ingredient quantities
- **Community detection** using greedy modularity maximization (Clauset-Newman-Moore algorithm)
- **Common ingredient analysis** - identifies products that share ingredients and clusters them
- **Interactive HTML visualizations** using PyVis with zoom, pan, and node selection
- **Network statistics** - tracks ingredient usage frequency and dependency patterns

**Key Features:**
- `RecipeNetwork` (igraph): Static network plotting with matplotlib
- `GraphBuilder` (NetworkX/PyVis): 
  - Interactive web-based graph visualization
  - Modularity-based community clustering with configurable resolution
  - Common ingredient clustering (groups products by 1, 2, 3+ shared ingredients)
  - Generates separate HTML files for each clustering view
- `GraphModularization`: Custom implementation of modularity maximization algorithm from Clauset, Newman, and Moore (2004)

**Input:** JSON recipe data from `data/final/items.json` and `data/final/buildings.json`

**Output:** 
- Interactive HTML graphs in `graphs/` directory:
  - `pyviz_graph.html` - Full recipe network with community clusters
  - `pyviz_graph_common_ingredients_N.html` - Clusters by N shared ingredients
- Detailed logs with ingredient usage statistics

**Location:** Run `recipe_network/program.py`

---

### Item Analysis Program
The **item_analysis** program performs comprehensive production dependency analysis for end-game manufacturing targets in Dyson Sphere Program. It calculates material requirements for complex production chains.

**What it does:**
- Takes user-defined production targets (items/minute) for end-game goals
- **Performs dependency traversal** through recipe chains to calculate all required intermediate materials
- **Aggregates demand** from multiple production chains that share common ingredients
- Tracks **contribution sources** - identifies which products drive demand for each material
- Provides **production scale estimates**:
  - Estimated assemblers needed (assuming ~60 items/min per assembler)
  - Scale categories: Local → Regional → Single Planet → Multi-Planet → Multi-System
- Generates detailed reports with multiple views of material requirements

**Features:**
- Processes both item recipes and building recipes
- Handles complex dependency chains (e.g., Science Matrices → intermediate components → raw materials)
- Identifies base resources with no dependencies (ores, raw materials)
- Warns about missing dependency data (e.g., Hydrogen, Antimatter)

**Target Categories:**
- **Science Matrices** - Continuous research production (60/min each, 30/min Universe Matrix)
- **Infrastructure** - Conveyor belts, sorters, logistics buildings
- **Manufacturing** - Assemblers, smelters, chemical plants
- **Dyson Sphere** - Frame materials, solar sails, rocket components
- **Power & Resources** - Accumulators, power plants, mining equipment

**Input:** 
- JSON recipe data from `data/final/items.json` and `data/final/buildings.json`
- Production targets defined in `end_game_targets` dictionary

**Output:** 
- Console output with formatted tables
- Comprehensive report in `logs/item_analysis_results.txt` with three sections:
  1. **Required Production Rates** - All materials sorted by demand (items/min)
  2. **Greatest Contributors** - Top 3 sources of demand for each material
  3. **All Sources** - Complete breakdown of every contribution to each material's demand
- Debug logs in `logs/item_analysis.log`

**Location:** Run `src/item_analysis.py`

---

## Usage

1. **Parse recipe data from CSV to JSON:**
   ```bash
   python data_manipulation/program.py
   ```

2. **Generate interactive network visualizations:**
   ```bash
   python recipe_network/program.py
   ```
   Then open `graphs/pyviz_graph.html` in a web browser to explore the recipe network.

3. **Analyze production requirements:**
   ```bash
   python src/item_analysis.py
   ```
   Review `logs/item_analysis_results.txt` for comprehensive material requirements.

---

## Key Outputs

- **Interactive Graphs** (`graphs/` directory):
  - Open any `.html` file in a web browser to explore recipe networks
  - Zoom, pan, and click nodes to see connections
  - Color-coded by community clusters
  
- **Production Analysis** (`logs/item_analysis_results.txt`):
  - Sorted list of all materials by production rate
  - Scale estimates from "Local" to "Multi-System"
  - Detailed breakdown of demand sources

- **Debug Logs** (`logs/` directory):
  - Detailed processing logs for debugging and analysis verification