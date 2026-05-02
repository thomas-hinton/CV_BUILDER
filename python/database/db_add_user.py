import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "db.db"


# TODO (Phase 2): Replace these stubs with proper CRUD functions that receive
# an authenticated user_id from the auth layer (Phase 1).
# A cv_profile cannot be created without a parent user in the users table.
# The old implementation was inserting cv_profiles with id_user_mail = "",
# which violates the foreign key constraint and corrupts the database silently.


def addUserIntoDatabaseByName(name: str):
    raise NotImplementedError(
        "Cannot create a cv_profile without an authenticated user. "
        "This function will be rewritten in Phase 2 once auth is in place."
    )


def addUserIntoDatabaseByFirstname(firstname: str):
    raise NotImplementedError("Not implemented yet — see Phase 2.")


def addUserIntoDatabaseByEmail(email: str):
    raise NotImplementedError("Not implemented yet — see Phase 2.")
