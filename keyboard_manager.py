from tkinter import Frame, Toplevel


class KeyboardManager:
    """
    Class to manage all keyboard interactions.
    """
    # Save key format in variables
    __tab: str = '<Tab>'
    __shift: str = '<Shift>'
    __shift_tab: str = '<Shift-Tab>'
    __esc: str = '<Escape>'
    __enter: str = '<Return>'

    def __check_button(self, widget) -> bool:
        """
        Returns True if widget is a button, False otherwise.

        :param widget: Widget to check
        :return: True if button else False
        """
        return "button" in widget.__str__()

    def __check_checkbutton(self, widget) -> bool:
        """
        Returns True if widget is a checkbox or radiobutton, False otherwise.

        :param widget: Widget to check
        :return: True if checkbox or radiobutton else False
        """
        return "checkbutton" in widget.__str__()

    def enter_bind(self, frame: Frame | Toplevel, widget):
        """
        Binds the Enter key to invoking the widget of a certain frame.

        :param frame: Frame in which the widget is present
        :param widget: Widget to be invoked by the Enter key
        """
        frame.bind(self.__enter, lambda e: widget.invoke())

    def focus_enter_bind(self, frame: Frame | Toplevel):
        """
        Binds the Enter key to invoking the focused widget of a certain frame.

        :param frame: Frame in which the widgets are present and should be focused
        """
        frame.bind(self.__enter, lambda e: frame.focus_get().invoke() if self.__check_button(
            frame.focus_get()) or self.__check_checkbutton(frame.focus_get()) else None)

    def tab_bind(self, frame: Frame | Toplevel, list_widgets: list):
        """
        Binds the Tab key to apply tab_focus_change function on the list of widgets.

        :param frame: Frame in which the widgets are present
        :param list_widgets: List of widgets to alternate between using Tab
        """
        frame.bind(self.__tab, lambda e: self.tab_focus_change(frame, list_widgets))

    def shift_tab_bind(self, frame: Frame | Toplevel, list_widgets: list):
        """
        Binds the Shift and Tab keys to apply REVERSED tab_focus_change function
        on the list of widgets.

        :param frame: Frame in which the widgets are present
        :param list_widgets: List of widgets to reverse alternate between using Shift + Tab
        """
        frame.bind(self.__shift_tab, lambda e: self.tab_focus_change(frame, list_widgets, reverse=True))

    def esc_bind(self, frame: Frame | Toplevel, event=''):
        """
        Binds the ESC to closing the frame using the event function.
        If event is not given, the function destroys the frame usind detroy().
        Else, the function uses event to close the frame.

        :param frame: Frame that should be closed using ESC
        :param event: The function to use to close the frame
        """
        if event == '':
            frame.bind(self.__esc, lambda e: frame.destroy())
        else:
            frame.bind(self.__esc, event)

    def tab_focus_change(self, frame: Frame | Toplevel, list_widgets: list, reverse: bool = False):
        """
        Works with tab_bind() and shift_tab_bind(). This functions creates a focus
        around the selected widget while tapping (Shift + ) Tab key(s) and binds this
        widget with the Enter key using enter_bind(). If the user presses Shift + Tab,
        the function works with reverse mechanism to alternate through widgets in
        reverse mode. Focus is created using a gray highlight or default focus.

        :param frame: Frame in which widgets are in
        :param list_widgets: List of widgets to (reverse) alternate between using (Shift + ) Tab
        :param reverse: Boolean to define if normal or reverse mode
        """
        nb_widgets = len(list_widgets) - 1
        widget_tracker = list_widgets[nb_widgets]

        increment = -1 if reverse else 1

        if (widget_tracker >= nb_widgets - 1 and not reverse) or (widget_tracker == -1 and reverse):
            widget_tracker = nb_widgets - 1 if reverse else 0
        else:
            widget_tracker += increment

        widget = list_widgets[widget_tracker]
        list_widgets[nb_widgets] = widget_tracker
        self.reset_all_widgets(list_widgets)
        if self.__check_button(widget):
            widget.configure(highlightbackground="black")
            self.enter_bind(frame, widget)
        else:
            return

    def reset_all_widgets(self, list_widgets: list):
        """
        Works with tab_focus_change(). Removes highlight focus from widgets.

        :param list_widgets: List of widgets to remove focus from
        """
        for widget in list_widgets[:-1]:
            if self.__check_button(widget):
                widget.configure(highlightbackground="white")
