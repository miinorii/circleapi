circleapi
---------

Yet another python wrapper for the osu! api

Take a look at the "examples" folder for typical use cases.

Disclaimer
----------

The wrapper was tailored for my needs (token management, massive concurrency, easy logging), unless you know what you're doing I would highly suggest using another wrapper ([aiosu](https://github.com/NiceAesth/aiosu), [ossapi](https://github.com/circleguard/ossapi))

Main features
-------------

- Built with high concurrency in mind (thread safe, coroutine safe)
- Optional async support
- Reusable Oauth2 token (api v2)
- Automatic Oauth2 token refresh (api v2)
- Built-in rate limiting
- Built-in thread support
- Response validation (pydantic)

Installation
------------

Development setup
```bash
$ git clone https://github.com/miinorii/circleapi.git
$ cd circleapi
$ python -m venv venv
$ venv/bin/activate # linux
$ venv/Scripts/activate.bat # windows
$ pip install -r requirements.txt
$ pip install -e .
```

Endpoints
---------

- osu api v2
  - beatmap_lookup
  - get_user_beatmap_score
  - get_user_beatmap_scores
  - get_beatmap_scores
  - get_beatmaps
  - get_beatmap
  - get_beatmap_attributes
  - get_score
- osu.lea.moe
  - get_ranked_ids
  - get_loved_ids
  - get_ranked_and_loved_ids






