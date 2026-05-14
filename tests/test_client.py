from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kosis_mcp.client import KosisClient, _normalize_javascript_object_array
from kosis_mcp.config import Settings


class KosisClientTest(unittest.TestCase):
    def test_get_item_metadata_groups_items(self):
        payload = {
            "value": [
                {
                    "OBJ_ID": "ITEM",
                    "TBL_ID": "DT_1DA7001",
                    "UNIT_ID": "14STD06156",
                    "ORG_ID": "101",
                    "OBJ_NM": "항목",
                    "ITM_NM_ENG": "Pop. 15 years old and over",
                    "ITM_NM": "15세이상인구",
                    "UNIT_ENG_NM": "Thousand Person",
                    "ITM_ID": "T10",
                    "UNIT_NM": "천명",
                    "OBJ_NM_ENG": "Item code list",
                },
                {
                    "OBJ_ID": "B",
                    "TBL_ID": "DT_1DA7001",
                    "ORG_ID": "101",
                    "OBJ_NM": "성별",
                    "ITM_NM_ENG": "Total",
                    "ITM_NM": "계",
                    "OBJ_ID_SN": "1",
                    "ITM_ID": "0",
                    "OBJ_NM_ENG": "By gender",
                },
            ],
            "Count": 2,
        }
        client = KosisClient(Settings(api_key="test-key"))

        with patch.object(client, "_get_json", return_value=payload):
            result = client.get_item_metadata(org_id="101", tbl_id="DT_1DA7001")

        self.assertEqual(result["count"], 2)
        self.assertEqual(result["items"][0]["item_id"], "T10")
        self.assertEqual(result["items"][0]["unit_name"], "천명")
        self.assertEqual(result["by_object"]["ITEM"]["object_name"], "항목")
        self.assertEqual(result["by_object"]["B"]["items"][0]["item_name"], "계")

    def test_normalize_javascript_object_array(self):
        body = '[{OBJ_ID:"ITEM",TBL_ID:"DT_1DA7001",ITM_ID:"T10",ITM_NM:"15세이상인구"}]'

        parsed = json.loads(_normalize_javascript_object_array(body))

        self.assertEqual(parsed[0]["OBJ_ID"], "ITEM")
        self.assertEqual(parsed[0]["ITM_NM"], "15세이상인구")


if __name__ == "__main__":
    unittest.main()
