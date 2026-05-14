# KOSIS MCP

KOSIS OpenAPI를 MCP tool로 감싼 테스트 프로젝트입니다.

현재 구현 범위는 통계표의 항목/분류 항목 메타데이터 조회입니다.

## Tool

### `get_kosis_item_metadata`

KOSIS `statisticsData.do?method=getMeta&type=ITM` API를 호출합니다.

입력:

- `org_id`: 기관 ID, 기본값 `101`
- `tbl_id`: 통계표 ID, 기본값 `DT_1DA7001`
- `api_key`: 선택값. 없으면 환경변수 `KOSIS_API_KEY` 사용

반환:

- `count`: 전체 항목 수
- `items`: KOSIS 원본 필드를 snake_case로 정리한 목록
- `by_object`: `OBJ_ID` 기준 그룹핑 결과
- `source`: 호출한 API 정보

## 실행

```powershell
$env:KOSIS_API_KEY="..."
python -m kosis_mcp.server
```

또는 MCP 클라이언트 설정에서 command를 `kosis-mcp`로 지정합니다.

## 예시 요청

```text
KOSIS orgId=101, tblId=DT_1DA7001의 항목 정보를 조회해줘.
```

## 다른 사람에게 배포하기

### GitHub 저장소로 배포

가장 간단한 방식입니다.

```powershell
git clone <repository-url>
cd kosis-mcp
python -m pip install -e .
setx KOSIS_API_KEY "발급받은_KOSIS_API_KEY"
```

MCP 클라이언트 설정 예:

```json
{
  "mcpServers": {
    "kosis": {
      "command": "python",
      "args": ["-m", "kosis_mcp.server"]
    }
  }
}
```

### wheel 파일로 배포

배포 파일 생성:

```powershell
python -m pip install build
python -m build
```

생성 결과:

```text
dist/kosis_mcp-0.1.0-py3-none-any.whl
dist/kosis_mcp-0.1.0.tar.gz
```

받는 사람 설치:

```powershell
python -m pip install .\dist\kosis_mcp-0.1.0-py3-none-any.whl
setx KOSIS_API_KEY "발급받은_KOSIS_API_KEY"
```

설치 확인:

```powershell
python -c "import kosis_mcp.server; print('server import ok')"
```

