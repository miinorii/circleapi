from circleapi import GuestToken, ApiV2, setup_queue_logging


CLIENT_ID = 12345
CLIENT_SECRET = "secret"

# Start logging requests
log = setup_queue_logging(to_console=True)
log.start()

# Initialize objects
token = GuestToken(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    filepath="my_token"  # Optional: Load/Save the token on your disk
)
api = ApiV2(token)

first_request = api.get_beatmap_attributes(53, ruleset="osu", as_thread=True)
second_request = api.get_beatmap_attributes(55, ruleset="osu", as_thread=True)

# Start and join threads
first_request.start()
second_request.start()

first_request.join()
second_request.join()

# Print results
print(first_request.result)
print(first_request.args)
print(second_request.result)
print(second_request.args)

log.stop()
