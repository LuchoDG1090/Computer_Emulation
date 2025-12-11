import customtkinter as ctk
from PIL import Image
import os

Image.MAX_IMAGE_PIXELS = None
class CommunicatingAgentsVisualization(ctk.CTkToplevel):
    def __init__(self, parent, image_dir=None, fg_color='#0C1826', **kwargs):
        super().__init__(parent, fg_color=fg_color)
        self.title("Visualización de agentes comunicantes")

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()


        self.geometry(f"{self.screen_width}x{self.screen_height}")
        self.iconify()

        # Rutas de las imágenes (dinámicas o por defecto)
        if image_dir is None:
            # Usar directorio por defecto relativo al proyecto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            image_dir = os.path.join(base_dir, "images")
        
        self.image_dir = image_dir
        self.bigrafo = os.path.join(self.image_dir, "graph.png")
        self.forest = os.path.join(self.image_dir, "forest.png")
        self.hipergrafo = os.path.join(self.image_dir, "hypergraph.png")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Frames contenedores
        self.bigraph_frame = None
        self.forest_frame = None
        self.hipergraph_frame = None

        self.refresh_images()
    
    def refresh_images(self):
        """Actualiza las imágenes mostradas"""
        # Limpiar frames anteriores
        if self.bigraph_frame:
            self.bigraph_frame.destroy()
        if self.forest_frame:
            self.forest_frame.destroy()
        if self.hipergraph_frame:
            self.hipergraph_frame.destroy()
        
        # Re-renderizar
        self.__render_bigraph()
        self.__render_forest()
        self.__render_hipergraph()
    
    def set_image_directory(self, image_dir):
        """Actualiza el directorio de imágenes y refresca"""
        self.image_dir = image_dir
        self.bigrafo = os.path.join(self.image_dir, "graph.png")
        self.forest = os.path.join(self.image_dir, "forest.png")
        self.hipergrafo = os.path.join(self.image_dir, "hypergraph.png")
        self.refresh_images()
    
    def __render_bigraph(self):
        self.bigraph_frame = ctk.CTkFrame(self)
        if os.path.exists(self.bigrafo):
            pil_image = Image.open(self.bigrafo)
            width, height = self.screen_width * 0.4, self.screen_height * 0.85
            img = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size = (width, height)
            )
            label = ctk.CTkLabel(self.bigraph_frame, text="", image=img)
            label.pack()
        else:
            label = ctk.CTkLabel(self.bigraph_frame, text="Gráfico no disponible", font=("Arial", 16))
            label.pack(expand=True)
        self.bigraph_frame.grid(column = 0, row = 0, rowspan = 2)

    def __render_forest(self):
        self.forest_frame = ctk.CTkFrame(self)
        if os.path.exists(self.forest):
            pil_image = Image.open(self.forest)
            width, height = self.screen_width * 0.4, self.screen_height * 0.45
            img = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size = (width, height)
            )
            label = ctk.CTkLabel(self.forest_frame, text="", image=img)
            label.pack()
        else:
            label = ctk.CTkLabel(self.forest_frame, text="Forest no disponible", font=("Arial", 16))
            label.pack(expand=True)
        self.forest_frame.grid(column = 1, row = 0)

    def __render_hipergraph(self):
        self.hipergraph_frame = ctk.CTkFrame(self)
        if os.path.exists(self.hipergrafo):
            pil_image = Image.open(self.hipergrafo)
            width, height = self.screen_width * 0.4 , self.screen_height * 0.45
            img = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size = (width, height)
            )
            label = ctk.CTkLabel(self.hipergraph_frame, text="", image=img)
            label.pack()
        else:
            label = ctk.CTkLabel(self.hipergraph_frame, text="Hipergráfico no disponible", font=("Arial", 16))
            label.pack(expand=True)
        self.hipergraph_frame.grid(column = 1, row = 1)

    





if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.withdraw()

    win = CommunicatingAgentsVisualization(root)
    win.deiconify()

    root.mainloop()
