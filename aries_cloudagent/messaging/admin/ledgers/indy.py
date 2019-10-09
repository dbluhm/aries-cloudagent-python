"""Define messages for indy ledger admin protocols."""

# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods

from marshmallow import fields
from .. import generate_model_schema, admin_only

from ...base_handler import BaseHandler, BaseResponder, RequestContext
from ....ledger.base import BaseLedger
from ....cache.base import BaseCache
from ....wallet.base import BaseWallet
from ....classloader import ClassLoader
from ....config.base import InjectorError
from ....ledger.indy import IndyLedger
from ...models.base_record import BaseRecord, BaseRecordSchema

PROTOCOL = 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/admin-indy-ledger/1.0'

GET_LIST_POOLS = '{}/get-list-pools'.format(PROTOCOL)
LIST_POOL = '{}/list-pool'.format(PROTOCOL)
CREATE_POOL = '{}/create-pool'.format(PROTOCOL)
OPEN_POOL = '{}/open-pool'.format(PROTOCOL)
CLOSE_POOL = '{}/close-pool'.format(PROTOCOL)
DELETE_POOL = '{}/delete-pool'.format(PROTOCOL)
POOL = '{}/pool'.format(PROTOCOL)

MESSAGE_TYPES = {
    POOL:
        'aries_cloudagent.messaging.admin.ledgers.indy'
        '.Pool',
    GET_LIST_POOLS:
        'aries_cloudagent.messaging.admin.ledgers.indy'
        '.GetListPools',
    LIST_POOL:
        'aries_cloudagent.messaging.admin.ledgers.indy'
        '.ListPool',
    CREATE_POOL:
        'aries_cloudagent.messaging.admin.ledgers.indy'
        '.CreatePool',
    OPEN_POOL:
        'aries_cloudagent.messaging.admin.ledgers.indy'
        '.OpenPool',
    CLOSE_POOL:
        'aries_cloudagent.messaging.admin.ledgers.indy'
        '.ClosePool',
    DELETE_POOL:
        'aries_cloudagent.messaging.admin.ledgers.indy'
        '.DeletePool'
}


class PoolRecord(BaseRecord):
    """Represents a Pool."""

    RECORD_ID_NAME = "pool"
    RECORD_TYPE = "pool"

    class Meta:
        """PoolRecord metadata."""

        schema_class = "PoolRecordSchema"

    def __init__(
         self,
         *,
         pool_name: str = None,
         **kwargs,
    ):
        """Initialize a new DidRecord."""
        super().__init__(None, None, **kwargs)
        self.pool_name = pool_name


class PoolRecordSchema(BaseRecordSchema):
    """Schema to allow serialization/deserialization of Pool records."""

    class Meta:
        """PoolRecordSchema metadata."""

        model_class = PoolRecord

    pool_name = fields.Str(required=True)


GetListPools, GetListPoolsSchema = generate_model_schema(
    name='GetListPools',
    handler='aries_cloudagent.messaging.admin.ledgers.indy.ListPoolHandler',
    msg_type=GET_LIST_POOLS,
    schema={}
)

ListPool, ListPoolSchema = generate_model_schema(
    name='ListPool',
    handler='aries_cloudagent.messaging.admin.PassHandler',
    msg_type=LIST_POOL,
    schema={
        'result': fields.List(
            fields.Nested(PoolRecordSchema),
            required=True
        )
    }
)

Pool, PoolSchema = generate_model_schema(
    name='Pool',
    handler='aries_cloudagent.messaging.admin.PassHandler',
    msg_type=POOL,
    schema={
        'pool_name': fields.Str(required=True)
    }
)

CreatePool, CreatePoolSchema = generate_model_schema(
    name='CreatePool',
    handler='aries_cloudagent.messaging.admin.ledgers.indy.CreatePoolHandler',
    msg_type=CREATE_POOL,
    schema={
        'pool_name': fields.Str(required=True),
        'genesis_txn': fields.Str(required=True)
    }
)

OpenPool, OpenPoolSchema = generate_model_schema(
    name='OpenPool',
    handler='aries_cloudagent.messaging.admin.ledgers.indy.OpenPoolHandler',
    msg_type=OPEN_POOL,
    schema={
        'pool_name': fields.Str(required=True)
    }
)

ClosePool, ClosePoolSchema = generate_model_schema(
    name='ClosePool',
    handler='aries_cloudagent.messaging.admin.ledgers.indy.ClosePoolHandler',
    msg_type=CLOSE_POOL,
    schema={
        'pool_name': fields.Str(required=True)
    }
)

DeletePool, DeletePoolSchema = generate_model_schema(
    name='DeletePool',
    handler='aries_cloudagent.messaging.admin.ledgers.indy.DeletePoolHandler',
    msg_type=DELETE_POOL,
    schema={
        'pool_name': fields.Str(required=True)
    }
)


async def get_ledger(context: RequestContext) -> IndyLedger:
    try:
        return await context.inject(BaseLedger)
    except InjectorError:
        pass

    cache: BaseCache = await context.inject(BaseCache, required=False)
    wallet: BaseWallet = await context.inject(BaseWallet)
    return IndyLedger(context.message.pool_name, wallet, keepalive=5, cache=cache)


class ListPoolHandler(BaseHandler):
    """Handler for list pools"""

    @admin_only
    async def handle(self, context: RequestContext, responder: BaseResponder):
        """List all available pools"""

        pools = await IndyLedger.list_pools()
        pool_list = ListPool(result=[PoolRecord(pool_name=x) for x in pools])
        pool_list.assign_thread_from(context.message)
        await responder.send_reply(pool_list)


class CreatePoolHandler(BaseHandler):
    """Handler for creating indy pools"""

    @admin_only
    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Create the pool and name it"""

        ledger = await get_ledger(context)
        await ledger.create_pool_config(context.message.genesis_txn)
        pool = Pool(pool_name=ledger.pool_name)
        pool.assign_thread_from(context.message)
        await responder.send_reply(pool)


class OpenPoolHandler(BaseHandler):
    """Handler for opening indy pools"""

    @admin_only
    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Open a pool"""
        ledger = await get_ledger(context)
        await ledger.open()
        pool = Pool(pool_name=ledger.pool_name)
        pool.assign_thread_from(context.message)
        await responder.send_reply(pool)


class ClosePoolHandler(BaseHandler):
    """Handler for closing indy pools"""

    @admin_only
    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Close a pool"""
        ledger = await get_ledger(context)

        await ledger.close()
        pool = Pool(pool_name=ledger.pool_name)
        pool.assign_thread_from(context.message)
        await responder.send_reply(pool)


class DeletePoolHandler(BaseHandler):
    """Handler for deleting indy pools"""

    @admin_only
    async def handle(self, context: RequestContext, responder: BaseResponder):
        """Delete a closed pool"""
        ledger = await get_ledger(context)

        await ledger.delete_pool_config()
        pool = Pool(pool_name=ledger.pool_name)
        pool.assign_thread_from(context.message)
        await responder.send_reply(pool)
