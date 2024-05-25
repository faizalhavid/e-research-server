from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

@database_sync_to_async
def get_user(token):
    try:
        token = RefreshToken(token)
        return token.user
    except (InvalidToken, TokenError):
        return None
    
class TokenAuthMiddleware:
    def __init__(self, inner):
        super().__init__()

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split(
                "&")))).get('token', None)
        except ValueError:
            token_key = None

        if token_key:
            scope['user'] = await get_user(token_key)
        return await self.inner(scope, receive, send)
    