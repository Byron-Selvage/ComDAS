"""
Implements NumPy-like array (duck array) [duckarrays]_ to hold compressed Patch data.
.. [duckarrays] https://docs.xarray.dev/en/stable/user-guide/duckarrays.html
"""

from __future__ import annotations

import itertools

import numpy as np

from comdas.codecs.base import Codec, CompressedPayload

class DuckArray(np.lib.mixins.NDArrayOperatorsMixin):
    """
    A NumPy-like duck array backed by a compressed payload and codec defining
    how the data is compressed and decompressed.

    Reads are performed via ``codec.decode_partial``. Writes go into a
    sparse overlay dict rather than immediately forcing a complete recompression
    of the underlying compressed payload. :meth:`consolidate` can be called to
    merge the overlay into the compressed payload. :meth:`consolidate` will be
    called automatically when the number of pending writes exceeds the codec's
    specified maximum number of pending writes.

    If the specified codec implements partial writes efficiently, the codec's
    partial writes function will always be used to update the compressed
    payload without accumulation.

    :param payload: The compressed payload backing this duck array.
    :type payload: CompressedPayload
    :param codec: The codec defining how the data is compressed and decompressed.
    :type codec: Codec
    :param max_pending_writes: Maximum number of pending writes before automatic
        consolidation.
    :type max_pending_writes: int or None
    """

    def __init__(
        self,
        payload: CompressedPayload,
        codec: Codec,
        *,
        max_pending_writes: int | None = None,
    ):
        self._payload = payload
        self._codec = codec
        self._overlay: dict[tuple[int, ...], object] = {}
        self._max_pending_writes = (
            max_pending_writes
            if max_pending_writes is not None
            else codec.max_pending_writes
        )

    # Array basics
    @property
    def shape(self) -> tuple[int, ...]:
        """
        Get the shape of the decompressed/original array.

        :rtype: tuple[int, ...]
        """
        return self._payload.original_shape

    @property
    def dtype(self) -> np.dtype:
        """
        Get the data type of the decompressed/original array.

        :rtype: numpy.dtype
        """
        return self._payload.dtype

    @property
    def ndim(self) -> int:
        """
        Get the number of dimensions of the decompressed/original array.

        :rtype: int
        """
        return len(self.shape)

    def __len__(self) -> int:
        return self.shape[0]

    @property
    def payload(self) -> CompressedPayload:
        """
        Get the current compressed payload backing this array.

        :rtype: CompressedPayload
        """
        return self._payload

    @property
    def codec(self) -> Codec:
        """
        Get the codec used to encode/decode :attr:`payload`.

        :rtype: Codec
        """
        return self._codec

    @property
    def overlay_size(self) -> int:
        """
        Get the number of elements currently held in the write overlay.

        :rtype: int
        """
        return len(self._overlay)

    def __array__(self, dtype=None) -> np.ndarray:
        """
        Fully materialize this array as a dense NumPy array.

        :param dtype: Optional dtype to cast the result to.
        :type dtype: numpy.dtype or None
        :returns: The decompressed array, with any pending overlay
            writes applied.
        :rtype: numpy.ndarray
        """
        out = self._codec.decode(self._payload).copy()
        for idx, val in self._overlay.items():
            out[idx] = val
        if dtype is not None:
            out = out.astype(dtype, copy=False)
        return out

    def __array_function__(self, func, types, args, kwargs):
        """
        Apply a numpy function to this array. Decompresses the
        array before applying the NumPy function.

        NOTE: Some codecs support efficient operations directly
        on the compressed representation. We should provide a way
        to implement these in the future.

        NOTE: Applying a chain of functions will decompress the array
        at each step. We should optimize chained operations to avoid
        this.

        :param func: The NumPy function being dispatched.
        :param types: Types of the arguments involved.
        :param args: Positional arguments to ``func``.
        :param kwargs: Keyword arguments to ``func``.
        :returns: The result of calling ``func`` on materialized arrays.
        """
        args = [np.asarray(a) if isinstance(a, DuckArray) else a for a in args]
        return func(*args, **kwargs)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        """
        Materializes the array then applies the ufunc.

        NOTE: We should explore per-codec optimizations.

        :param ufunc: The NumPy ufunc being dispatched.
        :param method: The ufunc method being called (e.g. ``"__call__"``).
        :param inputs: Positional inputs to the ufunc.
        :param kwargs: Keyword arguments to the ufunc.
        :returns: The result of calling the ufunc on materialized arrays.
        """
        inputs = [np.asarray(i) if isinstance(i, DuckArray) else i for i in inputs]
        return getattr(ufunc, method)(*inputs, **kwargs)

    def __repr__(self) -> str:
        ratio = self._codec.compression_ratio(self._payload)
        return (
            f"DuckArray(shape={self.shape}, dtype={self.dtype}, "
            f"codec={type(self._codec).__name__}, ratio={ratio:.1f}x, "
            f"overlay={self.overlay_size})"
        )

    def _key_to_index_lists(self, key) -> list[list[int]]:
        """
        Normalize a NumPy-style key into per-axis integer index lists.

        :param key: A NumPy-style index/slice key.
        :returns: One list of concrete integer indices per axis.
        :rtype: list[list[int]]
        """
        if not isinstance(key, tuple):
            key = (key,)
        key = key + (slice(None),) * (self.ndim - len(key))
        axes: list[list[int]] = []
        for k, dim in zip(key, self.shape):
            if isinstance(k, (int, np.integer)):
                axes.append([int(k)])
            elif isinstance(k, slice):
                axes.append(list(range(*k.indices(dim))))
            else:
                axes.append(np.atleast_1d(np.asarray(k)).tolist())
        return axes

    @staticmethod
    def _normalize_key(key, ndim: int) -> tuple:
        """
        Pad ``key`` with trailing full slices to length ``ndim``.

        :param key: A NumPy-style index/slice key.
        :param ndim: Number of dimensions to pad to.
        :type ndim: int
        :returns: The normalized, tuple-form key.
        :rtype: tuple
        """
        if not isinstance(key, tuple):
            key = (key,)
        return key + (slice(None),) * (ndim - len(key))

    def __getitem__(self, key):
        """
        Read values from the array.

        :param key: A NumPy-style index/slice key.
        :returns: The requested subset of the array.
        :rtype: numpy.ndarray or scalar
        """
        if not self._overlay:
            return self._codec.decode_partial(self._payload, key)

        axes = self._key_to_index_lists(key)
        axes_sets = [set(a) for a in axes]
        touched = [
            (idx, val)
            for idx, val in self._overlay.items()
            if all(idx[d] in axes_sets[d] for d in range(self.ndim))
        ]
        base = np.array(self._codec.decode_partial(self._payload, key), copy=True)
        if not touched:
            return base

        norm_key = self._normalize_key(key, self.ndim)
        for idx, val in touched:
            local = tuple(
                axes[d].index(idx[d])
                for d, k in enumerate(norm_key)
                if not isinstance(k, (int, np.integer))
            )
            base[local] = val
        return base

    def __setitem__(self, key, value) -> None:
        """
        Write a value. Attempts to not decompress the entire array if possible.

        Three strategies are tried, in order:

        1. If the codec implements :meth:`~comdas.codecs.base.Codec.partial_write`,
           it's used directly. In this case, the payload is patched in place.
           A codec may raise :class:`NotImplementedError` for a particular ``key``
           it can't handle (e.g. it only supports single elements), in
           this case it goes to strategy 2 for that call.
        2. Otherwise, small writes land in a sparse overlay dict,
           applied on read and folded in by :meth:`consolidate`.
        3. A write that touches more than
           :attr:`~comdas.codecs.base.Codec.max_pending_writes`
           elements or would push the overlay size past it auto-consolidates
           instead.

        :param key: A NumPy-style index/slice key.
        :param value: The value(s) to write; broadcast against the
            shape implied by ``key``, matching normal NumPy assignment.
        """
        if self._codec.supports_partial_write():
            try:
                self._payload = self._codec.partial_write(self._payload, key, value)
                return
            except NotImplementedError:
                pass

        axes = self._key_to_index_lists(key)
        size = 1
        for a in axes:
            size *= len(a)

        if size > self._max_pending_writes or (self.overlay_size + size) > self._max_pending_writes:
            dense = self.__array__()
            dense[key] = value
            self.consolidate(dense=dense)
            return

        indices = list(itertools.product(*axes))
        values = np.broadcast_to(value, tuple(len(a) for a in axes)).ravel()
        for idx, val in zip(indices, values):
            self._overlay[idx] = val

    def consolidate(
        self,
        *,
        dense: np.ndarray | None = None,
        **encode_kwargs,
    ) -> None:
        """
        Fold the write overlay into a freshly-compressed payload.

        By default, re-encodes using whatever compression level the
        current payload already used.

        :param dense: Precomputed dense array to encode, if the
            caller already has one.
        :type dense: numpy.ndarray or None
        :param encode_kwargs: Additional codec-specific kwargs
            forwarded to ``codec.encode``.
        """
        if dense is None:
            dense = self.__array__()

        encode_kwargs = self._payload.compression_params

        self._payload = self._codec.encode(dense, **encode_kwargs)
        self._overlay.clear()
