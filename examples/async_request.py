from circleapi import AsyncGuestToken, AsyncApiV2, setup_queue_logging
import asyncio
import os


CLIENT_ID = 12345
CLIENT_SECRET = "secret"


async def main():
    # Initialize objects
    token = AsyncGuestToken(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        filepath="my_token"  # Optional: Load/Save the token on your disk
    )
    api = AsyncApiV2(token)

    # Define tasks to be gathered
    tasks = [
        api.get_beatmap_attributes(53, ruleset="osu"),
        api.get_beatmap_attributes(55, ruleset="osu")
    ]

    # Gather tasks "concurrently"
    results = await asyncio.gather(*tasks)

    print(results)


if __name__ == "__main__":
    # Windows shenanigans
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Start logging requests
    log = setup_queue_logging(to_console=True)
    log.start()

    # Run main
    asyncio.run(main())

    log.stop()

