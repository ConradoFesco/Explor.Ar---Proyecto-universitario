# Importar todos los modelos para que estén disponibles
from .user import User
from .category_site import CategorySite
from .province import Province
from .city import City
from .state_site import StateSite
from .historic_site import HistoricSite
from .tag import Tag
from .event import Event
from .permission import Permission
from .rol_user import RolUser
from .permission_rol_user import PermissionRolUser
from .rol_user_user import RolUserUser
from .tag_historic_site import TagHistoricSite
from .flag import Flag

__all__ = [
    'User',
    'CategorySite', 
    'Province',
    'City',
    'StateSite',
    'HistoricSite',
    'Tag',
    'Flag',
    'Event',
    'Permission',
    'RolUser',
    'PermissionRolUser',
    'RolUserUser',
    'TagHistoricSite'
]