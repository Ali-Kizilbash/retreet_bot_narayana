from .common import router as common_router
from .client import router as client_router
from .admin import router as admin_router
from .support import router as support_router

__all__ = ["common_router", "client_router", "admin_router", "support_router"]