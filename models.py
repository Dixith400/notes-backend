from pydantic import BaseModel


class UserCredentials(BaseModel):
    """Credentials shared by register and login requests."""

    email: str
    password: str


class NotePayload(BaseModel):
    """Client-provided note fields."""

    name: str
    content: str


# Backward-compatible aliases keep older imports working while the app moves
# toward readable class names.
user_registration = UserCredentials
user_login = UserCredentials
notes = NotePayload
