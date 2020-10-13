"""A mediation keylist query response message."""

from typing import Sequence

from marshmallow import fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema
from ..message_types import KEYLIST, PROTOCOL_PACKAGE

from .inner.keylist_query_paginate import (
    KeylistQueryPaginate,
    KeylistQueryPaginateSchema
)


HANDLER_CLASS = (
    f"{PROTOCOL_PACKAGE}.handlers"
    ".keylist_query_response_handler.KeylistHandler"
)


class Keylist(AgentMessage):
    """Class representing a keylist query response message."""

    class Meta:
        """Metadata for a keylist query response."""

        handler_class = HANDLER_CLASS
        message_type = KEYLIST
        schema_class = "KeylistSchema"

    def __init__(
        self,
        *,
        keys: Sequence[str] = None,
        pagination: KeylistQueryPaginate = None,
        **kwargs,
    ):
        """
        Initialize keylist query response object.

        Args:
            keys: Found keys by requested query
            pagination: Pagination rules
        """
        super(Keylist, self).__init__(**kwargs)
        self.keys = list(keys) if keys else []
        self.pagination = pagination


class KeylistSchema(AgentMessageSchema):
    """Keylist query response schema class."""

    class Meta:
        """Keylist query response schema metadata."""

        model_class = Keylist

    pagination = fields.Nested(
        KeylistQueryPaginateSchema(),
        description="List of update rules"
    )
    keys = fields.List(
        fields.Str(),
        description="Query dictionary object"
    )