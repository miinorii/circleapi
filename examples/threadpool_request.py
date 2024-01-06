import concurrent.futures
from circleapi import GuestToken, ApiV2, start_logging


CLIENT_ID = 12345
CLIENT_SECRET = "secret"
MAX_THREAD_COUNT = 4

# Initialize objects
token = GuestToken(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    filepath="my_token"
)
api = ApiV2(token)

req_args = [{"beatmap_id": 53, "ruleset": "osu"}, {"beatmap_id": 55, "ruleset": "osu"}]
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREAD_COUNT) as executor, start_logging(to_console=True):
    future_to_args = {executor.submit(api.get_beatmap_attributes, **args): args for args in req_args}
    for future in concurrent.futures.as_completed(future_to_args):
        args = future_to_args.pop(future)
        try:
            data = future.result()
        except Exception as exc:
            print(f"{args} generated an exception: {exc}")
        else:
            print(data)

