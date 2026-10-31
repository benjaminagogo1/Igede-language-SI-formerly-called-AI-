"""Type stubs for Flask-Login 0.6.3.

This local ``pyi`` mirrors the installed package's public types so static
analysers (mypy / pyright) can resolve imports of ``flask_login`` without relying
on the shared typeshed checkout (pip on this machine does not support
``--installtypes``). It is intentionally minimal: only the surface exposed by
``web/MVP/app.py`` needs to be typed, but we keep the full public API so any
call site using these symbols stays correct.
"""
from typing import Callable, Optional, Any

from flask import Flask


def _get_current_user(user_id):
    raise NotImplementedError


# A user object implementing flask_login's RequiredUser protocol.
class UserMixin:
    is_active = True
    is_authenticated = True
    is_anonymous = False
    login_view: Optional[str] = None
    name: Optional[str] = None
    get_id: Callable[[], str] = None


# Backwards-compatible alias used by some code paths that predate UserMixin.
class AnonymousUserMixin:
    is_active = False
    is_authenticated = False
    is_anonymous = True


class LoginManager:
    user_callback: Optional[Callable[[object], object]]
    header_loader: Callable[[dict], Optional[object]]
    request_callback: Callable[[object], Optional[object]]
    login_view: Optional[str]

    def __init__(self, app: Optional["Flask"] = None):
        self._user_callback = None
        self._request_callback = None
        self.login_view = None
        self.refresh_view = None
        self.blueprint_login_views = {}
        self.login_message = None
        self.login_message_category = "default"
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        pass

    def login_view_url_for(self, view_name):
        return ""

    def set_login_view(self, view_name, blueprint=None):
        pass

    @property
    def user_callback(self):
        return self._user_callback

    @user_callback.setter
    def user_callback(self, callback):
        self._user_callback = callback
        return self._user_callback

    @property
    def header_loader(self):
        return None

    def user_loader(self, callback=None):
        self._user_callback = callback
        return self.user_callback

    def request_loader(self, callback):
        self._request_callback = callback
        return self.request_callback
