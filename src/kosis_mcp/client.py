from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import Settings


class KosisApiError(RuntimeError):
    """Raised when KOSIS OpenAPI cannot return usable data."""


@dataclass(frozen=True)
class KosisItem:
    org_id: str | None
    tbl_id: str | None
    object_id: str | None
    object_name: str | None
    object_name_en: str | None
    object_sequence: str | None
    item_id: str | None
    item_name: str | None
    item_name_en: str | None
    unit_id: str | None
    unit_name: str | None
    unit_name_en: str | None

    @classmethod
    def from_raw(cls, row: dict[str, Any]) -> "KosisItem":
        return cls(
            org_id=_as_optional_str(row.get("ORG_ID")),
            tbl_id=_as_optional_str(row.get("TBL_ID")),
            object_id=_as_optional_str(row.get("OBJ_ID")),
            object_name=_as_optional_str(row.get("OBJ_NM")),
            object_name_en=_as_optional_str(row.get("OBJ_NM_ENG")),
            object_sequence=_as_optional_str(row.get("OBJ_ID_SN")),
            item_id=_as_optional_str(row.get("ITM_ID")),
            item_name=_as_optional_str(row.get("ITM_NM")),
            item_name_en=_as_optional_str(row.get("ITM_NM_ENG")),
            unit_id=_as_optional_str(row.get("UNIT_ID")),
            unit_name=_as_optional_str(row.get("UNIT_NM")),
            unit_name_en=_as_optional_str(row.get("UNIT_ENG_NM")),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class KosisClient:
    def __init__(self, settings: Settings):
        self._settings = settings

    def get_item_metadata(
        self,
        *,
        org_id: str,
        tbl_id: str,
        api_key: str | None = None,
    ) -> dict[str, Any]:
        resolved_api_key = api_key or self._settings.api_key
        if not resolved_api_key:
            raise KosisApiError("KOSIS api key is required. Pass api_key or set KOSIS_API_KEY.")

        params = {
            "method": "getMeta",
            "type": "ITM",
            "apiKey": resolved_api_key,
            "orgId": org_id,
            "tblId": tbl_id,
        }
        url = f"{self._settings.base_url}/statisticsData.do?{urlencode(params)}"
        payload = self._get_json(url)
        rows = _extract_rows(payload)
        items = [KosisItem.from_raw(row).to_dict() for row in rows]

        return {
            "count": len(items),
            "items": items,
            "by_object": _group_by_object(items),
            "source": {
                "api": "statisticsData.do",
                "method": "getMeta",
                "type": "ITM",
                "org_id": org_id,
                "tbl_id": tbl_id,
            },
        }

    def _get_json(self, url: str) -> Any:
        request = Request(url, headers={"User-Agent": "kosis-mcp/0.1"})
        try:
            with urlopen(request, timeout=self._settings.timeout_seconds) as response:
                body = response.read().decode("utf-8-sig")
        except HTTPError as exc:
            raise KosisApiError(f"KOSIS HTTP error {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise KosisApiError(f"Could not connect to KOSIS: {exc.reason}") from exc
        except TimeoutError as exc:
            raise KosisApiError("KOSIS request timed out.") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            try:
                return json.loads(_normalize_javascript_object_array(body))
            except json.JSONDecodeError:
                raise KosisApiError("KOSIS returned a non-JSON response.") from exc


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]

    if isinstance(payload, dict):
        if "err" in payload:
            raise KosisApiError(str(payload["err"]))

        value = payload.get("value")
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]

        if "Count" in payload and int(payload.get("Count") or 0) == 0:
            return []

    raise KosisApiError("Unexpected KOSIS response shape.")


def _group_by_object(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in items:
        object_id = item.get("object_id") or "UNKNOWN"
        group = grouped.setdefault(
            object_id,
            {
                "object_id": object_id,
                "object_name": item.get("object_name"),
                "object_name_en": item.get("object_name_en"),
                "object_sequence": item.get("object_sequence"),
                "items": [],
            },
        )
        group["items"].append(item)
    return grouped


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _normalize_javascript_object_array(body: str) -> str:
    """KOSIS getMeta may return [{KEY:"value"}], not strict JSON."""

    return re.sub(r"([{,])\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", r'\1"\2":', body)
