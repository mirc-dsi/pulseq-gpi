import numpy as np

from mr_gpi.holder import Holder


def compress_shape(decompressed_shape):
    """
    Returns a run-length encoded compressed shape.

    Parameters
    ----------
    decompressed_shape : ndarray
        Decompressed shape.

    Returns
    -------
    compressed_shape : Holder
        A Holder object containing the shape of the compressed shape ndarray and the compressed shape ndarray itself.
    """

    if decompressed_shape.shape[0] != 1:
        raise ValueError("input should be of shape (1,x)")
    if not isinstance(decompressed_shape, np.ndarray):
        raise TypeError("input should be of type numpy.ndarray")

    data = np.array([decompressed_shape[0][0]])
    data = np.concatenate((data, np.diff(decompressed_shape[0])))

    mask_changes = np.array([1])
    diff_as_ones = (abs(np.diff(data)) > 1e-8).astype(int)
    mask_changes = np.concatenate((mask_changes, diff_as_ones))
    vals = data[np.nonzero(mask_changes)].astype(float)
    k = np.array(np.nonzero(np.append(mask_changes, 1)))
    k = k.reshape((1, k.shape[1]))
    n = np.diff(k)[0]

    n_extra = (n - 2).astype(float)
    vals2 = np.copy(vals)
    vals2[np.where(n_extra < 0)] = np.NAN
    n_extra[np.where(n_extra < 0)] = np.NAN
    v = np.array([vals, vals2, n_extra])
    v = np.concatenate(np.hsplit(v, v.shape[1]))
    finite_vals = np.isfinite(v)
    v = v[finite_vals]
    v_abs = abs(v)
    smallest_indices = np.where(v_abs < 1e-10)
    v[smallest_indices] = 0

    compressed_shape = Holder()
    compressed_shape.num_samples = decompressed_shape.shape[1]
    compressed_shape.data = v.reshape([1, v.shape[0]])
    return compressed_shape
