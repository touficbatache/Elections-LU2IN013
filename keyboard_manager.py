class KeyboardManager:
    """
    Class to manage all keyboard interactions.
    """
    # Save key format in veriables
    __tab: str = '<Tab>'
    __shift: str = '<Shift>'
    __shift_tab: str = '<Shift-Tab>'
    __esc: str = '<Escape>'
    __enter: str = '<Return>'

    def enter_bind(self, frame, widget):
        """
        Binds the Enter key to invoking the widgets for a certain frame.

        :param frame: Frame in which the widget is present
        :param widget: Widget to be invoked by the Enter key
        """
        frame.bind(self.__enter, lambda e: widget.invoke())

    def tab_bind(self, frame, list_widgets):
        """
        Binds the Tab key to apply tab_focus_change function on the list of widgets.

        :param frame: Frame in which the widgets are present
        :param list_widgets: List of widgets to alternate between using Tab
        """
        frame.bind(self.__tab, lambda e: self.tab_focus_change(frame, list_widgets))

    def shift_tab_bind(self, frame, list_widgets):
        """
        Binds the Shift and Tab keys to apply REVERSED tab_focus_change function
        on the list of widgets.

        :param frame: Frame in which the widgets are present
        :param list_widgets: List of widgets to reverse alternate between using Shift + Tab
        """
        frame.bind(self.__shift_tab, lambda e: self.tab_focus_change(frame, list_widgets, reverse=True))

    def esc_bind(self, frame, event=''):
        """
        Binds the ESC to closing the frame using the event function.
        If event is not given, the function destroys the frame.
        Else, the function uses event to close the frame.

        :param frame: Frame that should be closed using ESC
        :param event: The function to use to close the frame
        """
        if event == '':
            frame.bind(self.__esc, lambda e: frame.destroy())
        else:
            frame.bind(self.__esc, event)

    def tab_focus_change(self, frame, list_widgets, reverse=False):
        """
        Works with tab_bind() and shift_tab_bind(). This functions creates a focus
        around the selected widget while tapping Tab key and binds this widget with
        the Enter key using enter_bind(). If the user presses Shift + Tab, the function
        works with reverse mechanism to alternate through widgets in reverse mode. Focus
        is created using a gray highlight or default focus.

        :param frame: Frame in which widgets are in
        :param list_widgets: List of widgets to (reverse) alternate between using (Shift + ) Tab
        :param reverse: Boolean to define if normal or reverse mode
        """
        nb_widgets = len(list_widgets) - 1
        if reverse:
            if list_widgets[nb_widgets] != -1:
                list_widgets[nb_widgets] -= 1
            if list_widgets[nb_widgets] == -1:
                list_widgets[nb_widgets] = nb_widgets - 1
        else:
            if list_widgets[nb_widgets] >= nb_widgets - 1:
                list_widgets[nb_widgets] = 0
            else:
                list_widgets[nb_widgets] += 1

        widget = list_widgets[list_widgets[nb_widgets]]
        self.set_all_buttons(list_widgets)
        widget.configure(highlightbackground="gray")
        self.enter_bind(frame, widget)

    def set_all_buttons(self, list_widgets):
        """
        Works with tab_focus_change(). Removes highlight focus from widgets.

        :param list_widgets: List of widgets to remove focus from
        """
        for widget in list_widgets[:-1]:
            widget.configure(highlightbackground="black")
