from __future__ import annotations

from typing import Any, Dict, List, Optional

from models.asset import Asset, AssetDependency, AssetVersion
from storage.db import DatabaseManager


class AssetService:
    """
    Asset lifecycle service:
    - create asset
    - create version
    - add dependency
    - validate upstream dependency existence
    """

    VALID_ASSET_STATUSES = {
        "draft",
        "reviewed",
        "approved",
        "rejected",
        "deprecated",
    }

    INVALID_UPSTREAM_STATUSES = {
        "rejected",
        "deprecated",
    }

    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def create_asset(
        self,
        task_id: str,
        asset_type: str,
        status: str = "draft",
    ) -> Asset:
        if status not in self.VALID_ASSET_STATUSES:
            raise ValueError(f"Invalid asset status: {status}")

        asset = Asset(
            task_id=task_id,
            asset_type=asset_type,
            status=status,
        )
        self.db.save_asset(asset)
        return asset

    def create_asset_version(
        self,
        asset_id: str,
        version: int,
        data: Dict[str, Any],
        created_by: str,
    ) -> AssetVersion:
        asset_row = self.db.fetch_one(
            "SELECT * FROM assets WHERE asset_id = ?",
            (asset_id,),
        )
        if asset_row is None:
            raise ValueError(f"Asset not found: {asset_id}")

        version_row = self.db.fetch_one(
            "SELECT * FROM asset_versions WHERE asset_id = ? AND version = ?",
            (asset_id, version),
        )
        if version_row is not None:
            raise ValueError(f"Asset version already exists: {asset_id} v{version}")

        asset_version = AssetVersion(
            asset_id=asset_id,
            version=version,
            data=data,
            created_by=created_by,
        )
        self.db.save_asset_version(asset_version)

        # 同步更新 assets.current_version
        self.db.conn.execute(
            """
            UPDATE assets
            SET current_version = ?
            WHERE asset_id = ?
            """,
            (version, asset_id),
        )
        self.db.conn.commit()

        return asset_version

    def add_dependency(
        self,
        asset_id: str,
        depends_on: str,
        relation_type: str = "derived_from",
    ) -> AssetDependency:
        current_asset = self.db.fetch_one(
            "SELECT * FROM assets WHERE asset_id = ?",
            (asset_id,),
        )
        upstream_asset = self.db.fetch_one(
            "SELECT * FROM assets WHERE asset_id = ?",
            (depends_on,),
        )

        if current_asset is None:
            raise ValueError(f"Current asset not found: {asset_id}")

        if upstream_asset is None:
            raise ValueError(f"Upstream asset not found: {depends_on}")

        upstream_status = upstream_asset["status"]
        if upstream_status in self.INVALID_UPSTREAM_STATUSES:
            raise ValueError(
                f"Invalid upstream asset status for dependency: {depends_on} ({upstream_status})"
            )

        dependency = AssetDependency(
            asset_id=asset_id,
            depends_on=depends_on,
            relation_type=relation_type,
        )
        self.db.save_asset_dependency(dependency)
        return dependency

    def update_asset_status(
        self,
        asset_id: str,
        new_status: str,
    ) -> None:
        if new_status not in self.VALID_ASSET_STATUSES:
            raise ValueError(f"Invalid asset status: {new_status}")

        asset_row = self.db.fetch_one(
            "SELECT * FROM assets WHERE asset_id = ?",
            (asset_id,),
        )
        if asset_row is None:
            raise ValueError(f"Asset not found: {asset_id}")

        self.db.conn.execute(
            """
            UPDATE assets
            SET status = ?
            WHERE asset_id = ?
            """,
            (new_status, asset_id),
        )
        self.db.conn.commit()

    def get_asset(self, asset_id: str) -> Optional[dict]:
        row = self.db.fetch_one(
            "SELECT * FROM assets WHERE asset_id = ?",
            (asset_id,),
        )
        return dict(row) if row else None

    def get_asset_versions(self, asset_id: str) -> List[dict]:
        rows = self.db.fetch_all(
            """
            SELECT * FROM asset_versions
            WHERE asset_id = ?
            ORDER BY version ASC
            """,
            (asset_id,),
        )
        return [dict(r) for r in rows]

    def get_task_assets(self, task_id: str) -> List[dict]:
        rows = self.db.fetch_all(
            """
            SELECT * FROM assets
            WHERE task_id = ?
            ORDER BY created_at ASC
            """,
            (task_id,),
        )
        return [dict(r) for r in rows]

    def get_dependencies(self, asset_id: str) -> List[dict]:
        rows = self.db.fetch_all(
            """
            SELECT * FROM asset_dependencies
            WHERE asset_id = ?
            ORDER BY created_at ASC
            """,
            (asset_id,),
        )
        return [dict(r) for r in rows]
