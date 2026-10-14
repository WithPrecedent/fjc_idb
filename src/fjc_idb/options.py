import pathlib


_ADD_AGENCIES_FROM_PARTIES: bool = True  # Whether to add agencies from APPPELLANT and APPELLEE columns when no AGENCY is present.
_CHANGE_COURT_TO_STRING: bool = True
_DATA_FOLDER: pathlib.Path = (
    pathlib.Path(__file__).parents[4] / "data" / "courts" / "fjc_idb"
)
_DATE_FORMAT: str = "%Y-%m-%d"
_ENCODING: str = "latin-1"
_MISSING_CODES: tuple[str | int, ...] = ("-8", -8)
_MISSING_DATE: str = "1900-01-01"
_PENDING_COLUMN: str = "TAPEYEAR"
_PENDING_YEAR: int = 2099
_RENAME_COLUMNS: bool = True
_SOURCE_PREFIXES: dict[str, str] = {
    "appellate": "ap",
    "civil": "cv",
    "criminal": "cr",
}
