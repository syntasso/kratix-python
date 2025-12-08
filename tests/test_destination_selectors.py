from pathlib import Path

import yaml

import kratix_sdk as ks


def test_destination_selectors_read_write(tmp_path):
    assets_dir = Path(__file__).parent / "assets"
    asset_file = assets_dir / "destination-selectors.yaml"
    assert asset_file.exists(), f"Missing test asset: {asset_file}"

    ks.set_metadata_dir(assets_dir)
    sdk = ks.KratixSDK()

    selectors = sdk.read_destination_selectors()
    assert selectors[0].directory == "prod"
    assert selectors[0].match_labels == {"team": "team-billing"}
    assert selectors[1].directory == "dev"
    assert selectors[1].match_labels == {"env": "dev", "type": "terraform"}

    # Write to a temp METADATA_DIR and compare to the asset
    out_meta = tmp_path / "metadata"
    out_meta.mkdir(parents=True, exist_ok=True)
    ks.set_metadata_dir(out_meta)

    expected = yaml.safe_load(asset_file.read_text())
    sdk.write_destination_selectors(selectors)

    written = yaml.safe_load((out_meta / "destination-selectors.yaml").read_text())
    assert written == expected
