"""Tests for fjc_idb."""

from __future__ import annotations

import pandas as pd
import pytest

from fjc_idb import base, options
from fjc_idb.main import (
    _drop_stale_pending,
    export_data,
    import_data,
    parse_data,
)


def _raw_appellate() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "CIRCUIT": [9.0, 0.0],
            "DOCKET": ["0801434", "1910001"],
            "DKTDATE": pd.to_datetime(["2008-05-02", "2019-01-15"]),
            "AGENCY": ["-9", "XYZ"],
            "NOS": [510.0, -9.0],
            "DCIRC": [9.0, -8.0],
            "DDIST": ["73", "-8"],
            "JUDGDATE": pd.to_datetime(["2008-05-30", "1900-01-01"]),
            "TAPEYEAR": [2008.0, 2099.0],
        }
    )


def test_parse_docket_number() -> None:
    assert base.parse_docket_number("0801434") == "08-1434"
    assert base.parse_docket_number("1910001") == "19-10001"
    with pytest.raises(ValueError):
        base.parse_docket_number("-8")


def test_parse_data() -> None:
    data = parse_data(_raw_appellate(), "appellate", rename_columns=True)
    assert data["circuit"].tolist() == ["Ninth Circuit", "D.C. Circuit"]
    assert data["docket_num_idb"].tolist() == ["0801434", "1910001"]
    assert data["docket_number"].tolist() == ["08-1434", "19-10001"]
    assert data["district_of_origin"][0] == "Central District of California"
    assert data["agency"][1] == "XYZ"
    assert data["nature_of_suit"][0] == 510
    assert data["data_file_year"].tolist() == [2008, 2099]
    for column in ("agency", "nature_of_suit", "district_of_origin"):
        assert data[column].isna().sum() == 1
    assert pd.isna(data["judgment_date"][1])
    assert (
        parse_data(_raw_appellate(), "appellate", False).columns[0] == "CIRCUIT"
    )


def test_drop_stale_pending() -> None:
    raw = _raw_appellate()
    earlier, latest = _drop_stale_pending([raw, raw])
    assert earlier["TAPEYEAR"].tolist() == [2008.0]
    assert len(latest) == 2


def test_export_data(tmp_path) -> None:
    data = parse_data(_raw_appellate(), "appellate")
    export_data(data, tmp_path, "test.csv", {"judgment_date": "NA"})
    exported = pd.read_csv(
        tmp_path / "test.csv", dtype=str, keep_default_na=False
    )
    assert exported["judgment_date"].tolist() == ["2008-05-30", "NA"]
    assert exported["docket_date"].tolist() == ["2008-05-02", "2019-01-15"]
    assert exported["agency"].tolist() == ["", "XYZ"]


def test_import_data() -> None:
    data_folder = options._DATA_FOLDER / "appellate"
    if not any(data_folder.glob("ap08*.sas7bdat")):
        pytest.skip("FJC IDB appellate data is not available.")
    data = import_data("appellate", 2008, 2008, data_folder)
    assert not data.empty
    assert set(data["TAPEYEAR"]) == {2008}
    assert isinstance(data["DOCKET"][0], str)
    with pytest.raises(FileNotFoundError):
        import_data("appellate", 1901, 1901, data_folder)


if __name__ == "__main__":
    test_import_data()
