"""Functions copypasted from newer versions of numpy.

"""
from __future__ import division, print_function, absolute_import

import warnings
import sys

import numpy as np
from numpy.testing.nosetester import import_nose

from scipy._lib._version import NumpyVersion


if NumpyVersion(np.__version__) > '1.7.0.dev':
    _assert_warns = np.testing.assert_warns
else:
    def _assert_warns(warning_class, func, *args, **kw):
        r"""
        Fail unless the given callable throws the specified warning.

        This definition is copypasted from numpy 1.9.0.dev.
        The version in earlier numpy returns None.

        Parameters
        ----------
        warning_class : class
            The class defining the warning that `func` is expected to throw.
        func : callable
            The callable to test.
        *args : Arguments
            Arguments passed to `func`.
        **kwargs : Kwargs
            Keyword arguments passed to `func`.

        Returns
        -------
        The value returned by `func`.

        """
        with warnings.catch_warnings(record=True) as l:
            warnings.simplefilter('always')
            result = func(*args, **kw)
            if not len(l) > 0:
                raise AssertionError("No warning raised when calling %s"
                        % func.__name__)
            if not l[0].category is warning_class:
                raise AssertionError("First warning for %s is not a "
                        "%s( is %s)" % (func.__name__, warning_class, l[0]))
        return result


def assert_raises_regex(exception_class, expected_regexp,
                        callable_obj=None, *args, **kwargs):
    """
    Fail unless an exception of class exception_class and with message that
    matches expected_regexp is thrown by callable when invoked with arguments
    args and keyword arguments kwargs.
    Name of this function adheres to Python 3.2+ reference, but should work in
    all versions down to 2.6.
    Notes
    -----
    .. versionadded:: 1.8.0
    """
    __tracebackhide__ = True  # Hide traceback for py.test
    nose = import_nose()

    if sys.version_info.major >= 3:
        funcname = nose.tools.assert_raises_regex
    else:
        # Only present in Python 2.7, missing from unittest in 2.6
            funcname = nose.tools.assert_raises_regexp

    return funcname(exception_class, expected_regexp, callable_obj,
                    *args, **kwargs)


if NumpyVersion(np.__version__) >= '1.10.0':
    from numpy import broadcast_to
else:
    # Definition of `broadcast_to` from numpy 1.10.0.

    def _maybe_view_as_subclass(original_array, new_array):
        if type(original_array) is not type(new_array):
            # if input was an ndarray subclass and subclasses were OK,
            # then view the result as that subclass.
            new_array = new_array.view(type=type(original_array))
            # Since we have done something akin to a view from original_array, we
            # should let the subclass finalize (if it has it implemented, i.e., is
            # not None).
            if new_array.__array_finalize__:
                new_array.__array_finalize__(original_array)
        return new_array

    def _broadcast_to(array, shape, subok, readonly):
        shape = tuple(shape) if np.iterable(shape) else (shape,)
        array = np.array(array, copy=False, subok=subok)
        if not shape and array.shape:
            raise ValueError('cannot broadcast a non-scalar to a scalar array')
        if any(size < 0 for size in shape):
            raise ValueError('all elements of broadcast shape must be non-'
                             'negative')
        broadcast = np.nditer(
            (array,), flags=['multi_index', 'refs_ok', 'zerosize_ok'],
            op_flags=['readonly'], itershape=shape, order='C').itviews[0]
        result = _maybe_view_as_subclass(array, broadcast)
        if not readonly and array.flags.writeable:
            result.flags.writeable = True
        return result

    def broadcast_to(array, shape, subok=False):
        return _broadcast_to(array, shape, subok=subok, readonly=True)


if NumpyVersion(np.__version__) >= '1.9.0':
    from numpy import unique
else:
    # the return_counts keyword was added in 1.9.0
    def unique(ar, return_index=False, return_inverse=False, return_counts=False):
        """
        Find the unique elements of an array.

        Returns the sorted unique elements of an array. There are three optional
        outputs in addition to the unique elements: the indices of the input array
        that give the unique values, the indices of the unique array that
        reconstruct the input array, and the number of times each unique value
        comes up in the input array.

        Parameters
        ----------
        ar : array_like
            Input array. This will be flattened if it is not already 1-D.
        return_index : bool, optional
            If True, also return the indices of `ar` that result in the unique
            array.
        return_inverse : bool, optional
            If True, also return the indices of the unique array that can be used
            to reconstruct `ar`.
        return_counts : bool, optional
            If True, also return the number of times each unique value comes up
            in `ar`.

            .. versionadded:: 1.9.0

        Returns
        -------
        unique : ndarray
            The sorted unique values.
        unique_indices : ndarray, optional
            The indices of the first occurrences of the unique values in the
            (flattened) original array. Only provided if `return_index` is True.
        unique_inverse : ndarray, optional
            The indices to reconstruct the (flattened) original array from the
            unique array. Only provided if `return_inverse` is True.
        unique_counts : ndarray, optional
            The number of times each of the unique values comes up in the
            original array. Only provided if `return_counts` is True.

            .. versionadded:: 1.9.0

        Notes
        -----
        Taken over from numpy 1.12.0-dev (c8408bf9c).  Omitted examples,
        see numpy documentation for those.

        """
        ar = np.asanyarray(ar).flatten()

        optional_indices = return_index or return_inverse
        optional_returns = optional_indices or return_counts

        if ar.size == 0:
            if not optional_returns:
                ret = ar
            else:
                ret = (ar,)
                if return_index:
                    ret += (np.empty(0, np.bool),)
                if return_inverse:
                    ret += (np.empty(0, np.bool),)
                if return_counts:
                    ret += (np.empty(0, np.intp),)
            return ret

        if optional_indices:
            perm = ar.argsort(kind='mergesort' if return_index else 'quicksort')
            aux = ar[perm]
        else:
            ar.sort()
            aux = ar
        flag = np.concatenate(([True], aux[1:] != aux[:-1]))

        if not optional_returns:
            ret = aux[flag]
        else:
            ret = (aux[flag],)
            if return_index:
                ret += (perm[flag],)
            if return_inverse:
                iflag = np.cumsum(flag) - 1
                inv_idx = np.empty(ar.shape, dtype=np.intp)
                inv_idx[perm] = iflag
                ret += (inv_idx,)
            if return_counts:
                idx = np.concatenate(np.nonzero(flag) + ([ar.size],))
                ret += (np.diff(idx),)
        return ret
