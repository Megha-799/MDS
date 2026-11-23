import os

print("[Dev API Auth Patch] Bypassing auth with Maker-Checker support...")
filepath = "/usr/local/lib/python3.12/site-packages/iam_core/user_auth/middleware/validate_and_refresh.py"
if os.path.exists(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    # Reset old dispatch if present
    if "_old_dispatch" in content:
        # replace the dispatch block
        import re
        content = re.sub(
            r'async def dispatch\(self, request: Request, call_next\):.*?async def _old_dispatch',
            r'''async def dispatch(self, request: Request, call_next):
        from iam_core.schemas import AuthPrincipal
        dev_user = request.headers.get("x-dev-user", "admin")
        if dev_user == "checker":
            setattr(request.state, self._state_key, AuthPrincipal(credentials="dev-token", name="checker", sub="checker-sub", client_roles={"master-data": ["MASTER_DATA_ADMIN"]}))
        else:
            setattr(request.state, self._state_key, AuthPrincipal(credentials="dev-token", name="admin", sub="admin-sub", client_roles={"master-data": ["MASTER_DATA_ADMIN"]}))
        return await call_next(request)
    async def _old_dispatch''',
            content,
            flags=re.DOTALL
        )
        with open(filepath, "w") as f:
            f.write(content)
        print("[Dev API Auth Patch] Updated validate_and_refresh.py with user switcher")

filepath2 = "/usr/local/lib/python3.12/site-packages/iam_core/user_auth/middleware/resolve_permissions.py"
if os.path.exists(filepath2):
    with open(filepath2, "r") as f:
        content = f.read()
    target = 'async def dispatch(self, request: Request, call_next):'
    replacement = '''async def dispatch(self, request: Request, call_next):
        return await call_next(request)
    async def _old_dispatch(self, request: Request, call_next):'''
    if target in content and "_old_dispatch" not in content:
        content = content.replace(target, replacement, 1)
        with open(filepath2, "w") as f:
            f.write(content)
        print("[Dev API Auth Patch] Successfully patched resolve_permissions.py")

filepath3 = "/usr/local/lib/python3.12/site-packages/iam_core/user_auth/middleware/csrf.py"
if os.path.exists(filepath3):
    with open(filepath3, "r") as f:
        content = f.read()
    target = 'async def dispatch(self, request: Request, call_next):'
    replacement = '''async def dispatch(self, request: Request, call_next):
        return await call_next(request)
    async def _old_dispatch(self, request: Request, call_next):'''
    if target in content and "_old_dispatch" not in content:
        content = content.replace(target, replacement, 1)
        with open(filepath3, "w") as f:
            f.write(content)
        print("[Dev API Auth Patch] Successfully patched csrf.py")

print("[Dev API Auth Patch] Done!")
