import customtkinter as ctk

class GeneralPurposeRegisterFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0C1826'):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
    
        self.__build_text()
        self.__build_table()

    def __build_text(self):
        text = ctk.CTkLabel(
            self,
            text = 'Registros de propósito general',
            font=("Comic Sans MS", 14),
            text_color="white"
        )
        text.grid(row = 0, column = 0)
    
    def __build_table(self):
        scrollable_frame = ctk.CTkScrollableFrame(
            self
        )
        scrollable_frame.grid(row = 1, column = 0, sticky = 'nsew', padx = (10,10), pady = 5)

        headers = ['reg', 'val']
        for j, header in enumerate(headers):
            lbl = ctk.CTkLabel(scrollable_frame, text=header, fg_color="#2b2b2b", corner_radius=4)
            lbl.grid(row=0, column=j, sticky="nsew", padx=5, pady=5)