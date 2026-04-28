# Unit Tests for Zeo++ Output Parsers
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31

import pytest
from app.utils.parser import (
    _extract_value,
    parse_vol_from_text,
    parse_sa_from_text,
    parse_volpo_from_text,
    parse_res_from_text,
    parse_chan_from_text,
    parse_block_from_text,
    parse_strinfo_from_text,
    parse_oms_from_text,
)
from app.core.exceptions import ZeoppParsingError


class TestExtractValue:
    """Test cases for _extract_value helper function."""

    def test_extract_value_success(self):
        """Test successful value extraction."""
        tokens = ["Unitcell_volume:", "307.484", "Density:", "1.62239"]
        assert _extract_value("Unitcell_volume:", tokens) == 307.484
        assert _extract_value("Density:", tokens) == 1.62239

    def test_extract_value_key_not_found(self):
        """Test extraction when key is not in tokens."""
        tokens = ["Unitcell_volume:", "307.484"]
        result = _extract_value("NonExistent:", tokens)
        assert result == 0.0

    def test_extract_value_invalid_float(self):
        """Test extraction when value is not a valid float."""
        tokens = ["Unitcell_volume:", "invalid"]
        result = _extract_value("Unitcell_volume:", tokens)
        assert result == 0.0

    def test_extract_value_custom_default(self):
        """Test extraction with custom default value."""
        tokens = ["Unitcell_volume:", "307.484"]
        result = _extract_value("NonExistent:", tokens, default=-1.0)
        assert result == -1.0

    def test_extract_value_missing_value_after_key(self):
        """Test extraction when key exists but no value follows."""
        tokens = ["Unitcell_volume:"]
        result = _extract_value("Unitcell_volume:", tokens)
        assert result == 0.0


class TestParseVolFromText:
    """Test cases for parse_vol_from_text function."""

    def test_parse_vol_success(self, sample_vol_output):
        """Test successful parsing of .vol file content."""
        result = parse_vol_from_text(sample_vol_output)
        
        assert result["unitcell_volume"] == 307.484
        assert result["density"] == 1.62239
        assert result["av"]["unitcell"] == 22.6493
        assert result["av"]["fraction"] == 0.07366
        assert result["av"]["mass"] == 0.0454022
        assert result["nav"]["unitcell"] == 0
        assert result["nav"]["fraction"] == 0
        assert result["nav"]["mass"] == 0

    def test_parse_vol_incomplete_output(self):
        """Test parsing when the '@' header is missing entirely."""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_vol_from_text("Unitcell_volume: 307.484")
        assert "missing '@' header" in str(exc_info.value)

    def test_parse_vol_strict_missing_required(self):
        """Strict mode: raises when a required AV/NAV field is missing."""
        with pytest.raises(ZeoppParsingError):
            parse_vol_from_text("@ test.vol Unitcell_volume: 307.484 Density: 1.62239")

    def test_parse_vol_extension_fields(self, sample_vol_output_extended):
        """Optional channel/pocket extension fields are populated when present."""
        result = parse_vol_from_text(sample_vol_output_extended)
        assert result["number_of_channels"] == 1
        assert result["channel_volume_a3"] == [22.6493]
        assert result["number_of_pockets"] == 1
        assert result["pocket_volume_a3"] == [1.5]

    def test_parse_vol_empty_input(self):
        """Test parsing with empty input."""
        with pytest.raises(ZeoppParsingError):
            parse_vol_from_text("")


class TestParseSaFromText:
    """Test cases for parse_sa_from_text function."""

    def test_parse_sa_success(self, sample_sa_output):
        """Test successful parsing of .sa file content."""
        result = parse_sa_from_text(sample_sa_output)
        
        assert result["asa_unitcell"] == 60.7713
        assert result["asa_volume"] == 1976.4
        assert result["asa_mass"] == 1218.21
        assert result["nasa_unitcell"] == 0
        assert result["nasa_volume"] == 0
        assert result["nasa_mass"] == 0

    def test_parse_sa_incomplete_output(self):
        """Test parsing when '@' header is missing."""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_sa_from_text("ASA_A^2: 60.7713")
        assert "missing '@' header" in str(exc_info.value)

    def test_parse_sa_strict_missing_nasa(self):
        """Strict mode: raises when NASA_* required field is absent."""
        text = (
            "@ test.sa Unitcell_volume: 307.484 Density: 1.62239 "
            "ASA_A^2: 60.7713 ASA_m^2/cm^3: 1976.4 ASA_m^2/g: 1218.21\n"
        )
        with pytest.raises(ZeoppParsingError):
            parse_sa_from_text(text)

    def test_parse_sa_extension_fields(self, sample_sa_output_extended):
        """Optional channel/pocket extension fields are populated when present."""
        result = parse_sa_from_text(sample_sa_output_extended)
        assert result["nasa_unitcell"] == 12.34
        assert result["number_of_channels"] == 1
        assert result["channel_surface_area_a2"] == [60.7713]
        assert result["number_of_pockets"] == 2
        assert result["pocket_surface_area_a2"] == [7.5, 4.84]


class TestParseVolpoFromText:
    """Test cases for parse_volpo_from_text function."""

    def test_parse_volpo_success(self, sample_volpo_output):
        """Test successful parsing of .volpo file content."""
        result = parse_volpo_from_text(sample_volpo_output)
        
        assert result["poav_unitcell"] == 131.284
        assert result["poav_fraction"] == 0.42696
        assert result["poav_mass"] == 0.263168
        assert result["ponav_unitcell"] == 0
        assert result["ponav_fraction"] == 0
        assert result["ponav_mass"] == 0

    def test_parse_volpo_incomplete_output(self):
        """Test parsing when '@' header is missing."""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_volpo_from_text("POAV_A^3: 131.284")
        assert "missing '@' header" in str(exc_info.value)


class TestParseResFromText:
    """Test cases for parse_res_from_text function."""

    def test_parse_res_success(self, sample_res_output):
        """Test successful parsing of .res file content."""
        result = parse_res_from_text(sample_res_output)
        
        assert result["included_diameter"] == 4.89082
        assert result["free_diameter"] == 3.03868
        assert result["included_along_free"] == 4.81969

    def test_parse_res_insufficient_tokens(self):
        """Test parsing when output has fewer than 4 tokens."""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_res_from_text("test.res 4.89082")
        assert "Expected at least 4 tokens" in str(exc_info.value)

    def test_parse_res_invalid_values(self):
        """Test parsing when values are not valid floats."""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_res_from_text("test.res invalid 3.03868 4.81969")
        assert "Failed to parse .res file values" in str(exc_info.value)


class TestParseChanFromText:
    """Test cases for parse_chan_from_text function."""

    def test_parse_chan_success(self, sample_chan_output):
        """Test successful parsing of .chan file content."""
        result = parse_chan_from_text(sample_chan_output)
        
        assert result["dimension"] == 1
        assert result["included_diameter"] == 4.89082
        assert result["free_diameter"] == 3.03868
        assert result["included_along_free"] == 4.89082

    def test_parse_chan_empty_input(self):
        """Parsing empty input now raises rather than returning silent zeros."""
        with pytest.raises(ZeoppParsingError):
            parse_chan_from_text("")

    def test_parse_chan_single_line_no_channels(self):
        """dimensionality 0 with no Channel rows is a valid 'no channel' result."""
        result = parse_chan_from_text(
            "test.chan   0 channels identified of dimensionality 0"
        )
        assert result["dimension"] == 0
        assert result["included_diameter"] == 0.0
        assert result["channels"] == []

    def test_parse_chan_dim_positive_no_rows_raises(self):
        """dimensionality > 0 but no Channel rows is malformed -> raise."""
        with pytest.raises(ZeoppParsingError):
            parse_chan_from_text(
                "test.chan   1 channels identified of dimensionality 1"
            )

    def test_parse_chan_multi_digit_dimension(self):
        """Regression: multi-digit dimensionality must not be truncated."""
        text = (
            "test.chan  1 channels identified of dimensionality 10\n"
            "Channel  0  4.89082  3.03868  4.89082\n"
        )
        result = parse_chan_from_text(text)
        assert result["dimension"] == 10
        assert len(result["channels"]) == 1
        assert result["channels"][0]["id"] == 0

    def test_parse_chan_missing_dimensionality_keyword(self):
        """Test parsing when 'dimensionality' keyword is missing."""
        text = """test.chan   1 channels identified
Channel  0  4.89082  3.03868  4.89082"""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_chan_from_text(text)
        assert "dimensionality" in str(exc_info.value)


class TestParseBlockFromText:
    """Test cases for parse_block_from_text function."""

    def test_parse_block_success(self, sample_block_output):
        """Test successful parsing of .block file content."""
        result = parse_block_from_text(sample_block_output)
        
        assert result["channels"] == 0
        assert result["pockets"] == 2
        assert result["nodes_assigned"] == 139
        assert "Identified 0 channels" in result["raw"]

    def test_parse_block_empty_input(self):
        """Empty BLOCK output is now treated as an unrecognized format."""
        with pytest.raises(ZeoppParsingError):
            parse_block_from_text("")

    def test_parse_block_partial_info(self):
        """Test parsing with only partial information."""
        text = "Identified 5 channels and 3 pockets"
        result = parse_block_from_text(text)
        
        assert result["channels"] == 5
        assert result["pockets"] == 3
        assert result["nodes_assigned"] == 0

    def test_parse_block_no_channels_pockets(self):
        """Test parsing with nodes info only."""
        text = "42 nodes assigned to pores."
        result = parse_block_from_text(text)
        
        assert result["channels"] == 0
        assert result["pockets"] == 0
        assert result["nodes_assigned"] == 42


class TestParseStrinfoFromText:
    """Test cases for parse_strinfo_from_text function."""

    def test_parse_strinfo_success(self, sample_strinfo_output):
        """Test successful parsing of .strinfo file content."""
        result = parse_strinfo_from_text(sample_strinfo_output)
        
        assert result["filename"] == "test.strinfo"
        assert result["formula"] == "Si4O10"
        assert result["segments"] == 4
        assert result["number_of_frameworks"] == 1
        assert result["number_of_molecules"] == 0
        assert len(result["frameworks"]) == 1
        assert result["frameworks"][0]["dimensionality"] == 3

    def test_parse_strinfo_multiple_frameworks(self):
        """Test parsing with multiple frameworks of different dimensions."""
        text = "test.strinfo Si4O10 6 segments: 3 framework(s) (1D/2D/3D 1 1 1) and 2 molecule(s)"
        result = parse_strinfo_from_text(text)
        
        assert result["number_of_frameworks"] == 3
        assert result["number_of_molecules"] == 2
        assert len(result["frameworks"]) == 3
        # Should have one 3D, one 2D, one 1D framework
        dims = [f["dimensionality"] for f in result["frameworks"]]
        assert sorted(dims) == [1, 2, 3]

    def test_parse_strinfo_invalid_format(self):
        """Test parsing with invalid format."""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_strinfo_from_text("invalid format string")
        assert "format was not recognized" in str(exc_info.value)


class TestParseOmsFromText:
    """Test cases for parse_oms_from_text function."""

    def test_parse_oms_success(self, sample_oms_output):
        """Test successful parsing of .oms file content."""
        result = parse_oms_from_text(sample_oms_output)
        
        assert result["open_metal_sites_count"] == 4

    def test_parse_oms_zero_sites(self):
        """Test parsing when no open metal sites found."""
        text = """test.oms
Number of open metal sites: 0"""
        result = parse_oms_from_text(text)
        
        assert result["open_metal_sites_count"] == 0

    def test_parse_oms_missing_line(self):
        """Test parsing when 'Number of open metal sites' line is missing."""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_oms_from_text("test.oms\nSome other content")
        assert "Could not find" in str(exc_info.value)

    def test_parse_oms_invalid_count(self):
        """Test parsing when count is not a valid integer."""
        text = """test.oms
Number of open metal sites: invalid"""
        with pytest.raises(ZeoppParsingError) as exc_info:
            parse_oms_from_text(text)
        assert "Failed to parse OMS count" in str(exc_info.value)


class TestParserEdgeCases:
    """Test edge cases and unusual inputs across all parsers."""

    def test_unicode_in_input(self):
        """Test handling of Unicode characters in input."""
        text = """@ tëst.vol Unitcell_volume: 307.484   Density: 1.62239   AV_A^3: 22.6493 AV_Volume_fraction: 0.07366 AV_cm^3/g: 0.0454022
NAV_A^3: 0 NAV_Volume_fraction: 0 NAV_cm^3/g: 0"""
        result = parse_vol_from_text(text)
        assert result["unitcell_volume"] == 307.484

    def test_extra_whitespace(self):
        """Test handling of extra whitespace in input."""
        text = "test.res    4.89082   3.03868    4.81969   "
        result = parse_res_from_text(text)
        assert result["included_diameter"] == 4.89082

    def test_scientific_notation(self):
        """Test handling of scientific notation in values."""
        tokens = ["Unitcell_volume:", "3.07484e2"]
        result = _extract_value("Unitcell_volume:", tokens)
        assert abs(result - 307.484) < 0.001

    def test_negative_values(self):
        """Test handling of negative values (though unusual for Zeo++)."""
        text = "test.res -4.89082 -3.03868 -4.81969"
        result = parse_res_from_text(text)
        assert result["included_diameter"] == -4.89082
        assert result["free_diameter"] == -3.03868

    def test_very_large_values(self):
        """Test handling of very large float values."""
        tokens = ["Unitcell_volume:", "999999999.999"]
        result = _extract_value("Unitcell_volume:", tokens)
        assert result == 999999999.999

    def test_very_small_values(self):
        """Test handling of very small float values."""
        tokens = ["Unitcell_volume:", "0.000000001"]
        result = _extract_value("Unitcell_volume:", tokens)
        assert result == 0.000000001
