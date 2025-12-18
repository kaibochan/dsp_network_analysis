import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FINAL_DATA_DIR, LOGGING_DIR, LOG_LEVELS, GRAPH_OUTPUT_DIR
from utils.logging import Logger, LogLevel
import json
from collections import deque

logger = Logger(LOGGING_DIR, "item_analysis.log", LOG_LEVELS)
result_log = Logger(LOGGING_DIR, "item_analysis_results.log", LOG_LEVELS)

# Define realistic end-game production targets (items/min)
end_game_targets = {
    # Science Matrices - continuous research
    'Electromagnetic Matrix': 60.0,
    'Energy Matrix': 60.0,
    'Structure Matrix': 60.0,
    'Information Matrix': 60.0,
    'Gravity Matrix': 60.0,
    'Universe Matrix': 30.0,  # Slowest but still needed
    
    # Main inventory items
    'Conveyor Belt MK II': 300.0,
    'Conveyor Belt MK III': 300.0,
    'Sorter MK II': 200.0,
    'Sorter MK III': 200.0,
    'Arc Smelter': 10.0,
    'Assembling Machine MK II': 10.0,
    'Assembling Machine MK III': 10.0,
    'Traffic Monitor': 10.0,
    'Spray Coater': 5.0,
    'Depot MK I': 5.0,
    'Depot MK II': 5.0,
    'Storage Tank': 5.0,
    'Logistics Distributor': 5.0,
    
    # Buildings
    'Satellite Substation': 5.0,
    'Accumulator': 20.0,
    'Mini Fusion Power Plant': 1.0,
    'Mining Machine': 5.0,
    'Water Pump': 5.0,
    'Chemical Plant': 5.0,
    'Quantum Chemical Plant': 2.0,
    'Matrix Lab': 2.0,    
    
    # Key buildings for expansion
    'Vertical Launching Silo': 1.0,
    #'Interstellar Logistics Station': 2.0,
    #'Planetary Logistics Station': 4.0,
    #'Artificial Star': 2.0,
    #'Particle Collider': 1.0,
    #'Ray Receiver': 5.0,   
    
    # Dyson Sphere components
    'Frame Material': 100.0,
    'Dyson Sphere Component': 30.0,
    'Small Carrier Rocket': 10.0,
    'Solar Sail': 200.0,
    
    # Other random things
    'Graviton Lens': 15.0,
}

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def build_dependency_graph(items_data, buildings_data):
    item_dependencies = dict()
    building_dependencies = dict()
    
    for item in items_data:
        item_dependencies[item["product"]] = item["ingredients"]
        
    for building in buildings_data:
        building_dependencies[building["product"]] = building["ingredients"]
    
    return item_dependencies, building_dependencies
        
def analyze_item_dependencies(item_dependencies, building_dependencies, target_items):
    results = {}
    sources = {}  # Track where demand comes from
    queue = deque()
    
    logger(LogLevel.INFO, "Analyzing item dependencies for target production rates...")
    
    # initialize queue with all target items
    for item, target_rate in target_items.items():
        queue.append((item, target_rate, "End-game target"))
        logger(LogLevel.DEBUG, f"Queued target item {item} with rate {target_rate} items/min")
        
    # process queue until empty (BFS)
    while queue:
        current_node, required_rate, source_description = queue.popleft()
        logger(LogLevel.DEBUG, f"Processing {current_node} needing {required_rate} items/min from {source_description}")
        
        # accumulate rate for this item for this pass
        if current_node not in results:
            results[current_node] = 0.0
            sources[current_node] = []
            
        results[current_node] += required_rate
        sources[current_node].append((source_description, required_rate))
        
        # determine if the current node is an item or building
        dependencies = None
        if current_node in item_dependencies:
            dependencies = item_dependencies[current_node]
        elif current_node in building_dependencies:
            dependencies = building_dependencies[current_node]
        else:
            logger(LogLevel.WARNING, f"  - Warning: No dependency data found for {current_node}")
            continue
        
        # add all dependencies to the queue to be processed in the future
        for ingredient, quantity in dependencies.items():
            value = quantity * required_rate
            queue.append((ingredient, value, f"Used by {current_node}"))
            logger(LogLevel.DEBUG, f"  - Queued dependency {ingredient} needing {value:.2f} items/min to support {current_node}")
                
        logger(LogLevel.INFO, f"Completed analysis for {item}.")
        
    # Prepare output lines
    output_lines = []
    output_lines.append("")
    output_lines.append("=" * 100)
    output_lines.append("DEPENDENCY ANALYSIS COMPLETE - REQUIRED PRODUCTION RATES")
    output_lines.append("=" * 100)
    output_lines.append("")
    
    # Sort by rate descending to show highest-demand items first
    sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
    
    output_lines.append(f"{'Item':<40} {'Items/Min':>15} {'Assemblers':>15} {'Scale'}")
    output_lines.append("-" * 100)
    
    for item, rate in sorted_results:
        assemblers = rate / 60.0  # Assuming ~60 items/min per assembler
        
        # Determine scale category
        if rate >= 50000:
            scale = "Multi-System (5+ planets)"
        elif rate >= 20000:
            scale = "Multi-Planet (3-4 planets)"
        elif rate >= 5000:
            scale = "Full Planet"
        elif rate >= 1000:
            scale = "Single Planet"
        elif rate >= 100:
            scale = "Regional"
        else:
            scale = "Local"
        
        output_lines.append(f"{item:<40} {rate:>12.1f}   ~{assemblers:>8.0f}           {scale}")
    
    output_lines.append("=" * 100)
    output_lines.append("GREATEST CONTRIBUTORS PER ITEM")
    output_lines.append("=" * 100)
    output_lines.append("")
    
    for item, rate in sorted_results:  
        output_lines.append(f"{item:<40} {rate:>12.1f}   ~{assemblers:>8.0f}           {scale}")
        
        # Show top 3 sources of demand for this item
        if item in sources and sources[item]:
            # Sort sources by contribution (descending) and take top 3
            top_sources = sorted(sources[item], key=lambda x: x[1], reverse=True)[:3]
            for source_name, source_value in top_sources:
                if source_value > 0.1:  # Only show significant contributors
                    output_lines.append(f"    └─ {source_name}: {source_value:.1f} items/min")
    
    output_lines.append("")
    output_lines.append("=" * 100)
    output_lines.append("ALL SOURCES WITH CONTRIBUTIONS")
    output_lines.append("=" * 100)
    output_lines.append("")
    for item, rate in sorted_results:  
        output_lines.append(f"{item}: Total {rate:.1f} items/min")
        
        if item in sources and sources[item]:
            for source_name, source_value in sources[item]:
                output_lines.append(f"    └─ {source_name}: {source_value:.1f} items/min")
        output_lines.append("")
    
    # Print to console
    print("\n" + "\n".join(output_lines))
    
    # Write to file
    with open(f"{LOGGING_DIR}/item_analysis_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
            
if __name__ == "__main__":
    logger(LogLevel.INFO, "Starting item dependency analysis...", reset=True)
    result_log(LogLevel.INFO, "Item Dependency Analysis Results", reset=True)
    
    items_data = load_data(f"{FINAL_DATA_DIR}/items.json")
    buildings_data = load_data(f"{FINAL_DATA_DIR}/buildings.json")
    
    item_preds, building_preds = build_dependency_graph(items_data, buildings_data)    
    analyze_item_dependencies(item_preds, building_preds, end_game_targets)