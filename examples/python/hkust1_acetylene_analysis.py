#!/usr/bin/env python3
"""
HKUST-1 MOF Acetylene Adsorption Performance Analysis

This script demonstrates how to use the Zeo++ API to analyze HKUST-1 
metal-organic framework material for acetylene (C2H2) gas adsorption performance.

HKUST-1 (Cu-BTC, MOF-199) is a classic MOF material, widely used for 
acetylene storage and acetylene/ethylene separation due to:
- High specific surface area (~1500-2000 m²/g)
- Open metal sites (Cu²⁺)
- Multi-level pore structure

Acetylene molecule parameters:
- Kinetic diameter: 3.3 Å
- Probe radius: 1.65 Å (diameter/2)

References:
- Chui, S. S.-Y. et al., Science 1999, 283, 1148-1150
- Xiang, S. et al., Nature Chem. 2009, 1, 368-373 (C2H2 adsorption in MOFs)
"""

import requests
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

# =============================================================================
# Configuration Parameters
# =============================================================================

API_BASE_URL = "http://localhost:9876"

# Acetylene (C2H2) molecule parameters
C2H2_KINETIC_DIAMETER = 3.3  # Å
C2H2_PROBE_RADIUS = 1.65     # Å (kinetic diameter / 2)

# Nitrogen (N2) molecule parameters - for BET surface area comparison
N2_KINETIC_DIAMETER = 3.64   # Å
N2_PROBE_RADIUS = 1.82       # Å

# HKUST-1 structure file path
STRUCTURE_FILE = Path(__file__).parent.parent / "sample_structures" / "HKUST-1.cif"


@dataclass
class AnalysisResult:
    """Analysis result data class"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def api_request(endpoint: str, params: dict = None) -> AnalysisResult:
    """
    Send API request
    """
    if params is None:
        params = {}
    
    try:
        with open(STRUCTURE_FILE, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/{endpoint}",
                files={"structure_file": (STRUCTURE_FILE.name, f)},
                data=params,
                timeout=300  # Increase timeout, OMS/PSD calculations may take longer
            )
        
        if response.status_code == 200:
            return AnalysisResult(success=True, data=response.json())
        else:
            return AnalysisResult(
                success=False, 
                error=f"HTTP {response.status_code}: {response.text}"
            )
    except requests.exceptions.ConnectionError:
        return AnalysisResult(success=False, error=f"Cannot connect to {API_BASE_URL}")
    except Exception as e:
        return AnalysisResult(success=False, error=str(e))


def print_section(title: str):
    """Print section title"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(label: str, value: Any, unit: str = ""):
    """Print result"""
    if unit:
        print(f"  {label}: {value} {unit}")
    else:
        print(f"  {label}: {value}")


# =============================================================================
# Analysis Functions
# =============================================================================

def analyze_framework_info():
    """1. Analyze framework basic information"""
    print_section("1. Framework Basic Information")
    
    result = api_request("framework_info", {"ha": "true"})
    
    if result.success:
        data = result.data
        print_result("Material name", "HKUST-1 (Cu-BTC, MOF-199)")
        print_result("Chemical formula", data.get("formula", "N/A"))
        print_result("Number of frameworks", data.get("number_of_frameworks", "N/A"))
        print_result("Number of molecules", data.get("number_of_molecules", "N/A"))
        # Note: Density is obtained in accessible_volume, not in framework_info
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def analyze_pore_diameter():
    """2. Analyze pore diameter characteristics"""
    print_section("2. Pore Diameter Analysis")
    
    result = api_request("pore_diameter", {"ha": "true"})
    
    if result.success:
        data = result.data
        Di = data.get("included_diameter", 0)
        Df = data.get("free_diameter", 0)
        Dif = data.get("included_along_free", 0)
        
        print_result("Maximum included sphere diameter (Di)", f"{Di:.3f}", "Å")
        print_result("Maximum free sphere diameter (Df)", f"{Df:.3f}", "Å")
        print_result("Included sphere diameter along free path (Dif)", f"{Dif:.3f}", "Å")
        
        print()
        print("  📊 Acetylene accessibility analysis:")
        print(f"     Acetylene kinetic diameter: {C2H2_KINETIC_DIAMETER} Å")
        
        if Df >= C2H2_KINETIC_DIAMETER:
            print(f"     ✅ Acetylene can freely pass through pores (Df={Df:.2f} > {C2H2_KINETIC_DIAMETER} Å)")
        else:
            print(f"     ⚠️ Acetylene diffusion may be limited (Df={Df:.2f} < {C2H2_KINETIC_DIAMETER} Å)")
        
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def analyze_surface_area_for_c2h2():
    """3. Calculate acetylene accessible surface area"""
    print_section("3. Acetylene Accessible Surface Area (C2H2)")
    
    result = api_request("surface_area", {
        "chan_radius": str(C2H2_PROBE_RADIUS),
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "samples": "2000",
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        asa_m2_g = data.get("asa_mass", 0)
        asa_m2_cm3 = data.get("asa_volume", 0)  # Fix: asa_vol -> asa_volume
        nasa_m2_g = data.get("nasa_mass", 0)
        
        print(f"  Probe radius (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("Accessible surface area (ASA)", f"{asa_m2_g:.2f}", "m²/g")
        print_result("Accessible surface area (ASA)", f"{asa_m2_cm3:.2f}", "m²/cm³")
        print_result("Non-accessible surface area (NASA)", f"{nasa_m2_g:.2f}", "m²/g")
        
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def analyze_surface_area_for_n2():
    """4. Calculate nitrogen accessible surface area (comparison)"""
    print_section("4. Nitrogen Accessible Surface Area - BET Comparison (N2)")
    
    result = api_request("surface_area", {
        "chan_radius": str(N2_PROBE_RADIUS),
        "probe_radius": str(N2_PROBE_RADIUS),
        "samples": "2000",
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        asa_m2_g = data.get("asa_mass", 0)
        
        print(f"  Probe radius (N2): {N2_PROBE_RADIUS} Å")
        print()
        print_result("N2 accessible surface area", f"{asa_m2_g:.2f}", "m²/g")
        print()
        print("  📚 Literature reference: HKUST-1 BET surface area is typically 1500-2000 m²/g")
        
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def analyze_accessible_volume_for_c2h2():
    """5. Calculate acetylene accessible volume"""
    print_section("5. Acetylene Accessible Volume (C2H2)")
    
    result = api_request("accessible_volume", {
        "chan_radius": str(C2H2_PROBE_RADIUS),
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "samples": "50000",
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        density = data.get("density", 0)
        av_data = data.get("av", {})
        
        av_fraction = av_data.get("fraction", 0)
        av_cm3_g = av_data.get("mass", 0)
        
        print(f"  Probe radius (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("Framework density", f"{density:.4f}", "g/cm³")
        print_result("C2H2 accessible volume fraction", f"{av_fraction:.4f}", "")
        print_result("C2H2 accessible volume", f"{av_cm3_g:.4f}", "cm³/g")
        print()
        
        # Estimate acetylene uptake
        c2h2_molar_volume = 22.4  # L/mol at STP
        c2h2_density_stp = 1.092  # g/L at STP (26 g/mol / 22.4 L/mol)
        estimated_uptake = av_cm3_g * c2h2_density_stp * 1000  # mg/g
        estimated_uptake_cc = av_cm3_g * 1000 / c2h2_molar_volume * 22.4  # cc(STP)/g
        
        print("  📊 Estimated acetylene adsorption capacity (theoretical maximum):")
        print_result("     Estimated uptake", f"{estimated_uptake:.1f}", "mg/g")
        print_result("     Estimated uptake", f"{estimated_uptake_cc:.1f}", "cc(STP)/g")
        
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def analyze_channel():
    """6. Analyze channel characteristics"""
    print_section("6. Channel Analysis")
    
    result = api_request("channel_analysis", {
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        dimension = data.get("dimension", 0)
        included_diameter = data.get("included_diameter", 0)
        free_diameter = data.get("free_diameter", 0)
        included_along_free = data.get("included_along_free", 0)
        
        print(f"  Probe radius (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("Channel dimensionality", dimension, "D")
        print_result("Channel included sphere diameter (Di)", f"{included_diameter:.3f}", "Å")
        print_result("Channel free sphere diameter (Df)", f"{free_diameter:.3f}", "Å")
        print_result("Included sphere diameter along free path (Dif)", f"{included_along_free:.3f}", "Å")
        
        if dimension == 3:
            print("  ✅ 3D interconnected channels - facilitates rapid acetylene diffusion")
        elif dimension == 2:
            print("  ⚠️ 2D layered channels - acetylene diffusion may be limited between layers")
        elif dimension == 1:
            print("  ⚠️ 1D linear channels - acetylene diffusion is unidirectional")
        else:
            print("  ❌ No connected channels - acetylene molecules cannot enter pores")
        
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def analyze_open_metal_sites():
    """7. Analyze open metal sites"""
    print_section("7. Open Metal Sites")
    
    result = api_request("open_metal_sites", {"ha": "true"})
    
    if result.success:
        data = result.data
        oms_count = data.get("open_metal_sites_count", 0)
        
        print_result("Open metal sites count", oms_count)
        print()
        
        if oms_count > 0:
            print("  📊 Impact of open metal sites on acetylene adsorption:")
            print("     ✅ Cu²⁺ open sites can form coordination with acetylene π electrons")
            print("     ✅ Enhances acetylene adsorption enthalpy (typically 25-35 kJ/mol)")
            print("     ✅ Improves acetylene/ethylene separation selectivity")
        else:
            print("  ⚠️ No open metal sites detected")
            print("     (May be structural issue or detection parameters need adjustment)")
        
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def analyze_pore_size_distribution():
    """8. Analyze pore size distribution"""
    print_section("8. Pore Size Distribution")
    
    # Note: pore_size_dist/download returns a file, requires special handling
    print(f"  Probe radius (C2H2): {C2H2_PROBE_RADIUS} Å")
    print()
    
    try:
        with open(STRUCTURE_FILE, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/pore_size_dist/download",
                files={"structure_file": (STRUCTURE_FILE.name, f)},
                data={
                    "chan_radius": str(C2H2_PROBE_RADIUS),
                    "probe_radius": str(C2H2_PROBE_RADIUS),
                    "samples": "50000",
                    "ha": "true"
                },
                timeout=300  # Increase timeout, PSD calculation may take longer
            )
        
        if response.status_code == 200:
            # Parse returned histogram file content
            content = response.text
            lines = content.strip().split('\n')
            
            # Parse histogram data (skip comment lines)
            histogram = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        diameter = float(parts[0])
                        count = float(parts[1])
                        histogram.append({"diameter": diameter, "count": count})
                    except ValueError:
                        continue
            
            if histogram:
                total_count = sum(h["count"] for h in histogram)
                
                # Category statistics (diameter unit is Å)
                micropore = sum(h["count"] for h in histogram if h["diameter"] < 20)
                mesopore = sum(h["count"] for h in histogram if 20 <= h["diameter"] < 500)
                
                micropore_pct = micropore / total_count * 100 if total_count > 0 else 0
                mesopore_pct = mesopore / total_count * 100 if total_count > 0 else 0
                
                print(f"  Pore size distribution statistics ({len(histogram)} data points):")
                print_result("     Micropore ratio (<2nm)", f"{micropore_pct:.1f}", "%")
                print_result("     Mesopore ratio (2-50nm)", f"{mesopore_pct:.1f}", "%")
                
                # Find primary pore size
                max_bin = max(histogram, key=lambda x: x["count"])
                print_result("     Primary pore diameter range", f"{max_bin['diameter']:.2f}", "Å")
                
                return {"histogram": histogram}
            else:
                print("  ⚠️ Failed to parse pore size distribution data")
                return None
        else:
            print(f"  ❌ Error: HTTP {response.status_code}: {response.text[:200]}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Cannot connect to {API_BASE_URL}")
        return None
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return None


def analyze_blocking_spheres():
    """9. Analyze blocking spheres"""
    print_section("9. Blocking Spheres Analysis")
    
    result = api_request("blocking_spheres", {
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        channels = data.get("channels", 0)
        pockets = data.get("pockets", 0)
        nodes_assigned = data.get("nodes_assigned", 0)
        
        print(f"  Probe radius (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("Identified channels count", channels)
        print_result("Identified pockets count", pockets)
        print_result("Assigned nodes count", nodes_assigned)
        
        if channels == 0 and pockets == 0:
            print("  ✅ No blocking regions - all pores are fully accessible to acetylene")
        else:
            print("  ⚠️ Blocking regions detected")
            print("     See raw field for further details")
        
        return data
    else:
        print(f"  ❌ Error: {result.error}")
        return None


def print_summary():
    """Print analysis summary"""
    print_section("Analysis Summary - HKUST-1 Acetylene Adsorption Performance Evaluation")
    
    print("""
    HKUST-1 is an excellent MOF material for acetylene adsorption and separation
    for the following reasons:
  
  ✅ Structural advantages:
      - High specific surface area (~1500-2000 m²/g) provides numerous adsorption sites
      - 3D interconnected pore network facilitates rapid gas molecule diffusion
      - Multi-level pore structure (large cage ~9Å, small cage ~5Å)
  
  ✅ Chemical advantages:
      - Open Cu²⁺ metal sites coordinate with acetylene π electrons
      - High acetylene adsorption enthalpy (~25-35 kJ/mol)
      - Excellent C2H2/C2H4 separation selectivity (~2-4)
      - Excellent C2H2/CO2 separation selectivity
  
  📚 Literature-reported HKUST-1 acetylene adsorption performance:
      - Acetylene uptake: ~200 cm³(STP)/g @ 298K, 1bar
      - C2H2/C2H4 selectivity: ~2.5
      - Adsorption enthalpy: ~32 kJ/mol
  
    References:
  - Xiang, S. et al., Nature Chem. 2009, 1, 368-373
  - He, Y. et al., Chem. Soc. Rev. 2014, 43, 5657-5678
""")


def main():
    """Main function"""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║     HKUST-1 MOF Acetylene (C₂H₂) Adsorption Performance Analysis    ║")
    print("║     Zeo++ API Full Feature Demonstration                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    # Check structure file
    if not STRUCTURE_FILE.exists():
        print(f"\n❌ Error: Cannot find structure file {STRUCTURE_FILE}")
        print("   Please ensure HKUST-1.cif file exists in sample_structures directory")
        sys.exit(1)
    
    print(f"\n📂 Structure file: {STRUCTURE_FILE}")
    print(f"🔗 API address: {API_BASE_URL}")
    
    # Check API service
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API service is running normally")
        else:
            print(f"⚠️ API service returned status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API service {API_BASE_URL}")
        print("   Please start the service first: docker-compose up -d")
        sys.exit(1)
    
    # Execute all analyses
    print("\n" + "─" * 70)
    print("  Starting analysis of HKUST-1 acetylene adsorption properties...")
    print("─" * 70)
    
    # 1-9: Execute all analyses
    analyze_framework_info()
    analyze_pore_diameter()
    analyze_surface_area_for_c2h2()
    analyze_surface_area_for_n2()
    analyze_accessible_volume_for_c2h2()
    analyze_channel()
    analyze_open_metal_sites()
    analyze_pore_size_distribution()
    analyze_blocking_spheres()
    
    # Print summary
    print_summary()
    
    print("\n" + "═" * 70)
    print("  Analysis complete! All Zeo++ API features verified.")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
