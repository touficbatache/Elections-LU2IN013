class KeyboardManager:
    __tab: str = '<Tab>'
    __shift: str = '<Shift>'
    __shift_tab: str = '<Shift-Tab>'
    __esc: str = '<Escape>'
    __enter: str = '<Return>'

    def enter_bind(self, frame, widget):
        frame.bind(self.__enter, lambda e: widget.invoke())

    def tab_bind(self, frame, list_widgets):
        frame.bind(self.__tab, lambda e: self.tab_focus_change(frame, list_widgets))

    def shift_tab_bind(self, frame, list_widgets):
        frame.bind(self.__shift_tab, lambda e: self.tab_focus_change(frame, list_widgets, reverse=True))

    def esc_bind(self, frame, event=''):
        if event == '':
            frame.bind(self.__esc, lambda e: frame.destroy())
        else:
            frame.bind(self.__esc, event)

    def esc_bind_approbation(self, frame, graph_manager):
        frame.bind(self.__esc, lambda e: [graph_manager.clear_approbation_circles(), graph_manager.build(),
                                          frame.destroy()])

    def tab_focus_change(self, frame, list_widgets, reverse=False):
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
        for widget in list_widgets[:-1]:
            widget.configure(highlightbackground="black")
