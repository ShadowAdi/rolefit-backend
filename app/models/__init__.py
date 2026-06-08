# app/models/__init__.py
# Import every model module here so SQLAlchemy's mapper registry is fully
# populated whenever any part of the package is imported. Without this, a
# process that only imports a subset of models (e.g. the Celery worker) fails
# to resolve string-based relationships such as
# relationship("EmailVerification", ...) on the User mapper.
from . import Academic  # noqa: F401
from . import Achievement  # noqa: F401
from . import ApiKeys  # noqa: F401
from . import Experience  # noqa: F401
from . import GeneratedDocument  # noqa: F401
from . import JobDescription  # noqa: F401
from . import Profile  # noqa: F401
from . import Project  # noqa: F401
from . import Publication  # noqa: F401
from . import Skill  # noqa: F401
from . import Tool  # noqa: F401
from . import User  # noqa: F401
from . import UserSkill  # noqa: F401
from . import UserTool  # noqa: F401
from . import UserVerification  # noqa: F401
