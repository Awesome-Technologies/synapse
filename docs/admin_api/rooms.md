# Contents
- [List Room](#list-room-api)        `GET    /_synapse/admin/v1/rooms`
- [Create Room](#create-room-api)    `POST   /_synapse/admin/v1/rooms`
- [Room Details](#room-details-api)  `GET    /_synapse/admin/v1/rooms/<room_id>`
- [Delete Room](#delete-room-api)    `DELETE /_synapse/admin/v1/rooms/<room_id>`
  * [Undoing room shutdowns](#undoing-room-shutdowns)
- [Room Members](#room-members-api)  `GET    /_synapse/admin/v1/rooms/<room_id>/members`
- [Make Room Admin](#make-room-admin-api) `POST /_synapse/admin/v1/rooms/<room_id_or_alias>/make_room_admin`
- [Forward Extremities](#forward-extremities-admin-api) `GET|DELETE /_synapse/admin/v1/rooms/<room_id_or_alias>/forward_extremities`
- [Event Context](#event-context-api) `GET   /_synapse/admin/v1/rooms/<room_id>/context/<event_id>`


# List Room API

The List Room admin API allows server admins to get a list of rooms on their
server. There are various parameters available that allow for filtering and
sorting the returned list. This API supports pagination.

## Parameters

<details>
<summary>The following query parameters are available</summary>

* `from` - Offset in the returned list. Defaults to `0`.
* `limit` - Maximum amount of rooms to return. Defaults to `100`.
* `order_by` - The method in which to sort the returned list of rooms. Valid values are:
  - `alphabetical` - Same as `name`. This is deprecated.
  - `size` - Same as `joined_members`. This is deprecated.
  - `name` - Rooms are ordered alphabetically by room name. This is the default.
  - `canonical_alias` - Rooms are ordered alphabetically by main alias address of the room.
  - `joined_members` - Rooms are ordered by the number of members. Largest to smallest.
  - `joined_local_members` - Rooms are ordered by the number of local members. Largest to smallest.
  - `version` - Rooms are ordered by room version. Largest to smallest.
  - `creator` - Rooms are ordered alphabetically by creator of the room.
  - `encryption` - Rooms are ordered alphabetically by the end-to-end encryption algorithm.
  - `federatable` - Rooms are ordered by whether the room is federatable.
  - `public` - Rooms are ordered by visibility in room list.
  - `join_rules` - Rooms are ordered alphabetically by join rules of the room.
  - `guest_access` - Rooms are ordered alphabetically by guest access option of the room.
  - `history_visibility` - Rooms are ordered alphabetically by visibility of history of the room.
  - `state_events` - Rooms are ordered by number of state events. Largest to smallest.
* `dir` - Direction of room order. Either `f` for forwards or `b` for backwards. Setting
          this value to `b` will reverse the above sort order. Defaults to `f`.
* `search_term` - Filter rooms by their room name. Search term can be contained in any
                  part of the room name. Defaults to no filtering.
</details>
<details>
<summary>The following fields are possible in the JSON response body</summary>

* `rooms` - An array of objects, each containing information about a room.
  - Room objects contain the following fields:
    - `room_id` - The ID of the room.
    - `name` - The name of the room.
    - `canonical_alias` - The canonical (main) alias address of the room.
    - `joined_members` - How many users are currently in the room.
    - `joined_local_members` - How many local users are currently in the room.
    - `version` - The version of the room as a string.
    - `creator` - The `user_id` of the room creator.
    - `encryption` - Algorithm of end-to-end encryption of messages. Is `null` if encryption is not active.
    - `federatable` - Whether users on other servers can join this room.
    - `public` - Whether the room is visible in room directory.
    - `join_rules` - The type of rules used for users wishing to join this room. One of: ["public", "knock", "invite", "private"].
    - `guest_access` - Whether guests can join the room. One of: ["can_join", "forbidden"].
    - `history_visibility` - Who can see the room history. One of: ["invited", "joined", "shared", "world_readable"].
    - `state_events` - Total number of state_events of a room. Complexity of the room.
* `offset` - The current pagination offset in rooms. This parameter should be
             used instead of `next_batch` for room offset as `next_batch` is
             not intended to be parsed.
* `total_rooms` - The total number of rooms this query can return. Using this
                  and `offset`, you have enough information to know the current
                  progression through the list.
* `next_batch` - If this field is present, we know that there are potentially
                 more rooms on the server that did not all fit into this response.
                 We can use `next_batch` to get the "next page" of results. To do
                 so, simply repeat your request, setting the `from` parameter to
                 the value of `next_batch`.
* `prev_batch` - If this field is present, it is possible to paginate backwards.
                 Use `prev_batch` for the `from` value in the next request to
                 get the "previous page" of results.
</details>

## Usage

- List all rooms: `GET /_synapse/admin/v1/rooms`
  <details>
  <summary>Response</summary>

  ```jsonc
  {
    "rooms": [
      {
        "room_id": "!OGEhHVWSdvArJzumhm:matrix.org",
        "name": "Matrix HQ",
        "canonical_alias": "#matrix:matrix.org",
        "joined_members": 8326,
        "joined_local_members": 2,
        "version": "1",
        "creator": "@foo:matrix.org",
        "encryption": null,
        "federatable": true,
        "public": true,
        "join_rules": "invite",
        "guest_access": null,
        "history_visibility": "shared",
        "state_events": 93534
      },
      ... (8 hidden items) ...
      {
        "room_id": "!xYvNcQPhnkrdUmYczI:matrix.org",
        "name": "This Week In Matrix (TWIM)",
        "canonical_alias": "#twim:matrix.org",
        "joined_members": 314,
        "joined_local_members": 20,
        "version": "4",
        "creator": "@foo:matrix.org",
        "encryption": "m.megolm.v1.aes-sha2",
        "federatable": true,
        "public": false,
        "join_rules": "invite",
        "guest_access": null,
        "history_visibility": "shared",
        "state_events": 8345
      }
    ],
    "offset": 0,
    "total_rooms": 10
  }
  ```
  </details>

- Filter by room name: `GET /_synapse/admin/v1/rooms?search_term=TWIM`
  <details>
  <summary>Response</summary>

  ```json
  {
    "rooms": [
      {
        "room_id": "!xYvNcQPhnkrdUmYczI:matrix.org",
        "name": "This Week In Matrix (TWIM)",
        "canonical_alias": "#twim:matrix.org",
        "joined_members": 314,
        "joined_local_members": 20,
        "version": "4",
        "creator": "@foo:matrix.org",
        "encryption": "m.megolm.v1.aes-sha2",
        "federatable": true,
        "public": false,
        "join_rules": "invite",
        "guest_access": null,
        "history_visibility": "shared",
        "state_events": 8
      }
    ],
    "offset": 0,
    "total_rooms": 1
  }
  ```
  </details>

- Sort by number of joined members: `GET /_synapse/admin/v1/rooms?order_by=size`
  <details>
  <summary>Response</summary>

  ```jsonc
  {
    "rooms": [
      {
        "room_id": "!OGEhHVWSdvArJzumhm:matrix.org",
        "name": "Matrix HQ",
        "canonical_alias": "#matrix:matrix.org",
        "joined_members": 8326,
        "joined_local_members": 2,
        "version": "1",
        "creator": "@foo:matrix.org",
        "encryption": null,
        "federatable": true,
        "public": true,
        "join_rules": "invite",
        "guest_access": null,
        "history_visibility": "shared",
        "state_events": 93534
      },
      ... (98 hidden items) ...
      {
        "room_id": "!xYvNcQPhnkrdUmYczI:matrix.org",
        "name": "This Week In Matrix (TWIM)",
        "canonical_alias": "#twim:matrix.org",
        "joined_members": 314,
        "joined_local_members": 20,
        "version": "4",
        "creator": "@foo:matrix.org",
        "encryption": "m.megolm.v1.aes-sha2",
        "federatable": true,
        "public": false,
        "join_rules": "invite",
        "guest_access": null,
        "history_visibility": "shared",
        "state_events": 8345
      }
    ],
    "offset": 0,
    "total_rooms": 150
    "next_batch": 100
  }
  ```

  The presence of the `next_batch` parameter tells us that there are more rooms
  than returned in this request, and we need to make another request to get them.
  To get the next batch of room results, we repeat our request, setting the `from`
  parameter to the value of `next_batch`.
  </details>

- Paginate through a list of rooms: `GET /_synapse/admin/v1/rooms?order_by=size&from=100`
  <details>
  <summary>Response</summary>

  ```jsonc
  {
    "rooms": [
      {
        "room_id": "!mscvqgqpHYjBGDxNym:matrix.org",
        "name": "Music Theory",
        "canonical_alias": "#musictheory:matrix.org",
        "joined_members": 127,
        "joined_local_members": 2,
        "version": "1",
        "creator": "@foo:matrix.org",
        "encryption": null,
        "federatable": true,
        "public": true,
        "join_rules": "invite",
        "guest_access": null,
        "history_visibility": "shared",
        "state_events": 93534
      },
      ... (48 hidden items) ...
      {
        "room_id": "!twcBhHVdZlQWuuxBhN:termina.org.uk",
        "name": "weechat-matrix",
        "canonical_alias": "#weechat-matrix:termina.org.uk",
        "joined_members": 137,
        "joined_local_members": 20,
        "version": "4",
        "creator": "@foo:termina.org.uk",
        "encryption": null,
        "federatable": true,
        "public": true,
        "join_rules": "invite",
        "guest_access": null,
        "history_visibility": "shared",
        "state_events": 8345
      }
    ],
    "offset": 100,
    "prev_batch": 0,
    "total_rooms": 150
  }
  ```

  Once the `next_batch` parameter is no longer present, we know we've reached the
  end of the list.
  </details>


# Create Room API

The Create Room admin API allows server admins to create a new room on the server.
It is possible to specify an owner for the room other than the requester himself.
In that case, the server admin, who made the request **does not** become a member
of the created room.

## Parameters

<details>
<summary>The following query body parameters are available</summary>

The body parameters are the same as in [/_matrix/client/r0/createRoom](https://matrix.org/docs/spec/client_server/r0.6.1#post-matrix-client-r0-createroom) with one additional optional parameter
```json
{
    "owner": "@someuser:example.com"
}
```
</details>
<details>
<summary>The following fields are possible in the JSON response body</summary>

The response body is identical to the one of [/_matrix/client/r0/createRoom](https://matrix.org/docs/spec/client_server/r0.6.1#post-matrix-client-r0-createroom)
</details>

## Usage

<details>
<summary>Create a room</summary>
  Request:

  ```json
  POST /_matrix/client/r0/createRoom HTTP/1.1
  Content-Type: application/json

  {
    "preset": "public_chat",
    "room_alias_name": "thepub",
    "name": "The Grand Duke Pub",
    "topic": "All about happy hour",
    "creation_content": {
      "m.federate": false
    },
    "owner": "@user:matrix.org"
  }
  ```

  Response:

  ```json
  {
    "room_id": "!sefiuhWgwghwWgh:example.com"
  }
  ```
  </details>


# Room Details API

The Room Details admin API allows server admins to get all details of a room.

<details>
<summary>The following fields are possible in the JSON response body</summary>

* `room_id` - The ID of the room.
* `name` - The name of the room.
* `topic` - The topic of the room.
* `avatar` - The `mxc` URI to the avatar of the room.
* `canonical_alias` - The canonical (main) alias address of the room.
* `joined_members` - How many users are currently in the room.
* `joined_local_members` - How many local users are currently in the room.
* `joined_local_devices` - How many local devices are currently in the room.
* `version` - The version of the room as a string.
* `creator` - The `user_id` of the room creator.
* `encryption` - Algorithm of end-to-end encryption of messages. Is `null` if encryption is not active.
* `federatable` - Whether users on other servers can join this room.
* `public` - Whether the room is visible in room directory.
* `join_rules` - The type of rules used for users wishing to join this room. One of: ["public", "knock", "invite", "private"].
* `guest_access` - Whether guests can join the room. One of: ["can_join", "forbidden"].
* `history_visibility` - Who can see the room history. One of: ["invited", "joined", "shared", "world_readable"].
* `state_events` - Total number of state_events of a room. Complexity of the room.
</details>

## Usage

- Get room details: `GET /_synapse/admin/v1/rooms/<room_id>`
  <details>
  <summary>Response</summary>

  ```json
  {
    "room_id": "!mscvqgqpHYjBGDxNym:matrix.org",
    "name": "Music Theory",
    "avatar": "mxc://matrix.org/AQDaVFlbkQoErdOgqWRgiGSV",
    "topic": "Theory, Composition, Notation, Analysis",
    "canonical_alias": "#musictheory:matrix.org",
    "joined_members": 127,
    "joined_local_members": 2,
    "joined_local_devices": 2,
    "version": "1",
    "creator": "@foo:matrix.org",
    "encryption": null,
    "federatable": true,
    "public": true,
    "join_rules": "invite",
    "guest_access": null,
    "history_visibility": "shared",
    "state_events": 93534
  }
  ```
  </details>


# Delete Room API

The Delete Room API allows server admins to remove a room from the server
and block this room.

Shuts down a room. Moves all local users and room aliases automatically to a
new room if `new_room_user_id` is set. Otherwise local users only
leave the room without any information.

The new room will be created with the user specified by the `new_room_user_id` parameter
as room administrator and will contain a message explaining what happened. Users invited
to the new room will have power level `-10` by default, and thus be unable to speak.

If `block` is `True` it prevents new joins to the old room.

This API will remove all trace of the old room from your database after removing
all local users. If `purge` is `true` (the default), all traces of the old room will
be removed from your database after removing all local users. If you do not want
this to happen, set `purge` to `false`.
Depending on the amount of history being purged a call to the API may take
several minutes or longer.

The local server will only have the power to move local user and room aliases to
the new room. Users on other servers will be unaffected.

## Parameters

<details>
<summary>The following parameters should be set in the URL</summary>

* `room_id` - The ID of the room.

</details>

<details>
<summary>The following query body parameters are available</summary>

* `new_room_user_id` - Optional. If set, a new room will be created with this user ID
      as the creator and admin, and all users in the old room will be moved into that
      room. If not set, no new room will be created and the users will just be removed
      from the old room. The user ID must be on the local server, but does not necessarily
      have to belong to a registered user.
* `room_name` - Optional. A string representing the name of the room that new users will be
                invited to. Defaults to `Content Violation Notification`
* `message` - Optional. A string containing the first message that will be sent as
              `new_room_user_id` in the new room. Ideally this will clearly convey why the
               original room was shut down. Defaults to `Sharing illegal content on this server
               is not permitted and rooms in violation will be blocked.`
* `block` - Optional. If set to `true`, this room will be added to a blocking list, preventing
            future attempts to join the room. Defaults to `false`.
* `purge` - Optional. If set to `true`, it will remove all traces of the room from your database.
            Defaults to `true`.
* `force_purge` - Optional, and ignored unless `purge` is `true`. If set to `true`, it
  will force a purge to go ahead even if there are local users still in the room. Do not
  use this unless a regular `purge` operation fails, as it could leave those users'
  clients in a confused state.

The JSON body must not be empty. The body must be at least `{}`.
</details>
<details>
<summary>The following fields are possible in the JSON response body</summary>

* `kicked_users` - An array of users (`user_id`) that were kicked.
* `failed_to_kick_users` - An array of users (`user_id`) that that were not kicked.
* `local_aliases` - An array of strings representing the local aliases that were migrated from
                    the old room to the new.
* `new_room_id` - A string representing the room ID of the new room.
</details>

## Usage

<details>
<summary>Delete and purge a room</summary>

Example request:

```json
DELETE /_synapse/admin/v1/rooms/<room_id> HTTP/1.1
Content-Type: application/json

{
    "purge": true
}
```

Example response:

```json
{
    "kicked_users": [
        "@foobar:example.com"
    ],
    "failed_to_kick_users": []
}
```
</details>

<details>
<summary>Delete a room and move users to a new room</summary>

Example request:

```json
DELETE /_synapse/admin/v1/rooms/<room_id> HTTP/1.1
Content-Type: application/json

{
    "new_room_user_id": "@someuser:example.com",
    "room_name": "Content Violation Notification",
    "message": "Bad Room has been shutdown due to content violations on this server. Please review our Terms of Service.",
    "block": true,
    "purge": false
}
```

Example response:

```json
{
    "kicked_users": [
        "@foobar:example.com"
    ],
    "failed_to_kick_users": [],
    "local_aliases": [
        "#badroom:example.com",
        "#evilsaloon:example.com"
    ],
    "new_room_id": "!newroomid:example.com"
}
```
</details>

## Undoing room shutdowns

*Note*: This guide may be outdated by the time you read it. By nature of room shutdowns being performed at the database level,
the structure can and does change without notice.

First, it's important to understand that a room shutdown is very destructive. Undoing a shutdown is not as simple as pretending it
never happened - work has to be done to move forward instead of resetting the past. In fact, in some cases it might not be possible
to recover at all:

* If the room was invite-only, your users will need to be re-invited.
* If the room no longer has any members at all, it'll be impossible to rejoin.
* The first user to rejoin will have to do so via an alias on a different server.

With all that being said, if you still want to try and recover the room:

1. For safety reasons, shut down Synapse.
2. In the database, run `DELETE FROM blocked_rooms WHERE room_id = '!example:example.org';`
   * For caution: it's recommended to run this in a transaction: `BEGIN; DELETE ...;`, verify you got 1 result, then `COMMIT;`.
   * The room ID is the same one supplied to the shutdown room API, not the Content Violation room.
3. Restart Synapse.

You will have to manually handle, if you so choose, the following:

* Aliases that would have been redirected to the Content Violation room.
* Users that would have been booted from the room (and will have been force-joined to the Content Violation room).
* Removal of the Content Violation room if desired.

## Deprecated endpoint

The previous deprecated API will be removed in a future release, it was:

```
POST /_synapse/admin/v1/rooms/<room_id>/delete
```

It behaves the same way as the current endpoint except the path and the method.


# Room Members API

The Room Members admin API allows server admins to get a list of all members of a room.

<details>
<summary>The response includes the following fields</summary>

* `members` - A list of all the members that are present in the room, represented by their ids.
* `total` - Total number of members in the room.
</details>

## Usage

<details>
<summary>List all room members</summary>

```
GET /_synapse/admin/v1/rooms/<room_id>/members
```

Response:

```json
{
  "members": [
    "@foo:matrix.org",
    "@bar:matrix.org",
    "@foobar:matrix.org"
  ],
  "total": 3
}
```
</details>


# Room State API

The Room State admin API allows server admins to get a list of all state events in a room.

<details>
<summary>The response includes the following fields</summary>

* `state` - The current state of the room at the time of request.
</details>

## Usage

<details>
<summary>Get room state</summary>

```
GET /_synapse/admin/v1/rooms/<room_id>/state
```

Response:

```json
{
  "state": [
    {"type": "m.room.create", "state_key": "", "etc": true},
    {"type": "m.room.power_levels", "state_key": "", "etc": true},
    {"type": "m.room.name", "state_key": "", "etc": true}
  ]
}
```
</details>


# Make Room Admin API

Grants a server admin or another user the highest power available in the room.
If the user is not in the room, and it is not publicly joinable, then invite the user.

By default the server admin (the caller) is granted power, but another user can
optionally be specified.

## Usage

<details>
<summary>Grant highest power level to server admin making the request</summary>

```
    POST /_synapse/admin/v1/rooms/<room_id_or_alias>/make_room_admin HTTP/1.1
```
</details>
<details>
<summary>Grant highest power level to another user</summary>

```json
    POST /_synapse/admin/v1/rooms/<room_id_or_alias>/make_room_admin HTTP/1.1
    Content-Type: application/json

    {
        "user_id": "@foo:example.com"
    }
```
</details>

# Forward Extremities Admin API

Enables querying and deleting forward extremities from rooms. When a lot of forward
extremities accumulate in a room, performance can become degraded. For details, see 
[#1760](https://github.com/matrix-org/synapse/issues/1760).

## Usage

<details>
<summary>Check for forward extremities</summary>

```
GET /_synapse/admin/v1/rooms/<room_id_or_alias>/forward_extremities
```

A response as follows will be returned:

```json
{
  "count": 1,
  "results": [
    {
      "event_id": "$M5SP266vsnxctfwFgFLNceaCo3ujhRtg_NiiHabcdefgh",
      "state_group": 439,
      "depth": 123,
      "received_ts": 1611263016761
    }
  ]
}    
```
</details>
<details>
<summary>Delete forward extremities</summary>

**WARNING**: Please ensure you know what you're doing and have read 
the related issue [#1760](https://github.com/matrix-org/synapse/issues/1760).
Under no situations should this API be executed as an automated maintenance task!

If a room has lots of forward extremities, the extra can be
deleted as follows:

```
DELETE /_synapse/admin/v1/rooms/<room_id_or_alias>/forward_extremities
```

A response as follows will be returned, indicating the amount of forward extremities
that were deleted.

```json
{
  "deleted": 1
}
```
</details>


# Event Context API

This API lets a client find the context of an event. This is designed primarily to investigate abuse reports.

## Usage

<details>
<summary>Find the context of an event</summary>

```
GET /_synapse/admin/v1/rooms/<room_id>/context/<event_id>
```

This API mimmicks [GET /_matrix/client/r0/rooms/{roomId}/context/{eventId}](https://matrix.org/docs/spec/client_server/r0.6.1#get-matrix-client-r0-rooms-roomid-context-eventid). Please refer to the link for all details on parameters and reseponse.

Example response:

```json
{
  "end": "t29-57_2_0_2",
  "events_after": [
    {
      "content": {
        "body": "This is an example text message",
        "msgtype": "m.text",
        "format": "org.matrix.custom.html",
        "formatted_body": "<b>This is an example text message</b>"
      },
      "type": "m.room.message",
      "event_id": "$143273582443PhrSn:example.org",
      "room_id": "!636q39766251:example.com",
      "sender": "@example:example.org",
      "origin_server_ts": 1432735824653,
      "unsigned": {
        "age": 1234
      }
    }
  ],
  "event": {
    "content": {
      "body": "filename.jpg",
      "info": {
        "h": 398,
        "w": 394,
        "mimetype": "image/jpeg",
        "size": 31037
      },
      "url": "mxc://example.org/JWEIFJgwEIhweiWJE",
      "msgtype": "m.image"
    },
    "type": "m.room.message",
    "event_id": "$f3h4d129462ha:example.com",
    "room_id": "!636q39766251:example.com",
    "sender": "@example:example.org",
    "origin_server_ts": 1432735824653,
    "unsigned": {
      "age": 1234
    }
  },
  "events_before": [
    {
      "content": {
        "body": "something-important.doc",
        "filename": "something-important.doc",
        "info": {
          "mimetype": "application/msword",
          "size": 46144
        },
        "msgtype": "m.file",
        "url": "mxc://example.org/FHyPlCeYUSFFxlgbQYZmoEoe"
      },
      "type": "m.room.message",
      "event_id": "$143273582443PhrSn:example.org",
      "room_id": "!636q39766251:example.com",
      "sender": "@example:example.org",
      "origin_server_ts": 1432735824653,
      "unsigned": {
        "age": 1234
      }
    }
  ],
  "start": "t27-54_2_0_2",
  "state": [
    {
      "content": {
        "creator": "@example:example.org",
        "room_version": "1",
        "m.federate": true,
        "predecessor": {
          "event_id": "$something:example.org",
          "room_id": "!oldroom:example.org"
        }
      },
      "type": "m.room.create",
      "event_id": "$143273582443PhrSn:example.org",
      "room_id": "!636q39766251:example.com",
      "sender": "@example:example.org",
      "origin_server_ts": 1432735824653,
      "unsigned": {
        "age": 1234
      },
      "state_key": ""
    },
    {
      "content": {
        "membership": "join",
        "avatar_url": "mxc://example.org/SEsfnsuifSDFSSEF",
        "displayname": "Alice Margatroid"
      },
      "type": "m.room.member",
      "event_id": "$143273582443PhrSn:example.org",
      "room_id": "!636q39766251:example.com",
      "sender": "@example:example.org",
      "origin_server_ts": 1432735824653,
      "unsigned": {
        "age": 1234
      },
      "state_key": "@alice:example.org"
    }
  ]
}
```
</details>
