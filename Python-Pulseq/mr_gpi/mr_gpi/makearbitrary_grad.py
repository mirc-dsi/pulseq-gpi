import numpy as np

from mr_gpi.holder import Holder
from mr_gpi.opts import Opts


def makearbitrarygrad(kwargs):
    """
    Makes a Holder object for an arbitrary gradient Event.

    Parameters
    ----------
    kwargs : dict
        Key value mappings of RF Event parameters_params and values.

    Returns
    -------
    grad : Holder
        Trapezoidal gradient Event configured based on supplied kwargs.
    """

    channel = kwargs.get("channel", "z")
    system = kwargs.get("system", Opts())
    waveform = kwargs.get("waveform")
    max_grad_result = kwargs.get("max_grad", 0)
    max_slew_result = kwargs.get("max_slew", 0)

    max_grad = max_grad_result if max_grad_result > 0 else system.max_grad
    max_slew = max_slew_result if max_slew_result > 0 else system.max_slew

    g = waveform
    slew = (g[0][1:] - g[0][0:-1]) / system.grad_raster_time
    if max(abs(slew)) > max_slew:
        raise ValueError('Slew rate violation {:f}'.format(max(abs(slew)) / max_slew * 100))
    if max(abs(g[0])) > max_grad:
        raise ValueError('Gradient amplitude violation {:f}'.format(max(abs(g)) / max_grad * 100))
    grad = Holder()
    grad.type = 'grad'
    grad.channel = channel
    grad.waveform = g
    grad.t = np.array([[x * system.grad_raster_time for x in range(len(g[0]))]])
    return grad
