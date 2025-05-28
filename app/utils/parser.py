# Zeo++ Output Parser
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

import re
from pathlib import Path
from typing import Dict, Any


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


def parse_strinfo_from_text(text: str) -> dict:
    """
    Parse .strinfo file content and extract framework count and dimensionality.

    Expected format:
    Molecule types found: 1
    Molecule 0: Dimensionality = 3
    Identified 1 channels and 0 pockets
    108 nodes assigned to pores.

    Returns:
        {
            "num_frameworks": int,
            "frameworks": List[{"id": int, "dimensionality": int}],
            "channels": int,
            "pockets": int,
            "nodes_assigned": int,
            "raw": str
        }
    """
    lines = text.strip().splitlines()
    frameworks = []
    channels = 0
    pockets = 0
    nodes = 0

    for line in lines:
        if "Molecule types found" in line:
            pass  # total is counted by len(frameworks)
        elif line.startswith("Molecule"):
            tokens = line.strip().split()
            frameworks.append({
                "id": int(tokens[1].strip(":")),
                "dimensionality": int(tokens[-1])
            })
        elif "Identified" in line and "channels" in line:
            parts = line.split()
            channels = int(parts[1])
            pockets = int(parts[4])
        elif "nodes assigned to pores" in line:
            try:
                nodes = int(line.split()[0])
            except Exception:
                pass

    return {
        "num_frameworks": len(frameworks),
        "frameworks": frameworks,
        "channels": channels,
        "pockets": pockets,
        "nodes_assigned": nodes,
        "raw": text.strip()
    }


def parse_nt2_from_text(text: str) -> dict:
    """
    Parse Zeo++ .nt2 file to extract basic Voronoi network statistics.

    Looks for:
    - Node count: lines starting with 'node' (ignoring comments)
    - Edge count: lines starting with 'edge'

    Returns:
        {
            "node_count": int,
            "edge_count": int,
            "raw": str
        }
    """
    lines = text.strip().splitlines()
    node_count = 0
    edge_count = 0

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("node"):
            node_count += 1
        elif line.startswith("edge"):
            edge_count += 1

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "raw": text.strip()
    }
