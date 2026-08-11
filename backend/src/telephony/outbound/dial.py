"""Trigger a Krishi Mitra outbound call."""

import argparse
import asyncio
import json
import uuid

from dotenv import load_dotenv
from livekit import api


load_dotenv(".env.local")


# Must match agent_name in outbound/agent.py
AGENT_NAME = "outbound-agent"


async def dial(
    destination: str,
    room_name: str,
) -> None:

    lk = api.LiveKitAPI()

    try:

        # ----------------------------------------------------
        # Create room
        # ----------------------------------------------------

        await lk.room.create_room(
            api.CreateRoomRequest(
                name=room_name
            )
        )


        # ----------------------------------------------------
        # Dispatch Krishi Mitra outbound agent
        # ----------------------------------------------------

        await lk.agent_dispatch.create_dispatch(

            api.CreateAgentDispatchRequest(

                agent_name=AGENT_NAME,

                room=room_name,

                metadata=json.dumps(
                    {
                        "phone_number": destination
                    }
                ),
            )
        )

    finally:

        await lk.aclose()


def main():

    parser = argparse.ArgumentParser(
        description="Place a Krishi Mitra outbound call."
    )


    parser.add_argument(
        "--to",
        required=True,
        help=(
            "Linphone SIP destination, "
            "for example sip:username@sip.linphone.org"
        ),
    )


    parser.add_argument(
        "--room",
        default=None,
        help="Optional LiveKit room name.",
    )


    args = parser.parse_args()


    room_name = (
        args.room
        or f"krishi-outbound-{uuid.uuid4().hex[:8]}"
    )


    asyncio.run(
        dial(
            args.to,
            room_name,
        )
    )


    print(
        f"Dispatched {AGENT_NAME} "
        f"to room '{room_name}' "
        f"to call {args.to}."
    )

    print(
        "Watch the agent terminal for call progress."
    )


if __name__ == "__main__":
    main()
