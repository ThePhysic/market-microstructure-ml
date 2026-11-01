from copy import deepcopy
from pathlib import Path

import pytest

from market_microstructure.extension.config import load_config, protocol_identity, validate_config
from market_microstructure.extension.provenance import register_evaluation


@pytest.fixture
def config():
    return load_config(Path(__file__).resolve().parents[1] / "configs/research-extension.json")


@pytest.mark.parametrize("mutation", [
    lambda c: c["research"].update(practical_delta=float("nan")),
    lambda c: c["research"].update(inference_delay_us=1),
    lambda c: c["simulation"].update(max_position="NaN"),
    lambda c: c["data"].update(max_total_compressed_bytes=2**40),
    lambda c: c["market"].update(instrument_type="inverse_perpetual"),
    lambda c: c["publication"].update(signals=True),
    lambda c: c["publication"].update(signals=0),
    lambda c: c["research"]["final_dates"].reverse(),
    lambda c: c["scenarios"].append(deepcopy(c["scenarios"][0])),
])
def test_invalid_research_execution_or_distribution_contract_fails(config, mutation):
    mutation(config)
    with pytest.raises(ValueError):
        validate_config(config)


def test_authorization_changes_do_not_change_scientific_identity_but_fees_do(config):
    original = protocol_identity(config)
    config["research"].update(stage="final", final_scoring_authorized=True)
    assert protocol_identity(config) == original
    config["scenarios"][0]["fee_bps"] = "1"
    assert protocol_identity(config) != original


def test_registry_blocks_changed_contract_and_requires_explicit_reproduction(tmp_path):
    freeze = {"final_dates": ["2023-01-01"], "protocol_identity": "p", "dataset_identity": "d", "source_identity": "s"}
    assert register_evaluation(freeze, root=tmp_path)["execution_count"] == 1
    with pytest.raises(ValueError, match="reproduce"):
        register_evaluation(freeze, root=tmp_path)
    assert register_evaluation(freeze, root=tmp_path, reproduction=True)["execution_count"] == 2
    freeze["source_identity"] = "changed"
    with pytest.raises(ValueError, match="different scientific"):
        register_evaluation(freeze, root=tmp_path, reproduction=True)
