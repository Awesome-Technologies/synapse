import calendar
import logging
import time

from synapse.storage._base import SQLBaseStore
from synapse.storage.database import DatabasePool

logger = logging.getLogger(__name__)

class AmpMetricsStore(SQLBaseStore):
    """Functions to pull various metrics from the DB for amp monitoring
    """

    def __init__(self, database: DatabasePool, db_conn, hs):
        super().__init__(database, db_conn, hs)

    #generates current count of overall users
    async def _count_amp_users(self) -> int:
        def _count(txn):
            sql = """
                SELECT count(*)
                FROM users;
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)

    #generates current count of guest users
    async def _count_amp_guests(self) -> int:
        def _count(txn):
            sql = """
                SELECT count(*)
                FROM users
                WHERE is_guest <> 0;
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)

    #generates current count of deactivated users
    async def _count_amp_deactivated(self) -> int:
        def _count(txn):
            sql = """
                SELECT count(*)
                FROM users
                WHERE deactivated <> 0;
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)

    #generates current count of basic users
    async def _count_amp_basic(self) -> int:
        def _count(txn):
            sql = """
                SELECT count(*)
                FROM users
                WHERE user_type = 'free';
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)

    #generates current count of limited users
    async def _count_amp_limited(self) -> int:
        def _count(txn):
            sql = """
                SELECT count(*)
                FROM users
                WHERE user_type = 'limited';
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)

    #generates current count of monthly active users
    async def _count_amp_mau(self) -> int:
        def _count(txn):
            sql = """
                SELECT COUNT(*)
                FROM (SELECT name as user_id FROM users
                        WHERE is_guest=0 AND user_type IS NULL) AS u INNER JOIN
                        (SELECT user_id FROM monthly_active_users)
                        AS v ON u.user_id=v.user_id
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)

    #generates current count of one time active users
    async def _count_amp_otau(self) -> int:
        def _count(txn):
            sql = """
                SELECT count(*)
                FROM (SELECT sender AS user_id FROM events
                        GROUP BY user_id LIMIT 1) AS u INNER JOIN
                        (SELECT name AS user_id FROM users
                        WHERE is_guest = 0 AND deactivated = 0 AND user_type IS NULL)
                        AS v ON u.user_id = v.user_id
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)

    #generates current count of rooms
    async def _count_rooms(self) -> int:
        def _count(txn):
            sql = """
                SELECT count(*)
                FROM rooms;
            """
            txn.execute(sql)
            (count,) = txn.fetchone()
            return count

        return await self.db_pool.runInteraction("count", _count)
