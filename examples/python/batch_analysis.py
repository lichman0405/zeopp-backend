"""
Zeo++ API Batch Analysis Script

This script processes multiple structure files and exports results to CSV.
"""

import requests
import csv
import sys
from pathlib import Path
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime

# API configuration
API_BASE_URL = "http://localhost:9876"

# Probe radius (can be adjusted as needed)
PROBE_RADIUS = 1.82  # N2 probe


@dataclass
class AnalysisResult:
    """Analysis result data class"""
    filename: str
    formula: str = ""
    # Pore diameter
    Di: float = 0.0  # Maximum included sphere diameter
    Df: float = 0.0  # Maximum free sphere diameter
    Dif: float = 0.0  # Included sphere diameter along free path
    # Surface area
    ASA_m2_g: float = 0.0  # Accessible surface area m²/g
    NASA_m2_g: float = 0.0  # Non-accessible surface area m²/g
    # Volume
    density: float = 0.0  # Density g/cm³
    AV_fraction: float = 0.0  # Accessible volume fraction
    AV_cm3_g: float = 0.0  # Accessible volume cm³/g
    # Channel
    channel_dim: int = 0  # Channel dimensionality
    # Status
    status: str = "success"
    error_message: str = ""


def analyze_structure(file_path: Path) -> AnalysisResult:
    """
    Perform complete analysis on a single structure file
    """
    result = AnalysisResult(filename=file_path.name)
    
    try:
        # 1. Pore diameter calculation
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/pore_diameter",
                files={"structure_file": (file_path.name, f)},
                data={"ha": "true"},
                timeout=60
            )
        if response.status_code == 200:
            data = response.json()
            result.Di = data.get("included_diameter", 0)
            result.Df = data.get("free_diameter", 0)
            result.Dif = data.get("included_along_free", 0)
        
        # 2. Surface area calculation
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/surface_area",
                files={"structure_file": (file_path.name, f)},
                data={
                    "chan_radius": str(PROBE_RADIUS),
                    "probe_radius": str(PROBE_RADIUS),
                    "samples": "2000",
                    "ha": "true"
                },
                timeout=120
            )
        if response.status_code == 200:
            data = response.json()
            result.ASA_m2_g = data.get("asa_mass", 0)
            result.NASA_m2_g = data.get("nasa_mass", 0)
        
        # 3. Accessible volume calculation
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/accessible_volume",
                files={"structure_file": (file_path.name, f)},
                data={
                    "chan_radius": str(PROBE_RADIUS),
                    "probe_radius": str(PROBE_RADIUS),
                    "samples": "50000",
                    "ha": "true"
                },
                timeout=180
            )
        if response.status_code == 200:
            data = response.json()
            result.density = data.get("density", 0)
            result.AV_fraction = data.get("av", {}).get("fraction", 0)
            result.AV_cm3_g = data.get("av", {}).get("mass", 0)
        
        # 4. Channel analysis
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/channel_analysis",
                files={"structure_file": (file_path.name, f)},
                data={
                    "probe_radius": str(PROBE_RADIUS),
                    "ha": "true"
                },
                timeout=60
            )
        if response.status_code == 200:
            data = response.json()
            result.channel_dim = data.get("dimension", 0)
        
        # 5. Framework information
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/framework_info",
                files={"structure_file": (file_path.name, f)},
                data={"ha": "true"},
                timeout=60
            )
        if response.status_code == 200:
            data = response.json()
            result.formula = data.get("formula", "")
        
    except requests.exceptions.Timeout:
        result.status = "timeout"
        result.error_message = "Request timed out"
    except requests.exceptions.ConnectionError:
        result.status = "connection_error"
        result.error_message = f"Cannot connect to {API_BASE_URL}"
    except Exception as e:
        result.status = "error"
        result.error_message = str(e)
    
    return result


def batch_analyze(
    input_dir: Path,
    output_file: Path,
    max_workers: int = 4,
    extensions: List[str] = None
) -> List[AnalysisResult]:
    """
    Batch analyze all structure files in a directory
    
    Args:
        input_dir: Directory containing structure files
        output_file: Output CSV file path
        max_workers: Maximum number of parallel threads
        extensions: List of file extensions to process
    """
    if extensions is None:
        extensions = [".cif", ".cssr", ".v1", ".pdb", ".xyz"]
    
    # Collect all structure files
    structure_files = []
    for ext in extensions:
        structure_files.extend(input_dir.glob(f"*{ext}"))
    
    if not structure_files:
        print(f"No structure files found in {input_dir}")
        return []
    
    print(f"Found {len(structure_files)} structure files")
    print(f"Using probe radius: {PROBE_RADIUS} Å")
    print(f"Parallel threads: {max_workers}")
    print("-" * 60)
    
    results = []
    completed = 0
    
    # Use thread pool for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(analyze_structure, f): f 
            for f in structure_files
        }
        
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1
                status_icon = "✓" if result.status == "success" else "✗"
                print(f"[{completed}/{len(structure_files)}] {status_icon} {file_path.name}")
            except Exception as e:
                completed += 1
                print(f"[{completed}/{len(structure_files)}] ✗ {file_path.name}: {e}")
    
    # Export to CSV
    if results:
        fieldnames = list(asdict(results[0]).keys())
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(asdict(r))
        print("-" * 60)
        print(f"Results saved to: {output_file}")
    
    # Print statistics
    success_count = sum(1 for r in results if r.status == "success")
    print(f"Success: {success_count}/{len(results)}")
    
    return results


def main():
    """Main function"""
    # Use example directory by default
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    else:
        input_dir = Path(__file__).parent.parent / "sample_structures"
    
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"zeopp_results_{timestamp}.csv")
    
    if not input_dir.exists():
        print(f"Error: Directory does not exist {input_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("Zeo++ Batch Analysis Tool")
    print("=" * 60)
    print(f"Input directory: {input_dir}")
    print(f"Output file: {output_file}")
    print()
    
    try:
        batch_analyze(input_dir, output_file)
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API service {API_BASE_URL}")
        print("Please ensure Zeo++ API service is running:")
        print("  docker-compose up -d")
        sys.exit(1)


if __name__ == "__main__":
    main()
