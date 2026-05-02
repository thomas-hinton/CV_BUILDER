from fastapi import APIRouter

from python.database.db_add_user import addUserIntoDatabaseByName
from python.database.db_get_user import getUserFromDatabaseByName
from python.schemas.profiles import ModifyNameRequest

router = APIRouter(tags=["profiles"])


# TODO (Phase 2): Replace these temporary endpoints with proper RESTful CRUD.
# These are kept as stubs during the Phase 0 cleanup only.

@router.post("/modify_name")
def modify_name(payload: ModifyNameRequest):
    print(f"Modifying name to {payload.name}")
    return addUserIntoDatabaseByName(payload.name)


@router.get("/get_user_by_name")
def get_user_by_name(name: str):
    print(f"Getting user by name {name}")
    return getUserFromDatabaseByName(name)
