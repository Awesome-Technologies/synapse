# -*- coding: utf-8 -*-
# Copyright 2020 Awesome Technologies Innovationslabor GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Callable

from synapse.events import EventBase
from synapse.events.snapshot import EventContext
from synapse.types import Requester, StateMap


class RoomCreationRules:
    """Implementation of the ThirdPartyEventRules module API that allows federation admins
    to define custom rules for specific events and actions.
    """

    def __init__(self, config, http_client):
        self.http_client = http_client

    async def check_event_allowed(
        self, event: EventBase, context: EventContext
    ) -> bool:
        """Check if a provided event should be allowed in the given context.
        Args:
            event: The event to be checked.
            context: The context of the event.
        Returns:
            True if the event should be allowed, False if not.
        """

        return True

    async def on_create_room(
        self, requester: Requester, config: dict, is_requester_admin: bool
    ) -> bool:
        """Intercept requests to create room to allow, deny or update the
        request config.
        Args:
            requester
            config: The creation config from the client.
            is_requester_admin: If the requester is an admin
        Returns:
            Whether room creation is allowed or denied.
        """

        if not is_requester_admin and not is_direct:
            raise SynapseError(400, "Only server admins are allowed to create rooms")

        return True

    async def check_threepid_can_be_invited(
        self, medium: str, address: str, room_id: str
    ) -> bool:
        """Check if a provided 3PID can be invited in the given room.
        Args:
            medium: The 3PID's medium.
            address: The 3PID's address.
            room_id: The room we want to invite the threepid to.
        Returns:
            True if the 3PID can be invited, False if not.
        """

        return True

    async def check_visibility_can_be_modified(
        self, room_id: str, new_visibility: str
    ) -> bool:
        """Check if a room is allowed to be published to, or removed from, the public room
        list.
        Args:
            room_id: The ID of the room.
            new_visibility: The new visibility state. Either "public" or "private".
        Returns:
            True if the room's visibility can be modified, False if not.
        """

        return True

    async def _get_state_map_for_room(self, room_id: str) -> StateMap[EventBase]:
        """Given a room ID, return the state events of that room.
        Args:
            room_id: The ID of the room.
        Returns:
            A dict mapping (event type, state key) to state event.
        """
        state_ids = await self.store.get_filtered_current_state_ids(room_id)
        room_state_events = await self.store.get_events(state_ids.values())

        state_events = {}
        for key, event_id in state_ids.items():
            state_events[key] = room_state_events[event_id]

        return state_events
