"""Trigger a Krishi Mitra personalized outbound call."""

import argparse
import asyncio
import json
import uuid
import os
import sys

# Add backend directory to Python path
BACKEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")
)

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from dotenv import load_dotenv
from livekit import api

from src.memory.database import get_farmer


load_dotenv(".env.local")


# Must match agent_name in outbound/agent.py
AGENT_NAME = "outbound-agent"


async def dial(
    destination: str,
    room_name: str,
    farmer_id: str,
) -> None:

    # ----------------------------------------------------
    # Get farmer profile from Krishi Mitra database
    # ----------------------------------------------------

    farmer = get_farmer(farmer_id)

    if farmer is None:
        raise ValueError(
            f"Farmer '{farmer_id}' not found in database."
        )

    print()
    print("========================================")
    print("Krishi Mitra Outbound Call")
    print("========================================")
    print(f"Farmer ID       : {farmer['user_id']}")
    print(f"Farmer Name     : {farmer['name']}")
    print(f"Language        : {farmer['language_preference']}")
    print(f"Crop            : {farmer['crops_grown']}")
    print(f"Land Size       : {farmer['land_size']}")
    print(f"District        : {farmer['district']}")
    print(f"Irrigation      : {farmer['irrigation_type']}")
    print(f"SIP Destination : {destination}")
    print("========================================")
    print()

    # ----------------------------------------------------
    # Create LiveKit API client
    # ----------------------------------------------------

    lk = api.LiveKitAPI()

    try:

        # ------------------------------------------------
        # Create room
        # ------------------------------------------------

        await lk.room.create_room(
            api.CreateRoomRequest(
                name=room_name
            )
        )

        print(
            f"Created LiveKit room: {room_name}"
        )

        # ------------------------------------------------
        # Prepare farmer metadata
        # ------------------------------------------------

        metadata = {
            "phone_number": destination,
            "farmer_id": farmer["user_id"],
            "farmer_name": farmer["name"],
            "language": farmer["language_preference"],
            "crop": farmer["crops_grown"],
            "district": farmer["district"],
            "land_size": farmer["land_size"],
            "irrigation_type": farmer["irrigation_type"],
        }

        # ------------------------------------------------
        # Dispatch Krishi Mitra outbound agent
        # ------------------------------------------------

        await lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=AGENT_NAME,
                room=room_name,
                metadata=json.dumps(
                    metadata,
                    ensure_ascii=False,
                ),
            )
        )

        print(
            f"Dispatched {AGENT_NAME} "
            f"to room '{room_name}'."
        )

        print(
            f"Calling {farmer['name']} "
            f"about {farmer['crops_grown']} "
            f"in {farmer['district']}."
        )

        print()
        print(
            "Watch the agent terminal for call progress."
        )
        print()

    finally:

        await lk.aclose()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Place a personalized Krishi Mitra "
            "outbound call."
        )
    )

    # ----------------------------------------------------
    # SIP destination
    # ----------------------------------------------------

    parser.add_argument(
        "--to",
        required=True,
        help=(
            "Linphone SIP destination, "
            "for example "
            "sip:username@sip.linphone.org"
        ),
    )

    # ----------------------------------------------------
    # Farmer ID
    # ----------------------------------------------------

    parser.add_argument(
        "--farmer-id",
        required=True,
        help=(
            "Farmer user ID from the "
            "Krishi Mitra database."
        ),
    )

    # ----------------------------------------------------
    # Optional room name
    # ----------------------------------------------------

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
            args.farmer_id,
        )
    )

    print(
        f"Outbound call dispatched successfully "
        f"for farmer '{args.farmer_id}'."
    )


if __name__ == "__main__":
    main()
