# Mastodon #eqnz bot

This bot attempts to replicate for mastodon what [@geonet@twitter.com](https://twitter.com/geonet) and [@nz_quake@twitter.com](https://twitter.com/nz_quake) do on twitter: timely earthquake reporting. It is written in Python 3, and polls the [Geonet API](https://api.geonet.org.nz/).

## Setup

Posting to mastodon requires an account on a mastodon server (see [joinmastodon.org](https://joinmastodon.org/)), the [Mastodon.py](https://github.com/halcy/Mastodon.py) python module, and a `usercred.secret` file.

The `mastodon.py` module can be installed with e.g. `pip install --user Mastodon.py`. The secret file can most easily be generated via [this python script](https://gist.github.com/PetraOleum/5ebe6f0cc238df56615d086fc061eb14), e.g.:

```
python setupclient.py eqnz "https://botsin.space" "bot@example.com"
```

The script will prompt for a password and, if successful, will produce `eqnz_clientcred.secret` and `eqnz_usercred.secret` files.

## Running

Basic operation is e.g.:

```
python eqnz.py --secret eqnz_usercred.secret --mmi 3
```

This polls the API once every 30 seconds, for earthquakes with a Modified Mercalli Intensity of III or higher (weak and up), and posts to the mastodon account associated with the secret file.

This could probably be put into a systemd service file, but for now I leave this as an example to the user.

## Volcano bot

`volcano.py` checks the alert level of New Zealand's volcanoes and, if they have changed, posts to mastodon. To run with a `pyenv` virtualenvironment and `cron`, I suggest a wrapper script along the lines of:

```
*/15 * * * * /home/petra/runvolc >> /home/petra/volclog.txt 2>&1
```

**runvolc**:

```
#! /bin/bash

export PATH="/home/petra/.pyenv/bin:$PATH"
export PYENV_VIRTUALENV_DISABLE_PROMPT=1
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

cd /home/petra/eqnz-mastodon
pyenv activate eqnzvenv
python volcano.py
```
