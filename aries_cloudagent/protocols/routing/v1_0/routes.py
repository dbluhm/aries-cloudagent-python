""" routing routes for did_comm forwarding"""

from aiohttp import web
from aiohttp_apispec import (
    docs,
    match_info_schema,
    querystring_schema,
    request_schema,
    response_schema,
)

from .message_types import SPEC_URI

async def register(app: web.Application):
    """Register routes."""

    app.add_routes(
        [
            #web.get("/routess", list_keylists, allow_head=False),
            #web.update("/routes", update_keylists ),
            #web.delete("/routes", delete_keylist ),
        ]
    )


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "routes",
            "description": "List of connection ID to key list mappings used for message forwarding",
            "externalDocs": {"description": "Specification", "url": SPEC_URI},
        }
    )