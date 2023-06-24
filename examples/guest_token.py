from circleapi import GuestToken, setup_queue_logging


CLIENT_ID = 12345
CLIENT_SECRET = "SECRET"

# Start logging requests
log = setup_queue_logging(to_console=True)
log.start()

# Initialize object
token = GuestToken(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    filepath="my_token"  # Optional: Load/Save the token on your disk
)

# Check validity and renew/refresh if needed
token.check_token()

# Force refresh
token.check_token(force_refresh=True)

log.stop()
