import hashlib
import json
from typing import Optional

from scoring_api.api.store import KeyValueStore


def get_score(
    store: KeyValueStore,
    phone: Optional[str | int],
    email: Optional[str],
    birthday: Optional[str] = None,
    gender: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
) -> float:
    key_parts = [
        first_name or '',
        last_name or '',
        phone or '',
        birthday or '',
    ]
    key = 'uid:' + hashlib.md5(
        ''.join(map(str, key_parts)).encode('utf-8')
    ).hexdigest()
    # try get from cache,
    # fallback to heavy calculation in case of cache miss
    score = store.cache_get(key) or 0
    if score:
        return float(score)
    if phone:
        score += 1.5
    if email:
        score += 1.5
    if birthday and gender:
        score += 1.5
    if first_name and last_name:
        score += 0.5
    # cache for 60 minutes
    store.cache_set(key, score, 60 * 60)
    return score


def get_interests(
    store: KeyValueStore,
    cid: int | float
) -> list[str]:
    r = store.get('i:%s' % cid)
    return json.loads(r) if r else []
