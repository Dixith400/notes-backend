from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.responses import RedirectResponse

from config import settings
from database import database
from repositories.user_repository import UserRepository
from services.auth_service import token_service


class GoogleOAuthService:
    """Keeps Google OAuth setup and callback handling outside route functions."""

    def __init__(self):
        self.oauth = OAuth(Config(".env"))
        self.users = UserRepository(database.db)
        self.oauth.register(
            name="google",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    async def start_login(self, request):
        redirect_uri = settings.backend_url + "/auth/google/callback"
        return await self.oauth.google.authorize_redirect(request, redirect_uri)

    async def finish_login(self, request):
        token = await self.oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        email = user_info["email"]

        existing_user = await self.users.find_by_email(email)
        if not existing_user:
            await self.users.create(email, None)

        jwt_token = token_service.create(email)
        return RedirectResponse(f"{settings.frontend_url}/notes?token={jwt_token}")


google_oauth_service = GoogleOAuthService()
