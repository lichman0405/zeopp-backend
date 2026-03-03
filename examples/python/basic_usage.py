"""
Zeo++ API Basic Usage Examples

This script demonstrates how to call various Zeo++ API endpoints.
"""

import requests
from pathlib import Path

# API configuration
API_BASE_URL = "http://localhost:9876"

# Example structure file path
SAMPLE_FILE = Path(__file__).parent.parent / "sample_structures" / "EDI.cif"


def check_health():
    """Check API service status"""
    print("=" * 60)
    print("1. Health Check")
    print("=" * 60)
    
    # Basic health check
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Basic Health: {response.json()}")
    
    # Detailed health check
    response = requests.get(f"{API_BASE_URL}/health/detailed")
    print(f"Detailed Health: {response.json()}")
    
    # Version info
    response = requests.get(f"{API_BASE_URL}/version")
    print(f"Version: {response.json()}")
    print()


def calculate_pore_diameter(file_path: Path, force_recalculate: bool = False):
    """Calculate pore diameter"""
    print("=" * 60)
    print("2. Pore Diameter Calculation")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {"ha": "true"}
        
        # Add force_recalculate parameter (optional)
        if force_recalculate:
            data["force_recalculate"] = "true"
            print("⚡ Force recalculation mode (skip cache)")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/pore_diameter",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"Maximum included sphere diameter (Di): {result['included_diameter']:.4f} Å")
    print(f"Maximum free sphere diameter (Df): {result['free_diameter']:.4f} Å")
    print(f"Included sphere diameter along free path (Dif): {result['included_along_free']:.4f} Å")
    print(f"From cache: {result['cached']}")
    print()
    return result


def calculate_surface_area(file_path: Path, probe_radius: float = 1.82):
    """Calculate surface area"""
    print("=" * 60)
    print(f"3. Surface Area Calculation (probe_radius={probe_radius} Å)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {
            "chan_radius": str(probe_radius),
            "probe_radius": str(probe_radius),
            "samples": "2000",
            "ha": "true"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/surface_area",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"Accessible surface area (ASA): {result['asa_mass']:.2f} m²/g")
    print(f"Accessible surface area (volume): {result['asa_volume']:.2f} m²/cm³")
    print(f"Non-accessible surface area (NASA): {result['nasa_mass']:.2f} m²/g")
    print()
    return result


def calculate_volume(file_path: Path, probe_radius: float = 1.82):
    """Calculate accessible volume"""
    print("=" * 60)
    print(f"4. Accessible Volume Calculation (probe_radius={probe_radius} Å)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {
            "chan_radius": str(probe_radius),
            "probe_radius": str(probe_radius),
            "samples": "50000",
            "ha": "true"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/accessible_volume",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"Unit cell volume: {result['unitcell_volume']:.2f} Å³")
    print(f"Density: {result['density']:.4f} g/cm³")
    print(f"Accessible volume: {result['av']['mass']:.4f} cm³/g ({result['av']['fraction']*100:.2f}%)")
    print(f"Non-accessible volume: {result['nav']['mass']:.4f} cm³/g")
    print()
    return result


def calculate_channel(file_path: Path, probe_radius: float = 1.82):
    """Channel analysis"""
    print("=" * 60)
    print(f"5. Channel Analysis (probe_radius={probe_radius} Å)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {
            "probe_radius": str(probe_radius),
            "ha": "true"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/channel_analysis",
            files=files,
            data=data
        )
    
    result = response.json()
    dim_names = {0: "Isolated pore", 1: "1D channel", 2: "2D layer", 3: "3D interconnected"}
    print(f"Channel dimensionality: {result['dimension']} ({dim_names.get(result['dimension'], 'Unknown')})")
    print(f"Channel included sphere diameter: {result['included_diameter']:.4f} Å")
    print(f"Channel free sphere diameter: {result['free_diameter']:.4f} Å")
    print()
    return result


def get_framework_info(file_path: Path):
    """Get framework information"""
    print("=" * 60)
    print("6. Framework Information")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {"ha": "true"}
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/framework_info",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"Chemical formula: {result['formula']}")
    print(f"Number of frameworks: {result['number_of_frameworks']}")
    print(f"Number of molecules: {result['number_of_molecules']}")
    for fw in result['frameworks']:
        print(f"  - Framework {fw['framework_id']}: {fw['dimensionality']}D")
    print()
    return result


def full_analysis(file_path: Path):
    """Complete analysis workflow"""
    print("\n" + "=" * 60)
    print("Complete Zeo++ Analysis Report")
    print(f"Structure file: {file_path.name}")
    print("=" * 60 + "\n")
    
    # Execute all analyses
    check_health()
    pore = calculate_pore_diameter(file_path)
    sa = calculate_surface_area(file_path)
    vol = calculate_volume(file_path)
    chan = calculate_channel(file_path)
    fw = get_framework_info(file_path)
    
    # Print summary
    print("=" * 60)
    print("Analysis Summary")
    print("=" * 60)
    print(f"Chemical formula: {fw['formula']}")
    print(f"Maximum free sphere diameter (Df): {pore['free_diameter']:.4f} Å")
    print(f"Maximum included sphere diameter (Di): {pore['included_diameter']:.4f} Å")
    print(f"Accessible surface area: {sa['asa_mass']:.2f} m²/g")
    print(f"Accessible volume fraction: {vol['av']['fraction']*100:.2f}%")
    print(f"Channel dimensionality: {chan['dimension']}D")
    print()


if __name__ == "__main__":
    # Check if example file exists
    if not SAMPLE_FILE.exists():
        print(f"Error: Cannot find example file {SAMPLE_FILE}")
        print("Please ensure you are running this script in the correct directory")
        exit(1)
    
    # Run complete analysis
    try:
        full_analysis(SAMPLE_FILE)
        
        # Demonstrate force_recalculate parameter
        print("=" * 60)
        print("Additional Example: Force Recalculation (force_recalculate)")
        print("=" * 60)
        print("Using force_recalculate=True skips cache and forces Zeo++ calculation:")
        print()
        calculate_pore_diameter(SAMPLE_FILE, force_recalculate=True)
        
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API service {API_BASE_URL}")
        print("Please ensure Zeo++ API service is running:")
        print("  docker-compose up -d")
        exit(1)
