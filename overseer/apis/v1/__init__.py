import overseer.apis.v1.base as base
from overseer.apis.v1.base import api

api.add_resource(base.Suspicions, "/instances")
api.add_resource(base.Whitelist, "/whitelist")
