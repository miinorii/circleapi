circleapi
---------

Yet another python wrapper for osu! api

That wrapper was tailored for my needs (token management, massive concurrency, easy logging), unless you know what you're doing I would highly suggest using another wrapper ([aiosu](https://github.com/NiceAesth/aiosu), [ossapi](https://github.com/circleguard/ossapi))

Main features
-------------

- Reusable Oauth2 token (api v2)
- Automatic Oauth2 token refresh (api v2)
- Configurable rate limit
- Built-in thread support
- Response validation (pydantic)

Installation
------------

Development setup
```bash
$ git clone https://github.com/miinorii/circleapi.git
$ cd circleapi
$ python -m venv venv
$ venv/bin/activate
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






