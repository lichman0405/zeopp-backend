# Zeo++ Output Parser
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13
# Updated: 2025-12-22 - Enhanced error handling
# Updated: 2025-12-31 - Refactored to eliminate code duplication
# Updated: 2026-04-28 - Fixed line-split bug (NASA/NAV/PONAV all live on the
#                       same single `@`-line as ASA/AV/POAV; previous code
#                       wrongly searched them on the second
#                       "Number_of_channels:" line). Switched to whole-text
#                       token-pool lookup. Also enforced strict mode (silent
#                       default returns removed) and added optional
#                       channel/pocket extension fields for newer Zeo++
#                       output.


import re
from typing import Any, Dict, List, Optional

from app.core.exceptions import ZeoppParsingError
from app.utils.logger import logger


# ── Helpers ─────────────────────────────────────────────────────────────────


def _all_tokens(text: str) -> List[str]:
    """Split the entire output into a single flat token list.

    Zeo++ writes most metrics on a single ``@ ... key: value key: value ...``
    line, but newer versions append additional lines such as
    ``Number_of_channels:``, ``Channel_surface_area_A^2:`` etc. Splitting
    by line and assuming a fixed line-to-key mapping is unreliable; using
    a flat token pool lets us look up keys regardless of which physical
    line they appear on, which is robust to both old and new Zeo++
    versions.
    """
    return text.split()


def _extract_value(
    key: str,
    tokens: List[str],
    default: float = 0.0,
    *,
    required: bool = False,
    output_file: Optional[str] = None,
    raw_content: Optional[str] = None,
) -> float:
    """Extract a float value following ``key`` from a flat token list.

    Args:
        key: The exact key token to search for (e.g. ``"Unitcell_volume:"``).
        tokens: Flat list of tokens to search in.
        default: Returned when ``required`` is ``False`` and the key is
            missing or its value is not a float.
        required: When ``True``, raise :class:`ZeoppParsingError` on any
            failure instead of silently returning ``default``. Used for
            primary metrics whose absence indicates a real parsing
            problem.
        output_file: Optional output filename used in error messages.
        raw_content: Optional raw output included in errors for diagnostics.

    Returns:
        The parsed ``float`` value, or ``default`` when the key/value is
        missing and ``required`` is ``False``.

    Raises:
        ZeoppParsingError: Only when ``required=True`` and parsing fails.
    """
    try:
        idx = tokens.index(key)
    except ValueError:
        if required:
            raise ZeoppParsingError(
                f"Required key '{key}' not found in output",
                output_file=output_file,
                raw_content=raw_content,
            )
        logger.warning(
            f"Key '{key}' not found in output tokens, using default {default}"
        )
        return default

    if idx + 1 >= len(tokens):
        if required:
            raise ZeoppParsingError(
                f"Required key '{key}' has no value after it in output",
                output_file=output_file,
                raw_content=raw_content,
            )
        logger.warning(
            f"Key '{key}' has no value after it, using default {default}"
        )
        return default

    raw_value = tokens[idx + 1]
    try:
        return float(raw_value)
    except ValueError:
        if required:
            raise ZeoppParsingError(
                f"Value for key '{key}' is not a valid float: {raw_value!r}",
                output_file=output_file,
                raw_content=raw_content,
            )
        logger.warning(
            f"Value for key '{key}' is not a valid float: {raw_value!r}, "
            f"using default {default}"
        )
        return default


def _collect_floats_after(prefix: str, text: str) -> List[float]:
    """Collect all whitespace-separated float tokens immediately following
    a labelled prefix such as ``"Channel_surface_area_A^2:"``.

    Reading stops at the first non-float token (typically the next
    labelled section). Returns an empty list when the prefix is absent
    or no float follows it.
    """
    idx = text.find(prefix)
    if idx == -1:
        return []
    tail = text[idx + len(prefix):]
    out: List[float] = []
    for tok in tail.split():
        try:
            out.append(float(tok))
        except ValueError:
            break
    return out


def _extract_int(prefix: str, text: str) -> Optional[int]:
    """Extract the first integer following ``prefix`` in ``text``.

    Returns ``None`` if the prefix is missing or the next token is not an
    integer (these channel/pocket fields are optional in newer Zeo++
    output).
    """
    idx = text.find(prefix)
    if idx == -1:
        return None
    tail = text[idx + len(prefix):].split()
    if not tail:
        return None
    try:
        return int(tail[0])
    except ValueError:
        return None


# ── Parsers ─────────────────────────────────────────────────────────────────


def parse_vol_from_text(text: str) -> dict:
    """Parse Zeo++ ``-vol`` output (``.vol`` file) into a dict.

    Real Zeo++ output (single ``@``-line, plus optional appended lines
    in newer versions)::

        @ EDI.vol Unitcell_volume: 307.484   Density: 1.62239
        AV_A^3: 22.6493 AV_Volume_fraction: 0.07366 AV_cm^3/g: 0.0454022
        NAV_A^3: 0 NAV_Volume_fraction: 0 NAV_cm^3/g: 0
        Number_of_channels: 1 Channel_volume_A^3: 22.6493
        Number_of_pockets: 0
        Pocket_volume_A^3:

    All metrics may also appear on a single physical line, so we search
    the whole-text token pool rather than splitting by line.

    Returns:
        ``dict`` with keys ``unitcell_volume``, ``density``, ``av`` /
        ``nav`` sub-dicts, plus optional channel/pocket extension fields
        (``number_of_channels``, ``channel_volume_a3``,
        ``number_of_pockets``, ``pocket_volume_a3``) which are ``None``
        when not present in the output.

    Raises:
        ZeoppParsingError: When the ``@`` marker is missing or any of
            the primary AV metrics cannot be parsed.
    """
    if "@" not in text:
        raise ZeoppParsingError(
            "VOL output missing '@' header",
            output_file="result.vol",
            raw_content=text,
        )

    tokens = _all_tokens(text)
    kw = {"output_file": "result.vol", "raw_content": text}

    return {
        "unitcell_volume": _extract_value("Unitcell_volume:", tokens, required=True, **kw),
        "density": _extract_value("Density:", tokens, required=True, **kw),
        "av": {
            "unitcell": _extract_value("AV_A^3:", tokens, required=True, **kw),
            "fraction": _extract_value("AV_Volume_fraction:", tokens, required=True, **kw),
            "mass": _extract_value("AV_cm^3/g:", tokens, required=True, **kw),
        },
        "nav": {
            "unitcell": _extract_value("NAV_A^3:", tokens, required=True, **kw),
            "fraction": _extract_value("NAV_Volume_fraction:", tokens, required=True, **kw),
            "mass": _extract_value("NAV_cm^3/g:", tokens, required=True, **kw),
        },
        "number_of_channels": _extract_int("Number_of_channels:", text),
        "channel_volume_a3": _collect_floats_after("Channel_volume_A^3:", text) or None,
        "number_of_pockets": _extract_int("Number_of_pockets:", text),
        "pocket_volume_a3": _collect_floats_after("Pocket_volume_A^3:", text) or None,
    }


def parse_chan_from_text(text: str) -> dict:
    """Parse Zeo++ ``-chan`` output (``.chan`` file) into a dict.

    Real Zeo++ output (one ``Channel`` row per identified channel)::

        EDI.chan   1 channels identified of dimensionality 1
        Channel  0  4.89082  3.03868  4.89082

    Returns:
        ``dict`` with keys ``dimension``, ``included_diameter``,
        ``free_diameter``, ``included_along_free`` (taken from the first
        channel for backward compatibility), and ``channels`` which lists
        every parsed channel.

    Raises:
        ZeoppParsingError: When the format is invalid. No silent default
            results are returned (a real "no accessible channel" output
            with ``dimensionality 0`` and zero channel rows is still a
            valid result, not an error).
    """
    if not text or not text.strip():
        raise ZeoppParsingError(
            "CHAN output is empty",
            output_file="result.chan",
            raw_content=text,
        )

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        raise ZeoppParsingError(
            "CHAN output has no non-empty lines",
            output_file="result.chan",
            raw_content=text,
        )

    # Robust dimensionality extraction (supports multi-digit values and
    # arbitrary whitespace between the keyword and the integer).
    dim_match = re.search(r"dimensionality\s+(\d+)", lines[0])
    if dim_match is None:
        raise ZeoppParsingError(
            "Expected 'dimensionality <int>' phrase in first line of CHAN output",
            output_file="result.chan",
            raw_content=text,
        )
    dim = int(dim_match.group(1))

    channel_re = re.compile(
        r"^\s*Channel\s+(?P<id>\d+)\s+"
        r"(?P<di>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
        r"(?P<df>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s+"
        r"(?P<dif>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*$"
    )
    channels: List[Dict[str, float]] = []
    for line in lines[1:]:
        m = channel_re.match(line)
        if not m:
            continue
        channels.append(
            {
                "id": int(m.group("id")),
                "included_diameter": float(m.group("di")),
                "free_diameter": float(m.group("df")),
                "included_along_free": float(m.group("dif")),
            }
        )

    if dim > 0 and not channels:
        raise ZeoppParsingError(
            f"CHAN output declares dimensionality {dim} but no Channel rows were parsed",
            output_file="result.chan",
            raw_content=text,
        )

    if channels:
        first = channels[0]
        return {
            "dimension": dim,
            "included_diameter": first["included_diameter"],
            "free_diameter": first["free_diameter"],
            "included_along_free": first["included_along_free"],
            "channels": channels,
        }

    # dim == 0 with no Channel rows: no accessible channel — a real,
    # valid result rather than a parsing failure.
    return {
        "dimension": 0,
        "included_diameter": 0.0,
        "free_diameter": 0.0,
        "included_along_free": 0.0,
        "channels": [],
    }


def parse_sa_from_text(text: str) -> dict:
    """Parse Zeo++ ``-sa`` output (``.sa`` file) into a dict.

    Real Zeo++ output (single ``@``-line, plus optional appended lines
    in newer versions)::

        @ EDI.sa Unitcell_volume: 307.484 Density: 1.62239
        ASA_A^2: 60.7713 ASA_m^2/cm^3: 1976.4 ASA_m^2/g: 1218.21
        NASA_A^2: 0 NASA_m^2/cm^3: 0 NASA_m^2/g: 0
        Number_of_channels: 1 Channel_surface_area_A^2: 60.7713
        Number_of_pockets: 0
        Pocket_surface_area_A^2:

    Returns:
        ``dict`` with primary ASA/NASA metrics plus optional
        channel/pocket extension fields.

    Raises:
        ZeoppParsingError: When the ``@`` marker is missing or any of
            the primary ASA/NASA metrics cannot be parsed.
    """
    if "@" not in text:
        raise ZeoppParsingError(
            "SA output missing '@' header",
            output_file="result.sa",
            raw_content=text,
        )

    tokens = _all_tokens(text)
    kw = {"output_file": "result.sa", "raw_content": text}

    return {
        "asa_unitcell": _extract_value("ASA_A^2:", tokens, required=True, **kw),
        "asa_volume": _extract_value("ASA_m^2/cm^3:", tokens, required=True, **kw),
        "asa_mass": _extract_value("ASA_m^2/g:", tokens, required=True, **kw),
        "nasa_unitcell": _extract_value("NASA_A^2:", tokens, required=True, **kw),
        "nasa_volume": _extract_value("NASA_m^2/cm^3:", tokens, required=True, **kw),
        "nasa_mass": _extract_value("NASA_m^2/g:", tokens, required=True, **kw),
        "number_of_channels": _extract_int("Number_of_channels:", text),
        "channel_surface_area_a2": _collect_floats_after("Channel_surface_area_A^2:", text) or None,
        "number_of_pockets": _extract_int("Number_of_pockets:", text),
        "pocket_surface_area_a2": _collect_floats_after("Pocket_surface_area_A^2:", text) or None,
    }


def parse_volpo_from_text(text: str) -> dict:
    """Parse Zeo++ ``-volpo`` output (``.volpo`` file) into a dict.

    Real Zeo++ output::

        @ EDI.volpo Unitcell_volume: 307.484 Density: 1.62239
        POAV_A^3: 131.284 POAV_Volume_fraction: 0.42696 POAV_cm^3/g: 0.263168
        PONAV_A^3: 0 PONAV_Volume_fraction: 0 PONAV_cm^3/g: 0

    Newer versions may append per-channel/per-pocket volumes (using the
    same ``Channel_volume_A^3:`` / ``Pocket_volume_A^3:`` labels as
    ``-vol``); we expose them as optional extensions.

    Raises:
        ZeoppParsingError: When the ``@`` marker is missing or any of
            the primary POAV/PONAV metrics cannot be parsed.
    """
    if "@" not in text:
        raise ZeoppParsingError(
            "VOLPO output missing '@' header",
            output_file="result.volpo",
            raw_content=text,
        )

    tokens = _all_tokens(text)
    kw = {"output_file": "result.volpo", "raw_content": text}

    return {
        "poav_unitcell": _extract_value("POAV_A^3:", tokens, required=True, **kw),
        "poav_fraction": _extract_value("POAV_Volume_fraction:", tokens, required=True, **kw),
        "poav_mass": _extract_value("POAV_cm^3/g:", tokens, required=True, **kw),
        "ponav_unitcell": _extract_value("PONAV_A^3:", tokens, required=True, **kw),
        "ponav_fraction": _extract_value("PONAV_Volume_fraction:", tokens, required=True, **kw),
        "ponav_mass": _extract_value("PONAV_cm^3/g:", tokens, required=True, **kw),
        "number_of_channels": _extract_int("Number_of_channels:", text),
        "channel_volume_a3": _collect_floats_after("Channel_volume_A^3:", text) or None,
        "number_of_pockets": _extract_int("Number_of_pockets:", text),
        "pocket_volume_a3": _collect_floats_after("Pocket_volume_A^3:", text) or None,
    }


def parse_res_from_text(text: str) -> dict:
    """Parse ``.res`` file text to extract pore diameters.

    Expected format::

        EDI.res    4.89082 3.03868  4.81969

    Raises:
        ZeoppParsingError: If the output format is invalid.
    """
    tokens = text.strip().split()
    if len(tokens) < 4:
        raise ZeoppParsingError(
            f"Malformed .res file output. Expected at least 4 tokens, got {len(tokens)}",
            output_file="result.res",
            raw_content=text,
        )

    try:
        return {
            "included_diameter": float(tokens[1]),
            "free_diameter": float(tokens[2]),
            "included_along_free": float(tokens[3]),
        }
    except (ValueError, IndexError) as e:
        raise ZeoppParsingError(
            f"Failed to parse .res file values: {e}",
            output_file="result.res",
            raw_content=text,
        )


def parse_block_from_text(text: str) -> dict:
    """Parse ``.block`` summary output from Zeo++.

    Example lines::

        Identified 0 channels and 2 pockets
        139 nodes assigned to pores.

    Returns:
        ``dict`` with integer ``channels`` / ``pockets`` /
        ``nodes_assigned`` (zero-filled when only one of the two summary
        lines is present) plus the raw ``raw`` text.

    Raises:
        ZeoppParsingError: When neither summary line can be recognized.
    """
    raw = text.strip() if text else ""
    result: Dict[str, Any] = {
        "channels": None,
        "pockets": None,
        "nodes_assigned": None,
        "raw": raw,
    }

    ident_match = re.search(
        r"Identified\s+(\d+)\s+channels?\s+and\s+(\d+)\s+pockets?",
        raw,
    )
    if ident_match is not None:
        result["channels"] = int(ident_match.group(1))
        result["pockets"] = int(ident_match.group(2))

    nodes_match = re.search(r"(\d+)\s+nodes?\s+assigned\s+to\s+pores", raw)
    if nodes_match is not None:
        result["nodes_assigned"] = int(nodes_match.group(1))

    if (
        result["channels"] is None
        and result["pockets"] is None
        and result["nodes_assigned"] is None
    ):
        raise ZeoppParsingError(
            "BLOCK output did not contain any recognizable summary line "
            "('Identified N channels and M pockets' or 'N nodes assigned to pores')",
            output_file="result.block",
            raw_content=text,
        )

    # Backfill zeros for downstream consumers that expect ints when the
    # output was partial (e.g. only "nodes assigned" line was emitted).
    for key in ("channels", "pockets", "nodes_assigned"):
        if result[key] is None:
            result[key] = 0

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