import xml.etree.ElementTree as ET

from pulseq2jemris.genericpulse import GenericPulse
from pulseq2jemris.genericseq import GenericSeq


class JSeqTree():
    def __init__(self):
        self.parameters = None
        self.concat_seq = None
        # Dictionary to keep track of sequence and pulse numbering
        self.seq_numbering = {'C': 1, 'A': 1, 'D': 1, 'P': 1}

    def __doc__(self):
        help_str = "pulseq2jemris:\n---\n"
        help_str += "Functions:\n"
        help_str += "add_to_concat():" + self.add_to_concat.__doc__ + "\n"
        help_str += "add_to_atomic():" + self.add_to_atomic.__doc__ + "\n"
        help_str += "make_rf_pulse():" + self.make_rf_pulse.__doc__ + "\n"
        help_str += "make_trap_grad_pulse():" + self.make_trap_grad_pulse.__doc__ + "\n"
        help_str += "make_delay():" + self.make_delay.__doc__ + "\n"
        help_str += "make_adc():" + self.make_adc().__doc__ + "\n"
        help_str += "make_seq_tree():" + self.make_seq_tree().__doc__ + "\n"
        help_str += "write_xml():" + self.write_xml().__doc__
        return help_str

    def __make_concat_seq(self, kwargs):
        """
        Returns a GenericSeq object of type 'C'.

        Parameters
        ----------
        rep : int
            Number of repetitions for the ConcatSequence module.

        Returns
        -------
        concat_seq : GenericSeq
            Instance of GenericSeq of type 'C'.
        """

        if not isinstance(kwargs, dict):
            raise TypeError("Illegal arguments. make_concat_seq takes one dict parameter, that contains key-value "
                            "pair mappings of parameters_params.")

        concat_seq = GenericSeq()
        concat_seq.type = 'C'
        concat_seq.Name = 'C' + str(self.seq_numbering['C'])
        for k, v in kwargs.items():
            setattr(concat_seq, k, str(v))
        self.seq_numbering['C'] += 1

        return concat_seq

    def add_to_concat(self, kwargs, *events):
        """
        Returns a ConcatSequence object that wraps one or more ConcatSequence(s) or AtomicSequence(s).

        Parameters
        ----------
        kwargs : dict
            Key-value pairs of ConcatSequence parameters_params and values.
        events : list
            List of GenericSeq objects that need to be wrapped in the ConcatSequence.

        Returns
        -------
        concat_seq : GenericSeq
            GenericSeq instance wrapping the other GenericPulse children.
        """

        concat_seq = self.__make_concat_seq(kwargs)
        for event in events:
            if not isinstance(event, GenericSeq):
                raise TypeError(
                    "Illegal arguments. add_to_concat() takes at least 2 arguments: dict, GenericSeq [, "
                    "GenericSeq1...]. You have passed arguments of type: " + str(type(event)))
            concat_seq.events.append(event)

        return concat_seq

    def __make_atomic_seq(self):
        """
        Returns a GenericSeq object of type 'A'.

        Returns
        -------
        atomic_seq : GenericSeq
            GenericSeq object of type 'A'.
        """

        atomic_seq = GenericSeq()
        atomic_seq.type = 'A'
        atomic_seq.Name = 'A' + str(self.seq_numbering['A'])
        self.seq_numbering['A'] += 1

        return atomic_seq

    def add_to_atomic(self, *events):
        """
        Wraps one or more GenericPulse(s) in an AtomicSequence.

        Parameters
        ----------
        events : list of GenericPulse objects
            GenericPulse objects.

        Returns
        -------
        atomic_seq : GenericSeq
            GenericSeq object containing the GenericPulse events.
        """

        atomic_seq = self.__make_atomic_seq()
        for event in events:
            if not isinstance(event, GenericPulse):
                raise TypeError(
                    "Illegal arguments. add_to_atomic() takes at least 1 argument: GenericPulse [, GenericPulse1...]. "
                    "You have passed arguments of type: " + str(type(event)))

            atomic_seq.events.append(event)
        return atomic_seq

    def make_rf_pulse(self, rf_kwargs):
        """
        Returns a GenericPulse of type 'SincRfPulse'.

        Parameters
        ----------
        rf_kwargs : list of dicts
            Each dict describes a RF event.

        Returns
        -------
        rf_pulse : GenericPulse
            'SincRFPulse' GenericPulse object that has been configured appropriately.
        """
        # Raise exception if dict is not passed
        if not isinstance(rf_kwargs, dict):
            raise TypeError(
                "Illegal arguments. make_rf_pulse() takes one or more dict arguments.")

        rf_pulse = GenericPulse()
        rf_pulse.type = 'SincRFPulse'
        rf_pulse.Name = 'P' + str(self.seq_numbering['P'])

        for k, v in rf_kwargs.items():
            k = 'Axis' if k == 'Channel' else k
            setattr(rf_pulse, k, str(v))
        self.seq_numbering['P'] += 1
        return rf_pulse

    def make_trap_grad_pulse(self, trap_kwargs):
        """
        Returns a GenericPulse of type 'TrapGradPulse'.

        Parameters
        ----------
        trap_kwargs : list of dicts
            Each dict describes a Trap event.

        Returns
        -------
        trap_pulse : GenericPulse
            'TrapGradPulse' GenericPulse object that has been configured appropriately.
        """
        # Raise exception if dict is not passed
        if not isinstance(trap_kwargs, dict):
            raise TypeError(
                "Illegal arguments. make_trap_grad_pulse() takes one or more dict arguments.")
        trap_pulse = GenericPulse()
        trap_pulse.type = 'TrapGradPulse'
        trap_pulse.Name = 'P' + str(self.seq_numbering['P'])

        for k, v in trap_kwargs.items():
            setattr(trap_pulse, k, str(v))
        self.seq_numbering['P'] += 1
        return trap_pulse

    def make_delay(self, delay_kwargs):
        """
        Returns a GenericSeq of type 'D'.

        Parameters
        ----------
        delay_kwargs : list of dicts
            Each dict describes a Delay event.

        Returns
        -------
        delay_seq : GenericSeq
            'D' GenericSeq object that has been configured appropriately.
        """
        # Raise exception if dict is not passed
        if not isinstance(delay_kwargs, dict):
            raise TypeError(
                "Illegal arguments. make_delay() takes one or more dict arguments.")
        delay_seq = GenericSeq()
        delay_seq.type = 'D'
        delay_seq.Name = 'D' + str(self.seq_numbering['D'])
        for k, v in delay_kwargs.items():
            setattr(delay_seq, k, str(v))
        self.seq_numbering['D'] += 1

        return delay_seq

    def make_adc(self, adc_kwargs):
        """"
        Returns a GenericPulse of type 'TrapGradPulse'.

        Parameters
        ----------
        num_samples : int
            Number of readout samples.

        Returns
        -------
        adc_pulse : GenericPulse
            'TrapGradPulse' GenericPulse object that has been configured appropriately.
        """
        # Raise exception if dict is not passed
        if not isinstance(adc_kwargs, dict):
            raise TypeError(
                "Illegal arguments. make_adc() takes one or more dict arguments.")
        adc_pulse = GenericPulse()
        adc_pulse.type = 'TrapGradPulse'
        adc_pulse.Name = 'P' + str(self.seq_numbering['P'])

        for k, v in adc_kwargs.items():
            setattr(adc_pulse, k, str(v))
        self.seq_numbering['P'] += 1
        return adc_pulse

    def make_seq_tree(self, kwargs, concat_seq):
        """
        Takes system limits and a root ConcatSequence to make the 'Parameters' root node of the XML tree.

        Parameters
        ----------
        concat_seq : GenericSeq
            The root ConcatSequence node in the XML tree.
        FOV : int, optional
            Field of view.
        Nx : int, optional
            Nx.
        Ny : int, optional
            Ny.
        TE : int, optional
            Time to echo.
        TR : int, optional
            Time to repeat.
        """

        if not isinstance(concat_seq, GenericSeq) or concat_seq.type != 'C':
            raise TypeError(
                "Illegal arguments. First argument to make_seq_tree() has to be ConcatSequence")

        p = GenericSeq()
        p.type = 'P'
        p.Name = "P"
        for k, v in kwargs.items():
            setattr(p, k, str(v))

        self.parameters = p
        self.concat_seq = concat_seq

    def write_xml(self, file_name):
        """
        Writes XML file.

        Parameters
        ----------
        file_name : str
            Name of XML file to be written.
        """

        file_name += '.xml' if '.xml' not in file_name else ''
        if file_name[-4:] == '.xml':
            parameter_element = ET.Element('Parameters', attrib=self.parameters.make_attrib())
            self.__expand_concat(parameter_element, self.concat_seq)
            xml_tree = ET.ElementTree(parameter_element)
            xml_tree.write(file_name)

    def __expand_concat(self, param_parent_node, concat_seq):
        """
        Takes a GenericSeq object of type 'P' (called Parameter object) and a GenericSeq object of type 'C' (called
        ConcatSequence object), and recursively expands the ConcatSequence node to build the XML tree.

        Parameters
        ----------
        param_parent_node : GenericSeq
            GenericSeq of type 'P' that represents the 'Parameters' node in the Jemris-readable XML file.
        concat_seq : GenericSeq
            GenericSeq of type 'C' containing children that have to be visited (if need be) and added.

        Returns
        -------
        seq_tree : ET.SubElement
            ET.SubElement object.
        """

        # Dict that contains key-value mappings of pulse/sequence shorthand notations to their complete notations.
        self.xml_tags = {"A": "ATOMICSEQUENCE", "C": "ConcatSequence", "D": "DELAYATOMICSEQUENCE",
                         "SincRFPulse": "HARDRFPULSE", "TrapGradPulse": "TRAPGRADPULSE", "ADC": "TRAPGRADPULSE"}
        seq_tree = ET.SubElement(param_parent_node, 'ConcatSequence', attrib=concat_seq.make_attrib())
        for event in concat_seq.events:
            if event.type == 'C':
                self.__expand_concat(seq_tree, event)
            elif event.type == 'A':
                atomic_seq = ET.SubElement(seq_tree, self.xml_tags[event.type], attrib=event.make_attrib())
                for pulse in event.events:
                    if pulse.type == 'SincRFPulse':
                        ET.SubElement(atomic_seq, self.xml_tags[pulse.type], attrib=pulse.make_attrib())
                    elif pulse.type == 'TrapGradPulse':
                        ET.SubElement(atomic_seq, self.xml_tags[pulse.type], attrib=pulse.make_attrib())
                    elif pulse.type == 'ADC':
                        ET.SubElement(atomic_seq, self.xml_tags[pulse.type], attrib=pulse.make_attrib())
            elif event.type == 'D':
                ET.SubElement(seq_tree, self.xml_tags[event.type], attrib=event.make_attrib())

        return seq_tree

    def get_j_attrib(self, obj, attr):
        """
        Returns the required attribute.
        
        Parameters
        ----------
        obj : GenericPulse/GenericSeq
            Object whose attrib is required to be retrieved.
        attr : str
            The attribute that is to be retrieved from obj.
            
        Returns
        -------
        float
            Attribute attr of obj.
        """
        if not isinstance(obj, GenericPulse) or not isinstance(obj, GenericSeq):
            raise TypeError("Illegal arguments. get_j_attrib() takes exactly two arguments: GenericPulse, attrib or "
                            "GenericSeq, attrib. You passed arguments of type: " + str(type(obj)) + " and " + str(
                type(attr)))
        return float(getattr(obj, attr))
