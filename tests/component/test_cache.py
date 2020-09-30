"""Component test for cache_def."""
import time
from gcp_commons_utils.gcp_cache import cache_def, clear_cache
from gcp_commons_utils.gcp_cache.cacher import RedisCacher


def test_call_on_cache_def():
    """Test if method are called when cache does not exists."""
    start = time.time()
    redis_caching = RedisCacher(host="127.0.0.1")
    seed = "testing"
    clear_cache(seed, redis_caching)

    @cache_def(cacher=redis_caching, minute_expire=1)
    def cache_test(a, b):
        time.sleep(5)
        return a * b

    resp = cache_test(2, 4)
    duration = (time.time() - start)
    assert resp == 8
    assert duration >= 5


def test_call_multiple_times():
    """Test if cache are valid when calling the method multiple times and in different ways."""
    start = time.time()
    redis_caching = RedisCacher(host="127.0.0.1")
    seed = "testing"
    clear_cache(seed, redis_caching)

    @cache_def(seed="testing", cacher=redis_caching, minute_expire=1)
    def cache_test(a, b):
        time.sleep(5)
        return a * b

    resp = (
        cache_test(2, 4),
        cache_test(a=2, b=4),
        cache_test(2, b=4),
        cache_test(b=4, a=2)
    )
    duration = (time.time() - start)

    assert resp == (8, 8, 8, 8)
    assert duration <= 7


def test_multiple_call_different_param():
    """Test if cache are different for method when parameters are different."""
    start = time.time()
    redis_caching = RedisCacher(host="127.0.0.1")
    seed = "testing"
    clear_cache(seed, redis_caching)

    @cache_def(seed="testing", cacher=redis_caching, minute_expire=1)
    def cache_test(a, b):
        time.sleep(5)
        return a * b

    resp = (
        cache_test(a=2, b=4),
        cache_test(2, b=7),
        cache_test(2, 8),

        cache_test(2, 4),
        cache_test(b=7, a=2),
        cache_test(a=2, b=8),
    )
    duration = (time.time() - start)

    assert resp == (8, 14, 16, 8, 14, 16)
    assert duration >= 15 <= 17


def test_clear_cache():
    """Test if cache are cleared."""
    start = time.time()
    redis_caching = RedisCacher(host="127.0.0.1")
    seed = "testing"
    clear_cache(seed, redis_caching)

    @cache_def(seed="testing", cacher=redis_caching, minute_expire=1)
    def cache_test(a, b):
        time.sleep(5)
        return a * b

    resp = cache_test(a=2, b=4)
    assert resp == 8

    clear_cache(seed, redis_caching)

    resp = cache_test(a=2, b=4)
    assert resp == 8

    duration = (time.time() - start)

    assert duration >= 10


def test_none_cacher():
    """Test if cacher is None, no cache will be used."""
    start = time.time()
    seed = "testing"

    @cache_def(seed=seed, cacher=None, minute_expire=1)
    def cache_test(a, b):
        time.sleep(5)
        return a * b

    resp = (
       cache_test(a=2, b=5),
       cache_test(2, 5)
    )

    duration = (time.time() - start)

    assert resp == (10, 10)
    assert duration >= 10
