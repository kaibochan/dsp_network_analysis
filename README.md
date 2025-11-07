# Dyson Sphere Program Network Analysis
### Kai and Nick

## Program Descriptions
### Data Manipulation Program
The **data_manipulation** program is a **Dyson Sphere Program recipe parser** that converts crafting recipe data from CSV format into structured JSON. 

**What it does:**
- Takes CSV files containing item and building recipes (sourced from a Google Sheets database)
- Parses recipe strings like `"1- Particle Collider,1- Processor"` into structured ingredient lists
- Outputs clean JSON files with products and their required ingredients/quantities
- Processes both **items** and **buildings** separately with detailed logging

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