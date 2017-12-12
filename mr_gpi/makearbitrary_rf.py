from math import pi

import numpy as np

from mr_gpi.holder import Holder
from mr_gpi.maketrap import maketrapezoid
from mr_gpi.opts import Opts


def makearbitraryrf(kwargs, nargout=1):
    """
    Makes a Holder object for an arbitrary RF pulse Event.

    Parameters
    ----------
    kwargs : dict
        Key value mappings of RF Event parameters_params and values.
    nargout: int
        Number of output arguments to be returned. Default is 1, only RF Event is returned. Passing any number greater
        than 1 will return the Gz Event along with the RF Event.

    Returns
    -------
    rf : Holder
        RF Event configured based on supplied kwargs.
    gz : Holder
        Slice select trapezoidal gradient Event.
    """

    flip_angle = kwargs.get("flip_angle")
    system = kwargs.get("system", Opts())
    signal = kwargs.get("signal", 0)
    freq_offset = kwargs.get("freq_offset", 0)
    phase_offset = kwargs.get("phase_offset", 0)
    time_bw_product = kwargs.get("time_bw_product", 0)
    bandwidth = kwargs.get("bandwidth", 0)
    max_grad = kwargs.get("max_grad", 0)
    max_slew = kwargs.get("max_slew", 0)
    slice_thickness = kwargs.get("slice_thickness", 0)

    signal = signal / sum(signal * system.rf_raster_time) * flip_angle / (2 * pi)
    N = len(signal)
    duration = N * system.rf_raster_time
    t = [x * system.rfRasterTime for x in range(0, N)]

    rf = Holder()
    rf.type = 'rf'
    rf.signal = signal
    rf.t = t
    rf.freq_offset = freq_offset
    rf.phase_offset = phase_offset
    rf.rf_dead_time = system.rf_dead_time

    if nargout > 1:
        if slice_thickness <= 0:
            raise ValueError('Slice thickness must be provided')
        if bandwidth <= 0:
            raise ValueError('Bandwdith of pulse must be provided')

        system.maxgrad = max_grad if max_grad > 0 else system.maxgrad
        system.max_slew = max_slew if max_slew > 0 else system.max_slew

        BW = bandwidth
        if time_bw_product > 0:
            BW = time_bw_product / duration

        amplitude = BW / slice_thickness
        area = amplitude * duration
        kwargs_for_trap = {"channel": 'z', "system": system, "flat_time": duration, "flat_area": area}
        gz = maketrapezoid(**kwargs_for_trap)

        t_fill = [x * 1e-6 for x in range(1, round(gz.riseTime / 1e-6))]
        rf.t = [t_fill, rf.t + t_fill[-1], t_fill + rf.t[-1] + t_fill[-1]]
        rf.signal = [np.zeros(len(t_fill)), rf.signal, np.zeros(len(t_fill))]

    return rf, gz
