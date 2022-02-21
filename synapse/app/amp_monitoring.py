import logging
import math
import resource
import sys

from prometheus_client import Gauge

from synapse.metrics.background_process_metrics import wrap_as_background_process

logger = logging.getLogger("synapse.app.homeserver")

amp_users_all = Gauge("amp_users_all", "")
amp_users_guest = Gauge("amp_users_guest", "")
amp_users_deactivated = Gauge("amp_users_deactivated", "")
amp_users_basic = Gauge("amp_users_basic", "")
amp_users_limited = Gauge("amp_users_limited", "")
amp_users_mau = Gauge("amp_users_mau", "")
amp_users_otau = Gauge("amp_users_otau", "")
amp_rooms = Gauge("amp_rooms", "")

def monitor_amp_chat(hs):
    """
    Start the background monitoring for amp.chat
    """
    clock = hs.get_clock()

    @wrap_as_background_process("amp_metrics")
    async def get_amp_metrics():
        store = hs.get_datastore()

        curr_users = await store._count_amp_users()
        amp_users_all.set(curr_users)

        curr_guest = await store._count_amp_guests()
        amp_users_guest.set(curr_guest)

        curr_deactivated = await store._count_amp_deactivated()
        amp_users_deactivated.set(curr_deactivated)

        curr_basic = await store._count_amp_basic()
        amp_users_basic.set(curr_basic)

        curr_limited = await store._count_amp_limited()
        amp_users_limited.set(curr_limited)

        curr_mau = await store._count_amp_mau()
        amp_users_mau.set(curr_mau)

        curr_otau = await store._count_amp_otau()
        amp_users_otau.set(curr_otau)

        curr_rooms = await store._count_rooms()
        amp_rooms.set(curr_rooms)

    get_amp_metrics()
    clock.looping_call(get_amp_metrics, 5 * 60 * 1000)