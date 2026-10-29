#!/usr/bin/env python3
"""
Kryptic-Agent: Compliance Asset Integrity Validation Suite
"""

import pytest
import os
import json
from generate_llc12_manifest import EntityManifestGenerator

@pytest.fixture
def manifest_engine():
    return EntityManifestGenerator(
        business_name="Krypticsoundz LLC",
        location="Dinuba, California"
    )

def test_manifest_schema_parameters(manifest_engine):
    """Confirm the corporate blueprint correctly maps necessary grant alignment fields."""
    blueprint = manifest_engine.assemble_corporate_blueprint()
    
    assert blueprint["entity_legal_name"] == "Krypticsoundz LLC"
    assert "Dinuba" in blueprint["primary_location"]
    assert blueprint["manifest_metadata"]["sam_purpose_of_registration"] == "ALL_AWARDS"
    assert "541" in blueprint["naics_industry_classification"]

def test_manifest_file_writing_boundary(manifest_engine):
    """Verify that file exports output clean, readable JSON records."""
    test_filename = "test_llc12_output.json"
    
    try:
        exported_path = manifest_engine.export_manifest_asset(filename=test_filename)
        assert os.path.exists(exported_path)
        
        with open(exported_path, "r") as f:
            parsed_data = json.load(f)
            
        assert parsed_data["entity_legal_name"] == "Krypticsoundz LLC"
        assert parsed_data["governance_structure"]["member_type"] == "Manager-Managed"
    finally:
        if os.path.exists(test_filename):
            os.remove(test_filename)
            
