# Zeo++ Output Parser
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13
# Updated: 2025-12-22 - Enhanced error handling
# Updated: 2025-12-31 - Refactored to eliminate code duplication


import re
from typing import List
from app.core.exceptions import ZeoppParsingError
from app.utils.logger import logger


def _extract_value(key: str, tokens: List[str], default: float = 0.0) -> float:
    """
    Extract a float value following a key from a list of tokens.
    
    Args:
        key: The key to search for (e.g., "Unitcell_volume:")
        tokens: List of string tokens to search in
        default: Default value to return if extraction fails
    
    Returns:
        The extracted float value, or default if not found/invalid
    """
    try:
        idx = tokens.index(key)
        return float(tokens[idx + 1])
    except ValueError as e:
        logger.warning(f"Failed to convert '{key}' value to float: {e}")
        return default
    except IndexError:
        logger.warning(f"Key '{key}' not found in tokens or missing value after key")
        return default


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
    
    Raises:
        ZeoppParsingError: If the output format is invalid
    """
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ZeoppParsingError(
            "VOL output incomplete or malformed. Expected at least 2 lines.",
            output_file="result.vol",
            raw_content=text
        )

    tokens1 = lines[0].split()
    tokens2 = lines[1].split()

    return {
        "unitcell_volume": _extract_value("Unitcell_volume:", tokens1),
        "density": _extract_value("Density:", tokens1),
        "av": {
            "unitcell": _extract_value("AV_A^3:", tokens1),
            "fraction": _extract_value("AV_Volume_fraction:", tokens1),
            "mass": _extract_value("AV_cm^3/g:", tokens1),
        },
        "nav": {
            "unitcell": _extract_value("NAV_A^3:", tokens2),
            "fraction": _extract_value("NAV_Volume_fraction:", tokens2),
            "mass": _extract_value("NAV_cm^3/g:", tokens2),
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
    
    Raises:
        ZeoppParsingError: If the output format is invalid
        """
    lines = text.strip().splitlines()
    default_result = {
        "dimension": 0,
        "included_diameter": 0.0,
        "free_diameter": 0.0,
        "included_along_free": 0.0
    }
    
    if not lines or len(lines) < 2:
        logger.warning("CHAN output has fewer than 2 lines, returning default values")
        return default_result

    try:
        dim_line = lines[0]
        if "dimensionality" not in dim_line:
            raise ZeoppParsingError(
                "Expected 'dimensionality' keyword not found in first line",
                output_file="result.chan",
                raw_content=text
            )
        
        # Extract dimensionality value
        dim_part = dim_line.split("dimensionality")[1].strip()
        dim = int(dim_part.split()[0] if ' ' in dim_part else dim_part[0])
        
        # Parse second line
        tokens = lines[1].split()
        if len(tokens) < 5:
            raise ZeoppParsingError(
                f"Expected at least 5 tokens in second line, got {len(tokens)}",
                output_file="result.chan",
                raw_content=text
            )
        
        return {
            "dimension": dim,
            "included_diameter": float(tokens[2]),
            "free_diameter": float(tokens[3]),
            "included_along_free": float(tokens[4])
        }
    except (ValueError, IndexError) as e:
        logger.warning(f"Failed to parse CHAN data: {e}. Returning default values.")
        return default_result


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
    
    Raises:
        ZeoppParsingError: If the output format is invalid
    """
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ZeoppParsingError(
            "SA output incomplete or malformed. Expected at least 2 lines.",
            output_file="result.sa",
            raw_content=text
        )

    tokens1 = lines[0].split()
    tokens2 = lines[1].split()

    return {
        "asa_unitcell": _extract_value("ASA_A^2:", tokens1),
        "asa_volume": _extract_value("ASA_m^2/cm^3:", tokens1),
        "asa_mass": _extract_value("ASA_m^2/g:", tokens1),
        "nasa_unitcell": _extract_value("NASA_A^2:", tokens2),
        "nasa_volume": _extract_value("NASA_m^2/cm^3:", tokens2),
        "nasa_mass": _extract_value("NASA_m^2/g:", tokens2),
    }


def parse_volpo_from_text(text: str) -> dict:
    """
    Parse content of Zeo++ .volpo file string for probe occupiable volume.

    Format:
    @ ... POAV_A^3: <float> POAV_Volume_fraction: <float> POAV_cm^3/g: <float>
    PONAV_A^3: <float> PONAV_Volume_fraction: <float> PONAV_cm^3/g: <float>
    
    Raises:
        ZeoppParsingError: If the output format is invalid
    """
    lines = text.strip().splitlines()
    if len(lines) < 2:
        raise ZeoppParsingError(
            "VOLPO output malformed. Expected at least 2 lines.",
            output_file="result.volpo",
            raw_content=text
        )

    tokens1 = lines[0].split()
    tokens2 = lines[1].split()

    return {
        "poav_unitcell": _extract_value("POAV_A^3:", tokens1),
        "poav_fraction": _extract_value("POAV_Volume_fraction:", tokens1),
        "poav_mass": _extract_value("POAV_cm^3/g:", tokens1),
        "ponav_unitcell": _extract_value("PONAV_A^3:", tokens2),
        "ponav_fraction": _extract_value("PONAV_Volume_fraction:", tokens2),
        "ponav_mass": _extract_value("PONAV_cm^3/g:", tokens2),
    }


def parse_res_from_text(text: str) -> dict:
    """
    Parse .res file text to extract pore diameters.
    Expected format:
    EDI.res    4.89082 3.03868  4.81969
    
    Raises:
        ZeoppParsingError: If the output format is invalid
    """
    tokens = text.strip().split()
    if len(tokens) < 4:
        raise ZeoppParsingError(
            f"Malformed .res file output. Expected at least 4 tokens, got {len(tokens)}",
            output_file="result.res",
            raw_content=text
        )
    
    try:
        return {
            "included_diameter": float(tokens[1]),
            "free_diameter": float(tokens[2]),
            "included_along_free": float(tokens[3])
        }
    except (ValueError, IndexError) as e:
        raise ZeoppParsingError(
            f"Failed to parse .res file values: {e}",
            output_file="result.res",
            raw_content=text
        )


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
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse channels/pockets from line: {e}")
        elif "nodes assigned to pores" in line:
            try:
                result["nodes_assigned"] = int(line.split()[0])
            except (ValueError, IndexError) as e:
                logger.warning(f"Failed to parse nodes_assigned from line: {e}")

    return result


def parse_strinfo_from_text(text: str) -> dict:
    """
    Parses the dense single-line content of a .strinfo file using a comprehensive
    regular expression to extract all available details.
    
    Raises:
        ZeoppParsingError: If the output format is invalid
    """
    text = text.strip()

    pattern = re.compile(
        r'^(?P<filename>\S+)\s+'
        r'(?P<formula>\S+)\s+'
        r'(?P<segments>\d+)\s*segments:\s*'
        r'(?P<num_frameworks>\d+)\s*framework\(s\)\s*'
        r'\(1D/2D/3D\s+(?P<dims_1d>\d+)\s+(?P<dims_2d>\d+)\s+(?P<dims_3d>\d+)\s*\)\s*and\s*'
        r'(?P<num_molecules>\d+)\s*molecule\(s\)'
    )
    
    match = pattern.search(text)
    
    if not match:
        raise ZeoppParsingError(
            "Failed to parse .strinfo file. The format was not recognized.",
            output_file="result.strinfo",
            raw_content=text
        )
        
    data = match.groupdict()
    
    num_frameworks = int(data['num_frameworks'])
    framework_details = []
    
    fw_id_counter = 1
    for _ in range(int(data['dims_3d'])):
        framework_details.append({"framework_id": fw_id_counter, "dimensionality": 3})
        fw_id_counter += 1
    for _ in range(int(data['dims_2d'])):
        framework_details.append({"framework_id": fw_id_counter, "dimensionality": 2})
        fw_id_counter += 1
    for _ in range(int(data['dims_1d'])):
        framework_details.append({"framework_id": fw_id_counter, "dimensionality": 1})
        fw_id_counter += 1

    return {
        "filename": data['filename'],
        "formula": data['formula'],
        "segments": int(data['segments']),
        "number_of_frameworks": num_frameworks,
        "number_of_molecules": int(data['num_molecules']),
        "frameworks": framework_details
    }

def parse_oms_from_text(text: str) -> dict:
    """
    Parses the content of a .oms file to find the count of open metal sites.
    It looks for a line containing "Number of open metal sites:".
    
    Raises:
        ZeoppParsingError: If the output format is invalid
    """
    lines = text.strip().splitlines()
    for line in lines:
        if "Number of open metal sites" in line:
            try:
                count = int(line.split(":")[1].strip())
                return {"open_metal_sites_count": count}
            except (IndexError, ValueError) as e:
                raise ZeoppParsingError(
                    f"Failed to parse OMS count from line: '{line}'. Error: {e}",
                    output_file="result.oms",
                    raw_content=text
                )

    raise ZeoppParsingError(
        "Could not find the line 'Number of open metal sites' in the .oms output.",
        output_file="result.oms",
        raw_content=text
    )