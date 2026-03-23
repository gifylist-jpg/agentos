from pathlib import Path

from services.asset_service import AssetService
from storage.db import DatabaseManager


TEST_DB_PATH = Path("runtime/state/test_asset_service.db")


def setup_db() -> DatabaseManager:
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    db = DatabaseManager(TEST_DB_PATH)
    db.initialize()
    return db


def test_create_asset_and_version() -> None:
    db = setup_db()
    asset_service = AssetService(db)

    asset = asset_service.create_asset(
        task_id="task_asset_001",
        asset_type="script",
        status="draft",
    )
    assert asset.asset_type == "script"

    version_1 = asset_service.create_asset_version(
        asset_id=asset.asset_id,
        version=1,
        data={"text": "script v1"},
        created_by="worker_script",
    )
    assert version_1.version == 1

    version_2 = asset_service.create_asset_version(
        asset_id=asset.asset_id,
        version=2,
        data={"text": "script v2"},
        created_by="worker_script",
    )
    assert version_2.version == 2

    asset_row = asset_service.get_asset(asset.asset_id)
    assert asset_row is not None
    assert asset_row["current_version"] == 2

    versions = asset_service.get_asset_versions(asset.asset_id)
    assert len(versions) == 2

    print("Create asset and versions test passed.")
    db.close()


def test_dependency_creation() -> None:
    db = setup_db()
    asset_service = AssetService(db)

    script_asset = asset_service.create_asset(
        task_id="task_asset_002",
        asset_type="script",
        status="approved",
    )
    clip_asset = asset_service.create_asset(
        task_id="task_asset_002",
        asset_type="clip",
        status="draft",
    )

    dependency = asset_service.add_dependency(
        asset_id=clip_asset.asset_id,
        depends_on=script_asset.asset_id,
        relation_type="derived_from",
    )
    assert dependency.relation_type == "derived_from"

    dependencies = asset_service.get_dependencies(clip_asset.asset_id)
    assert len(dependencies) == 1

    print("Dependency creation test passed.")
    db.close()


def test_invalid_upstream_dependency_blocked() -> None:
    db = setup_db()
    asset_service = AssetService(db)

    rejected_script = asset_service.create_asset(
        task_id="task_asset_003",
        asset_type="script",
        status="rejected",
    )
    clip_asset = asset_service.create_asset(
        task_id="task_asset_003",
        asset_type="clip",
        status="draft",
    )

    try:
        asset_service.add_dependency(
            asset_id=clip_asset.asset_id,
            depends_on=rejected_script.asset_id,
            relation_type="derived_from",
        )
    except ValueError as exc:
        print("Invalid upstream dependency blocked:", exc)
    else:
        raise AssertionError("Rejected upstream dependency was not blocked")

    db.close()


def test_update_asset_status() -> None:
    db = setup_db()
    asset_service = AssetService(db)

    asset = asset_service.create_asset(
        task_id="task_asset_004",
        asset_type="video",
        status="draft",
    )
    asset_service.update_asset_status(asset.asset_id, "approved")

    updated = asset_service.get_asset(asset.asset_id)
    assert updated is not None
    assert updated["status"] == "approved"

    print("Update asset status test passed.")
    db.close()


if __name__ == "__main__":
    test_create_asset_and_version()
    test_dependency_creation()
    test_invalid_upstream_dependency_blocked()
    test_update_asset_status()
    print("\nAll asset service tests passed.")
