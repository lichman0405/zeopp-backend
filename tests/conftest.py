# Pytest Fixtures and Configuration
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def client():
    """Synchronous test client for FastAPI."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Asynchronous test client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_cif_content():
    """Sample CIF file content for testing."""
    return """data_test_structure
_cell_length_a   10.0
_cell_length_b   10.0
_cell_length_c   10.0
_cell_angle_alpha   90.0
_cell_angle_beta    90.0
_cell_angle_gamma   90.0

loop_
_atom_site_label
_atom_site_type_symbol
_atom_site_fract_x
_atom_site_fract_y
_atom_site_fract_z
Si1 Si 0.0 0.0 0.0
O1 O 0.25 0.25 0.25
"""


@pytest.fixture
def sample_cssr_content():
    """Sample CSSR file content for testing."""
    return """                                   6.926  6.926  6.41
                   90   90  90   SPGR =  1 P 1         OPT = 1
15   0
0 EDI       : EDI
  1 O  0.189800  0.000000  0.355000  0  0  0  0  0  0  0  0  0.00
  2 O  0.000000  0.810200  0.645000  0  0  0  0  0  0  0  0  0.00
  3 Si  0.267900  0.000000  0.118400  0  0  0  0  0  0  0  0  0.00
"""


@pytest.fixture
def temp_cif_file(tmp_path, sample_cif_content):
    """Create a temporary CIF file for testing."""
    file_path = tmp_path / "test_structure.cif"
    file_path.write_text(sample_cif_content)
    return file_path


@pytest.fixture
def temp_cssr_file(tmp_path, sample_cssr_content):
    """Create a temporary CSSR file for testing."""
    file_path = tmp_path / "test_structure.cssr"
    file_path.write_text(sample_cssr_content)
    return file_path


# Sample Zeo++ output fixtures for parser testing

@pytest.fixture
def sample_res_output():
    """Sample .res file output from Zeo++."""
    return "test_structure.res    4.89082 3.03868  4.81969"


@pytest.fixture
def sample_sa_output():
    """Sample .sa file output from Zeo++."""
    return """@ test.sa Unitcell_volume: 307.484   Density: 1.62239   ASA_A^2: 60.7713 ASA_m^2/cm^3: 1976.4 ASA_m^2/g: 1218.21
NASA_A^2: 0 NASA_m^2/cm^3: 0 NASA_m^2/g: 0"""


@pytest.fixture
def sample_vol_output():
    """Sample .vol file output from Zeo++."""
    return """@ test.vol Unitcell_volume: 307.484   Density: 1.62239   AV_A^3: 22.6493 AV_Volume_fraction: 0.07366 AV_cm^3/g: 0.0454022
NAV_A^3: 0 NAV_Volume_fraction: 0 NAV_cm^3/g: 0"""


@pytest.fixture
def sample_volpo_output():
    """Sample .volpo file output from Zeo++."""
    return """@ test.volpo Unitcell_volume: 307.484   Density: 1.62239 POAV_A^3: 131.284 POAV_Volume_fraction: 0.42696 POAV_cm^3/g: 0.263168
PONAV_A^3: 0 PONAV_Volume_fraction: 0 PONAV_cm^3/g: 0"""


@pytest.fixture
def sample_chan_output():
    """Sample .chan file output from Zeo++."""
    return """test.chan   1 channels identified of dimensionality 1
Channel  0  4.89082  3.03868  4.89082"""


@pytest.fixture
def sample_block_output():
    """Sample .block file output from Zeo++."""
    return """Identified 0 channels and 2 pockets
139 nodes assigned to pores."""


@pytest.fixture
def sample_strinfo_output():
    """Sample .strinfo file output from Zeo++."""
    return "test.strinfo Si4O10 4 segments: 1 framework(s) (1D/2D/3D 0 0 1) and 0 molecule(s)"


@pytest.fixture
def sample_oms_output():
    """Sample .oms file output from Zeo++."""
    return """test.oms
Number of open metal sites: 4"""
