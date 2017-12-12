import gpi
from gpi import QtGui


class ConfigSeqWidgets(gpi.GenericWidgetGroup):
    """A unique widget that display a variable number of StringBoxes depending on the Pulse being configured."""

    valueChanged = gpi.Signal()

    def __init__(self, title, parent=None):
        super(ConfigSeqWidgets, self).__init__(title, parent)
        self.button_names_list = ['Off', 'SincRfPulse', 'HardRfPulse', 'TrapGradPulse', 'TriangleGradPulse']
        self.clicked_button_name, self.clicked_button_index = '', 0
        self.buttons_list, self.string_box_list = [], []

        # Labels for StringBoxes to configure Events
        self.sinc_rf_labels = ['Name', 'Observe', 'ADCs', 'Apodization', 'Bandwidth', 'Axis', 'FlipAngle',
                               'Frequency', 'HardwareMode', 'InitialDelay', 'InitialPhase', 'Refocusing', 'Symmetry',
                               'Vector', ' Zeros']
        self.hard_rf_labels = ['Name', 'Observe', 'ADCs', 'Channel', 'Duration', 'FlipAngle', 'Frequency',
                               'HardwareMode', 'InitialDelay', 'InitialPhase', 'Refocusing', 'Symmetry', 'Vector']
        self.trap_grad_labels = ['Name', 'Observe', 'ADCs', 'Area', 'Asymmetric', 'Axis', 'Duration', 'EddyConvLength',
                                 'EddyCurrents', 'FlatTopArea', 'FlatTopTime', 'Frequency', 'HardwareMode', 'Hide',
                                 'InitialDelay', 'InitialPhase', 'MaxAmpl', 'NLG_field', 'PhaseLock', 'SlewRate']
        self.triangle_grad_labels = ['Name', 'Observe', 'ADCs', 'Amplitude', 'Axis', 'Duration', 'EddyConvLength',
                                     'EddyCurrents', 'HardwareMode', 'Hide', 'InitialDelay', 'InitialPhase', 'MaxAmpl',
                                     'NLG_field', 'PhaseLock', 'TriangleType', 'Vector']

        # Variable to denote the maximum number of StringBoxes to be added; obviously depends on the Event which has the
        # maximum number of configuration parameters_params
        self.num_string_boxes = max(len(self.hard_rf_labels), len(self.trap_grad_labels))

        # First index is None because the first button is 'Off'. Look into event_def['event_values'] in get_val()
        self.labels = [None, self.sinc_rf_labels, self.hard_rf_labels, self.trap_grad_labels, self.triangle_grad_labels]

        self.wdg_layout = QtGui.QGridLayout()
        self.add_event_pushbuttons()
        self.add_config_stringboxes()

        self.setLayout(self.wdg_layout)
        self.buttons_list[0].setChecked(True)

    def add_event_pushbuttons(self):
        """Adding PushButtons for the Pulses."""
        col_count = 0
        for name in self.button_names_list:
            new_button = QtGui.QPushButton(name)
            new_button.setCheckable(True)
            new_button.setAutoExclusive(True)
            new_button.clicked.connect(self.button_clicked)
            new_button.clicked.connect(self.valueChanged)
            # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
            self.wdg_layout.addWidget(new_button, 0, col_count, 1, 1)
            self.buttons_list.append(new_button)
            col_count += 1

    def add_config_stringboxes(self):
        """Adding StringBoxes for configuring the Pulses."""
        for x in range(self.num_string_boxes):
            string_box = gpi.StringBox(str(x))
            string_box.set_visible(False)
            # Syntax: addWidget(widget, row, col, rowSpan, colSpan)
            self.wdg_layout.addWidget(string_box, x + 1, 1, 1, 6)
            self.string_box_list.append(string_box)

    # Getter
    def get_val(self):
        if self.clicked_button_index == self.button_names_list.index('Off'):
            # 'Off' PushButton selected, return empty dict
            return None
        else:
            """
            event_def contains:
            - event_name : str
                Event name, corresponds to Event button that is selected. See make_pulse() in JWriteXML_GPI
            - key-value pairs of Event parameters_params and values
            """
            event_def = {}
            labels = self.labels[self.clicked_button_index]
            for i in range(len(self.string_box_list)):
                val = self.string_box_list[i].get_val()
                if val != '':
                    event_def[labels[i]] = val
            event_def['event_name'] = self.clicked_button_name
            return event_def

    # Setter
    def set_val(self, val):
        self.hide_config_widgets()
        if val is not None and len(val) != 0:
            # If Event is not configured, self.clicked_button_name will be ''
            self.clicked_button_name = val['event_name']
            if self.clicked_button_name != '':
                self.clicked_button_index = self.button_names_list.index(self.clicked_button_name)
                self.buttons_list[self.clicked_button_index].setChecked(True)
                self.show_config_widgets()

                labels = self.labels[self.clicked_button_index]
                for x in range(len(labels)):
                    # Set value only if value is present in val dict
                    if labels[x] in val:
                        self.string_box_list[x].setTitle(labels[x])
                        self.string_box_list[x].set_val(val[labels[x]])

    def button_clicked(self):
        """Identifies the button that was clicked and stores the name and ID of the button."""
        for button in self.buttons_list:
            if button.isChecked():
                self.clicked_button_index = self.buttons_list.index(button)
                self.clicked_button_name = self.button_names_list[self.clicked_button_index]
        self.show_config_widgets()

    def show_config_widgets(self):
        """Show appropriate number of StringBoxes and relevant Widgets based on the button that was clicked."""
        self.hide_config_widgets()

        if self.clicked_button_index != 0:
            [self.string_box_list[x].set_visible(True) for x in range(len(self.labels[self.clicked_button_index]))]
            [self.string_box_list[x].setTitle(self.labels[self.clicked_button_index][x]) for x in
             range(len(self.labels[self.clicked_button_index]))]

    def hide_config_widgets(self):
        """Hide all Widgets."""
        [x.set_visible(False) for x in self.string_box_list]
        [x.set_val("") for x in self.string_box_list]


class ExternalNode(gpi.NodeAPI):
    """This Node provides allows the user to make a AtomicSequence for Jemris."""

    def initUI(self):
        # Init constant(s)
        self.num_concurrent_events = 6

        # Widgets
        [self.addWidget('ConfigSeqWidgets', 'Event ' + str(x + 1)) for x in range(self.num_concurrent_events)]
        self.addWidget('PushButton', 'ComputeEvents', button_title="Compute events")

        # IO Ports
        self.addOutPort('AtomicSequence Children', 'LIST')

        return 0

    def compute(self):
        if 'ComputeEvents' in self.widgetEvents() or '_INIT_EVENT_' in self.getEvents():
            # Retrieve pulse definitions and add to atomic_seq_children
            atomic_seq_children = []
            for x in range(self.num_concurrent_events):
                pulse_def = self.getVal('Event ' + str(x + 1))
                if pulse_def is not None:
                    atomic_seq_children.append(pulse_def)

            self.setData('AtomicSequence Children', atomic_seq_children)

        return 0
