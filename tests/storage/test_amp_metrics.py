from tests import unittest

from synapse.types import UserID, create_requester


class AmpMetricsStoreTestCase(unittest.HomeserverTestCase):
    def prepare(self, reactor, clock, hs):
        self.store = hs.get_datastore()
        self.room_creator = hs.get_room_creation_handler()

    def test_count_amp_users(self):
        standard_user1 = "@standard_user1:test"
        standard_user2 = "@standard_user2:test"

        self.get_success(
            self.store.register_user(
                user_id=standard_user1, password_hash=None)
        )

        count = self.get_success(self.store._count_amp_users())
        self.assertEqual(count, 1)

        self.get_success(
            self.store.register_user(
                user_id=standard_user2, password_hash=None)
        )

        count = self.get_success(self.store._count_amp_users())
        self.assertEqual(count, 2)

    def test_count_amp_guests(self):
        standard_user = "@standard_user:test"
        guest_user = "@guest_user:test"

        count = self.get_success(self.store._count_amp_guests())
        self.assertEqual(count, 0)

        self.get_success(
            self.store.register_user(
                user_id=standard_user, password_hash=None, make_guest=False)
        )
        self.get_success(
            self.store.register_user(
                user_id=guest_user, password_hash=None, make_guest=True)
        )

        count = self.get_success(self.store._count_amp_guests())
        self.assertEqual(count, 1)

    def test_count_amp_deactivated(self):
        standard_user = "@standard_user:test"
        deactivated_user = "@deactivated_user:test"

        count = self.get_success(self.store._count_amp_deactivated())
        self.assertEqual(count, 0)

        self.get_success(
            self.store.register_user(
                user_id=standard_user, password_hash=None)
        )
        self.get_success(
            self.store.register_user(
                user_id=deactivated_user, password_hash=None)
        )

        self.get_success(self.store.set_user_deactivated_status(deactivated_user, True))

        count = self.get_success(self.store._count_amp_deactivated())
        self.assertEqual(count, 1)

    def test_count_amp_basic(self):
        standard_user = "@standard_user:test"
        basic_user = "@basic_user:test"

        basic_type = "free"

        count = self.get_success(self.store._count_amp_basic())
        self.assertEqual(count, 0)

        self.get_success(
            self.store.register_user(
                user_id=standard_user, password_hash=None, user_type=None)
        )
        self.get_success(
            self.store.register_user(
                user_id=basic_user, password_hash=None, user_type=basic_type)
        )

        count = self.get_success(self.store._count_amp_basic())
        self.assertEqual(count, 1)

    def test_count_amp_limited(self):
        standard_user = "@standard_user:test"
        limited_user = "@limited_user:test"

        limited_type = "limited"

        count = self.get_success(self.store._count_amp_limited())
        self.assertEqual(count, 0)

        self.get_success(
            self.store.register_user(
                user_id=standard_user, password_hash=None, user_type=None)
        )
        self.get_success(
            self.store.register_user(
                user_id=limited_user, password_hash=None, user_type=limited_type)
        )

        count = self.get_success(self.store._count_amp_limited())
        self.assertEqual(count, 1)

    def test_count_amp_mau(self):
        standard_user = "@standard_user:test"
        mau = "@mau:test"

        self.get_success(
            self.store.register_user(
                user_id=standard_user, password_hash=None)
        )
        self.get_success(
            self.store.register_user(
                user_id=mau, password_hash=None)
        )

        count = self.get_success(self.store._count_amp_mau())
        self.assertEqual(count, 0)

        self.get_success(self.store.upsert_monthly_active_user(mau))

        count = self.get_success(self.store._count_amp_mau())
        self.assertEqual(count, 1)

    def test_count_amp_otau(self):
        standard_user = "@standard_user:test"
        otau = "@otau:test"

        self.get_success(
            self.store.register_user(
                user_id=standard_user, password_hash=None)
        )
        self.get_success(
            self.store.register_user(
                user_id=otau, password_hash=None)
        )

        count = self.get_success(self.store._count_amp_otau())
        self.assertEqual(count, 0)

        requester = create_requester(UserID.from_string(otau))
        info, _ = self.get_success(self.room_creator.create_room(requester, {}))
        room_id = info["room_id"]

        event_id = self.create_and_send_event(room_id, UserID.from_string(otau))

        count = self.get_success(self.store._count_amp_otau())
        self.assertEqual(count, 1)

    def test_count_rooms(self):
        standard_user = "@standard_user:test"
        requester = create_requester(standard_user)

        user_id = UserID("helper", "test")
        our_user = create_requester(user_id)

        count = self.get_success(self.store._count_rooms())
        self.assertEqual(count, 0)

        room_creator = self.hs.get_room_creation_handler()
        self.room_id = self.get_success(
            self.room_creator.create_room(
                our_user, {}
            )
        )

        count = self.get_success(self.store._count_rooms())
        self.assertEqual(count, 1)
