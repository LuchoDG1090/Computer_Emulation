import customtkinter as ctk
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
class CommunicatingAgentsVisualization(ctk.CTkToplevel):
    def __init__(self, parent, fg_color='#0C1826', **kwargs):
        super().__init__(parent, fg_color=fg_color)
        self.title("Visualización de agentes comunicantes")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()


        self.geometry(f"{self.screen_width}x{self.screen_height}")
        self.iconify()

        # Rutas de las imágenes
        self.bigrafo = r"C:\Users\cmedi\OneDrive\Escritorio\computer emulation\src\communicating_agents\graph.png"
        self.forest = r"C:\Users\cmedi\OneDrive\Escritorio\computer emulation\src\communicating_agents\forest.png"
        self.hipergrafo = r"C:\Users\cmedi\OneDrive\Escritorio\computer emulation\src\communicating_agents\hypergraph.png"

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.__render_bigraph()
        self.__render_forest()
        self.__render_hipergraph()
    
    def __render_bigraph(self):
        bigraph_frame = ctk.CTkFrame(self)
        pil_image = Image.open(self.bigrafo)
        width, height = self.screen_width * 0.4, self.screen_height * 0.85
        img = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size = (width, height)
        )
        label = ctk.CTkLabel(bigraph_frame, text="", image=img)
        label.pack()
        bigraph_frame.grid(column = 0, row = 0, rowspan = 2)

    def __render_forest(self):
        forest_frame = ctk.CTkFrame(self)
        pil_image = Image.open(self.forest)
        width, height = self.screen_width * 0.4, self.screen_height * 0.45
        img = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size = (width, height)
        )
        label = ctk.CTkLabel(forest_frame, text="", image=img)
        label.pack()
        forest_frame.grid(column = 1, row = 0)

    def __render_hipergraph(self):
        hipergraph_frame = ctk.CTkFrame(self)
        pil_image = Image.open(self.hipergrafo)
        width, height = self.screen_width * 0.4 , self.screen_height * 0.45
        img = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size = (width, height)
        )
        label = ctk.CTkLabel(hipergraph_frame, text="", image=img)
        label.pack()
        hipergraph_frame.grid(column = 1, row = 1)

    





if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.withdraw()

    win = CommunicatingAgentsVisualization(root)
    win.deiconify()

    root.mainloop()
