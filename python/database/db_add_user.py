# These functions are stubs kept for reference.
# Profile CRUD is now handled by python/services/profiles.py (Phase 2).
# These could be repurposed or removed in a future cleanup phase.


def addUserIntoDatabaseByName(name: str):
    raise NotImplementedError(
        "Cannot create a cv_profile without an authenticated user. "
        "This function will be rewritten in Phase 2 once auth is in place."
    )


def addUserIntoDatabaseByFirstname(firstname: str):
    raise NotImplementedError("Not implemented yet — see Phase 2.")


def addUserIntoDatabaseByEmail(email: str):
    raise NotImplementedError("Not implemented yet — see Phase 2.")
