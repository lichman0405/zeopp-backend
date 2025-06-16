# Zeo++ Output Parser
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13


def parse_vol_from_text(text: str) -> dict:
    """
    Parse content of Zeo++ .vol file from string for volume and density.
    Expected format:
    @ ... Unitcell_volume: <float> Density: <float>
    AV_A^3: <float> AV_Volume_fraction: <float> AV_cm^3/g: <float>
    NAV_A^3: <float> NAV_Volume_fraction: <float> NAV_cm^3/g: <float>
    
    Returns:
        dict with keys:
        - unitcell_volume
        - density
        - av (dict with keys: unitcell, fraction, mass)
        - nav (dict with keys: unitcell, fraction, mass)
    """
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("VOL output incomplete or malformed.")

    tokens1 = lines[0].split()
    tokens2 = lines[1].split()

    def extract(name: str, tokens: list[str]) -> float:
        try:
            return float(tokens[tokens.index(name) + 1])
        except (ValueError, IndexError):
            return 0.0

    return {
        "unitcell_volume": extract("Unitcell_volume:", tokens1),
        "density": extract("Density:", tokens1),
        "av": {
            "unitcell": extract("AV_A^3:", tokens1),
            "fraction": extract("AV_Volume_fraction:", tokens1),
            "mass": extract("AV_cm^3/g:", tokens1),
        },
        "nav": {
            "unitcell": extract("NAV_A^3:", tokens2),
            "fraction": extract("NAV_Volume_fraction:", tokens2),
            "mass": extract("NAV_cm^3/g:", tokens2),
        }
    }


def parse_chan_from_text(text: str) -> dict:
    """
    Parse content of Zeo++ .chan file from string for channel dimensionality.
    Expected format:
    @ ... dimensionality: <int>
    <int> included_diameter: <float> free_diameter: <float> included_along_free: <float>
    <int> included_diameter: <float> free_diameter: <float> included_along_free: <float>
    ...
    Returns:
        
        dict with keys:
        - dimension
        - included_diameter
        - free_diameter
        - included_along_free
    
        """
    lines = text.strip().splitlines()
    if not lines or len(lines) < 2:
        return {
            "dimension": 0,
            "included_diameter": 0.0,
            "free_diameter": 0.0,
            "included_along_free": 0.0
        }

    try:
        dim_line = lines[0]
        dim = int(dim_line.split("dimensionality")[1].strip()[0])
        tokens = lines[1].split()
        return {
            "dimension": dim,
            "included_diameter": float(tokens[2]),
            "free_diameter": float(tokens[3]),
            "included_along_free": float(tokens[4])
        }
    except Exception:
        return {
            "dimension": 0,
            "included_diameter": 0.0,
            "free_diameter": 0.0,
            "included_along_free": 0.0
        }


def parse_sa_from_text(text: str) -> dict:
    """
    Parse content of Zeo++ .sa file from string for surface area.

    Expected format:
    @ ... ASA_A^2: <float> ASA_m^2/cm^3: <float> ASA_m^2/g: <float>
    NASA_A^2: <float> NASA_m^2/cm^3: <float> NASA_m^2/g: <float>

    Returns:
        dict with keys:
        - asa_unitcell
        - asa_volume
        - asa_mass
        - nasa_unitcell
        - nasa_volume
        - nasa_mass
    """
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("SA output incomplete or malformed.")

    tokens1 = lines[0].split()
    tokens2 = lines[1].split()

    def extract(name: str, tokens: list[str]) -> float:
        try:
            return float(tokens[tokens.index(name) + 1])
        except (ValueError, IndexError):
            return 0.0  # or raise a more descriptive error if desired

    return {
        "asa_unitcell": extract("ASA_A^2:", tokens1),
        "asa_volume": extract("ASA_m^2/cm^3:", tokens1),
        "asa_mass": extract("ASA_m^2/g:", tokens1),
        "nasa_unitcell": extract("NASA_A^2:", tokens2),
        "nasa_volume": extract("NASA_m^2/cm^3:", tokens2),
        "nasa_mass": extract("NASA_m^2/g:", tokens2),
    }


def parse_volpo_from_text(text: str) -> dict:
    """
    Parse content of Zeo++ .volpo file string for probe occupiable volume.

    Format:
    @ ... POAV_A^3: <float> POAV_Volume_fraction: <float> POAV_cm^3/g: <float>
    PONAV_A^3: <float> PONAV_Volume_fraction: <float> PONAV_cm^3/g: <float>
    """
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError("VOLPO output malformed")

    tokens1 = lines[0].split()
    tokens2 = lines[1].split()

    def extract(key: str, tokens: list[str]) -> float:
        try:
            return float(tokens[tokens.index(key) + 1])
        except (ValueError, IndexError):
            return 0.0

    return {
        "poav_unitcell": extract("POAV_A^3:", tokens1),
        "poav_fraction": extract("POAV_Volume_fraction:", tokens1),
        "poav_mass": extract("POAV_cm^3/g:", tokens1),
        "ponav_unitcell": extract("PONAV_A^3:", tokens2),
        "ponav_fraction": extract("PONAV_Volume_fraction:", tokens2),
        "ponav_mass": extract("PONAV_cm^3/g:", tokens2),
    }


def parse_res_from_text(text: str) -> dict:
    """
    Parse .res file text to extract pore diameters.
    Expected format:
    EDI.res    4.89082 3.03868  4.81969
    """
    tokens = text.strip().split()
    if len(tokens) < 4:
        raise ValueError("Malformed .res file output")
    return {
        "included_diameter": float(tokens[1]),
        "free_diameter": float(tokens[2]),
        "included_along_free": float(tokens[3])
    }


def parse_block_from_text(text: str) -> dict:
    """
    Parse .block output content from Zeo++ to extract summary info.

    Example lines:
    Identified 0 channels and 2 pockets
    139 nodes assigned to pores.
    """
    result = {
        "channels": 0,
        "pockets": 0,
        "nodes_assigned": 0,
        "raw": text.strip()
    }

    for line in text.splitlines():
        if "Identified" in line and "channels" in line and "pockets" in line:
            try:
                parts = line.split()
                result["channels"] = int(parts[1])
                result["pockets"] = int(parts[4])
            except Exception:
                pass
        elif "nodes assigned to pores" in line:
            try:
                result["nodes_assigned"] = int(line.split()[0])
            except Exception:
                pass

    return result

def parse_psd_from_text(text: str) -> dict:
    """
    Parses the content of a .psd_histo file into a list of histogram data points.
    This version is more robust and skips header lines that do not start with numbers.
    """
    histogram_data = []
    lines = text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        
        parts = line.split()
        if len(parts) < 4:
            continue
        
        try:
            float(parts[0])

            data_point = {
                "radius": float(parts[0]),
                "pore_volume": float(parts[1]),
                "cumulative_volume": float(parts[2]),
                "derivative_pore_volume": float(parts[3]),
            }
            histogram_data.append(data_point)
        except (ValueError, IndexError):
            continue
    
    if not histogram_data:
        raise ValueError("No valid numerical data points found in the .psd_histo output.")

    return {"psd_histogram_data": histogram_data}


def parse_strinfo_from_text(text: str) -> dict:
    """
    Parses the content of a .strinfo file.
    Example format:
    Number of frameworks: 1
    Framework 1 dimensionality: 3
    """
    frameworks = []
    lines = text.strip().splitlines()
    if not lines:
        raise ValueError("Empty .strinfo file content.")

    try:
        num_frameworks_line = lines[0]
        num_frameworks = int(num_frameworks_line.split(":")[1].strip())


        for line in lines[1:]:
            if "dimensionality" in line:
                parts = line.split()
                framework_id = int(parts[1])
                dimensionality = int(parts[3])
                frameworks.append({
                    "framework_id": framework_id,
                    "dimensionality": dimensionality
                })

        if len(frameworks) != num_frameworks:
            raise ValueError("Mismatch between reported number of frameworks and parsed framework details.")

        return {
            "number_of_frameworks": num_frameworks,
            "frameworks": frameworks
        }
    except (IndexError, ValueError) as e:
        raise ValueError(f"Failed to parse .strinfo file content: '{text}'. Error: {e}")

def parse_oms_from_text(text: str) -> dict:
    """
    Parses the content of a .oms file to find the count of open metal sites.
    It looks for a line containing "Number of open metal sites:".
    """
    lines = text.strip().splitlines()
    for line in lines:
        if "Number of open metal sites" in line:
            try:
                count = int(line.split(":")[1].strip())
                return {"open_metal_sites_count": count}
            except (IndexError, ValueError) as e:
                raise ValueError(f"Failed to parse OMS count from line: '{line}'. Error: {e}")

    raise ValueError("Could not find the line 'Number of open metal sites' in the .oms output.")