"""Decorator for python application cache methods."""

import ast
import hashlib
import logging
import pickle
import pprint
from functools import wraps
from inspect import getcallargs
from typing import Union

from gcp_commons_utils.gcp_cache.cacher import CacherInterface

LOGGER = logging.getLogger(__name__)


# noinspection PyBroadException
class CacheDef:
    """
    Decorator responsible for making a cache.

    Decorator responsible for making a cache of the results of calling a
    method in accordance with the reported.

    :arg seed: Name of the cache
    :arg cacher: The system where the cache will be saved, must be an instance of CacherInterface
    :arg minute_expire: Time in minutes for validity of cache
    :arg debug: Active debug mode
    :arg ftype: Format to store the cache ('pickle', 'literal')
    :arg hash_format: Format of hash when using filesystem
    """

    def __init__(
        self,
        cacher: CacherInterface,
        seed: str = None,
        minute_expire: int = 60 * 24 * 7,
        debug: bool = False,
        ftype: str = 'pickle',
        hash_format: str = '%(md5)s'
    ):
        """Class constructor."""
        LOGGER.debug(
            f"Received variables: seed=[{seed}] - cacher=[{cacher}] - minute_expire=["
            f"{minute_expire}] - debug=[{debug}] - ftype=[{ftype}] - hash_format=[{hash_format}]"
        )

        self.seed = seed
        self.cacher = cacher
        self.seconds_expire = minute_expire * 60 if minute_expire >= 1 else 60 * 60 * 24 * 7
        self.debug = debug
        self.ftype = ftype
        self.hash_format = hash_format
        self._config = {}

    @property
    def config(self):
        """Getter for config property."""
        if not self._config:
            self._config = {
                "seed": self.seed,
                "cacher": self.cacher,
                "seconds_expire": self.seconds_expire,
                "debug": self.debug,
                "ftype": self.ftype,
                "hash_format": self.hash_format,
            }
            LOGGER.debug("Setting values for config. [%s]" % self._config)
        LOGGER.debug("Returning values for config. [%s]" % self._config)
        return self._config

    def __call__(self, call, *args, **kwargs):
        """Intercept the all calls for the cached method."""
        LOGGER.info("Call for cache_def.")
        config = self.config.copy()

        @wraps(call)
        def new_def(*in_args, **in_kwargs):

            if self.cacher is None:
                LOGGER.warning("CacheDef::cache_def: WARNING NO CACHE IS BEING USED!")
                return call(*in_args, **in_kwargs)

            if self.seed is None:
                self.seed = call.__qualname__.replace("<", "").replace(">", "").replace(".", "::")
                self.seed += f"::{int(self.seconds_expire / 60)}"
            resp = None

            call_kwargs = getcallargs(call, *in_args, **in_kwargs)
            if 'self' in call_kwargs:
                call_kwargs.pop('self')
            cache_hash = self._generate_hash(config=config, kwargs=call_kwargs)
            cache_key = 'cache:' + cache_hash

            if not kwargs.get('renew_cache'):
                resp = self.cacher.get_cache(self.seed, cache_key, self.seconds_expire)
                resp = self.loads(resp)
                LOGGER.info(['sbox_cache', 'get cache', self.seed])

            if resp is None:
                LOGGER.info(['sbox_cache', 'no cache', self.seed])

                # Make the normal call to the function
                resp = call(*in_args, **in_kwargs)

                # Set the cache
                # thread BIG QUERY
                self.cacher.set_cache(self.seed, cache_key, self.dumps(resp))
                LOGGER.info(['sbox_cache', 'save cache', self.seed])
            return resp
        return new_def

    def loads(self, element):
        """Serialize the element retrieved from cacher."""
        if element is None:
            return element
        if self.ftype == 'pickle':
            return pickle.loads(element)
        if self.ftype == 'literal':
            return ast.literal_eval(element)
        raise TypeError(f"Type of {self.ftype} not supported.")

    def dumps(self, element):
        """Deserialize the element to save in the cacher."""
        if self.ftype == 'pickle':
            return pickle.dumps(element)
        if self.ftype == 'literal':
            r = pprint.pformat(element).encode('utf-8')
            return r
        raise TypeError(f"Type of {self.ftype} not supported.")

    def _generate_hash(self, config, kwargs):
        LOGGER.info(f"GENERATING CACHE_HASH....")
        LOGGER.debug(['sbox_cache', '_gera_hash::kwargs', kwargs])

        if 'renew_cache' in kwargs:
            kwargs.pop('renew_cache')

        s = self.seed + str(self.seconds_expire) + pprint.pformat([kwargs])

        if hasattr(s, 'encode'):
            s = s.encode('utf-8')

        hash_format = config.get('hash_format')
        hash_key = hash_format % dict(md5=hashlib.md5(s).hexdigest(), **kwargs)

        LOGGER.debug(['sbox_cache', '_gera_hash', hash_key])
        LOGGER.debug(f"CACHE_HASH = {hash_key}")
        return hash_key


def cache_def(
    cacher: Union[CacherInterface, None],
    seed: str = None,
    minute_expire: int = 60,
    debug: bool = False,
    ftype: str = 'pickle',
    hash_format: str = '%(md5)s'
):
    """
    Decorator responsible for making a cache.

    Decorator responsible for making a cache of the results
    of calling a method in accordance with the reported.

    :arg seed: Name of the cache
    :arg cacher: The system where the cache will be saved, must be an instance of CacherInterface
    :arg minute_expire: Time in minutes for validity of cache
    :arg debug: Active debug mode
    :arg ftype: Format to store the cache ('pickle', 'literal')
    :arg hash_format: Format of hash when using filesystem
    """
    return CacheDef(
        cacher=cacher,
        seed=seed,
        minute_expire=minute_expire,
        debug=debug,
        ftype=ftype,
        hash_format=hash_format,
    )


def clear_cache(seed: str, cacher: CacherInterface):
    """Remove the cache based on it seed."""

    return cacher.clear_cache(seed)


def clear_all_cache(cacher: CacherInterface) -> bool:
    """Remove all cache from the given gacher."""

    return cacher.clear_all_cache()
