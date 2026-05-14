from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .client import KosisApiError, KosisClient
from .config import load_settings

mcp = FastMCP("kosis-mcp")


@mcp.tool()
def get_kosis_item_metadata(
    org_id: str = "101",
    tbl_id: str = "DT_1DA7001",
    api_key: str | None = None,
) -> dict[str, Any]:
    """Get item metadata for a KOSIS statistics table."""

    client = KosisClient(load_settings())
    try:
        return client.get_item_metadata(org_id=org_id, tbl_id=tbl_id, api_key=api_key)
    except KosisApiError as exc:
        return {
            "error": {
                "type": "KosisApiError",
                "message": str(exc),
            }
        }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

