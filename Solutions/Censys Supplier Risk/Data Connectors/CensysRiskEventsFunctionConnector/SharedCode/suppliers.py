"""Supplier names and ids, kept in an Azure Storage Table so that supplier names can be used as an input."""
from typing import Dict, Iterable, List, Tuple

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient, UpdateMode

from . import consts
from .exceptions import CensysException
from .logger import applogger

_BATCH = 100  # entities per Table transaction, all in the same partition


def normalize(name: str) -> str:
    """Compare names without caring about case or extra spaces. Used at run time only, nothing normalized is stored."""
    return " ".join((name or "").split()).casefold()


def parse_names(raw: str) -> List[str]:
    """Split the SupplierNames setting on the separator, trim, and drop empty entries and duplicates (any case)."""
    names, seen = [], set()
    for part in (raw or "").replace("\n", consts.SUPPLIER_NAME_SEPARATOR).split(consts.SUPPLIER_NAME_SEPARATOR):
        name = " ".join(part.split())
        key = normalize(name)
        if key and key != "suppliernames" and key not in seen:
            seen.add(key)
            names.append(name)
    return names


def resolve(names: Iterable[str], suppliers: Iterable[Tuple[str, str]]) -> Tuple[List[str], List[str]]:
    """Return (supplier ids, names that matched no supplier). suppliers is a list of (supplier id, display name).

    A name can match several suppliers, and all their ids are returned. The ids keep the order of the names.
    """
    by_name: Dict[str, List[str]] = {}
    for supplier_id, display_name in suppliers:
        by_name.setdefault(normalize(display_name), []).append(supplier_id)
    ids, missing = [], []
    for name in names:
        found = by_name.get(normalize(name))
        if not found:
            missing.append(name)
            continue
        for supplier_id in sorted(found):
            if supplier_id not in ids:
                ids.append(supplier_id)
    return ids, missing


class SupplierStore:
    """Table with one row per supplier: partition = organization id, row = supplier id, DisplayName as returned."""

    def __init__(self, connection_string: str, table_name: str, organization_id: str):
        """Create the table client, creating the table when needed."""
        self.organization_id = organization_id
        try:
            service = TableServiceClient.from_connection_string(conn_str=connection_string)
            self.table = service.create_table_if_not_exists(table_name)
        except Exception as err:
            applogger.error(f"{consts.LOG_PREFIX} SupplierStore.__init__: error accessing suppliers table "
                            f"{table_name}: {err}")
            raise CensysException(f"Error accessing suppliers table {table_name}: {err}")

    def load(self) -> List[Tuple[str, str]]:
        """Return (supplier id, display name) of every stored supplier of the organization."""
        try:
            rows = self.table.query_entities(f"PartitionKey eq '{self.organization_id}'")
            return [(row["RowKey"], row.get("DisplayName") or "") for row in rows]
        except ResourceNotFoundError:
            return []
        except Exception as err:
            applogger.error(f"{consts.LOG_PREFIX} SupplierStore.load: error reading suppliers table: {err}")
            raise CensysException(f"Error reading suppliers table: {err}")

    def sync(self, pages: Iterable[List[dict]]) -> Tuple[int, int]:
        """Store every supplier of the pages, then remove the rows of suppliers that no longer exist in Censys.

        Returns (suppliers stored, rows removed). Rows are removed only after all pages were read and written,
        so a failed run never removes anything.
        """
        latest: Dict[str, str] = {}
        for page in pages:
            for supplier in page:
                if supplier.get("id"):
                    latest[supplier["id"]] = supplier.get("display_name") or ""
        try:
            self._write([("upsert", {"PartitionKey": self.organization_id, "RowKey": sid, "DisplayName": name},
                          {"mode": UpdateMode.REPLACE}) for sid, name in latest.items()])
            stale = [sid for sid, _ in self.load() if sid not in latest]
            self._write([("delete", {"PartitionKey": self.organization_id, "RowKey": sid}) for sid in stale])
        except CensysException:
            raise
        except Exception as err:
            applogger.error(f"{consts.LOG_PREFIX} SupplierStore.sync: error writing suppliers table: {err}")
            raise CensysException(f"Error writing suppliers table: {err}")
        return len(latest), len(stale)

    def _write(self, operations: list) -> None:
        """Send the operations to the table in transactions of at most 100 entities."""
        for start in range(0, len(operations), _BATCH):
            self.table.submit_transaction(operations[start:start + _BATCH])
