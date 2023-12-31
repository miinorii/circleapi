from circleapi import UserToken, start_logging


CLIENT_ID = 12345
CLIENT_SECRET = "secret"

# Start logging requests
with start_logging(to_console=True):
    # Initialize object
    token = UserToken(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        filepath="filepath"  # Optional: Load/Save the token on your disk
    )

    # Check validity and renew/refresh if needed
    token.check_token()

    # Force renewal
    # token.check_token(force_renew=True)

    # Force refresh
    # token.check_token(force_refresh=True)

