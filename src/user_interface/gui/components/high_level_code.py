import customtkinter as ctk
import tempfile
import os
from PIL import Image
from src.user_interface.gui.func import high_level_code as func
from src.compiler.preprocessor import Preprocessor
from src.compiler.lexer import MyLexer
from src.compiler.parser import Parser
from .design_variable_elements import Fonts
from .compiler_phases_window import CompilerPhasesWindow

class HighLevelCodeFrame(ctk.CTkFrame):
    def __init__(self, parent, fg_color = '#0C1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=8)
        self.rowconfigure(2, weight=1)
        self.compile_icon = kwargs.get('compile_icon', '')
        self.upload_icon = kwargs.get('upload_icon', '')
        self.clean_icon = kwargs.get('clean_icon', '')
        self.assembly_callback = None
        self.compiler_window = None
        self.current_file_path = None

        self.__build_text()
        self.__build_entry_text()
        self.__build_buttons()

    def set_assembly_callback(self, callback):
        self.assembly_callback = callback

    def load_file_wrapper(self):
        path = func.select_file()
        if path:
            self.current_file_path = path
            content = func.open_file(path)
            self.text_entry.delete("1.0", "end")
            self.text_entry.insert("1.0", content)

    def open_compiler_phases(self):
        code = self.text_entry.get("0.0", "end")
        if not code.strip():
            return
        
        try:
            # 1. Preprocesar
            with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmp:
                tmp.write(code)
                tmp_path = tmp.name
            
            preprocessor = Preprocessor()
            
            # Agregar directorio del archivo original a los includes si existe
            if self.current_file_path:
                file_dir = os.path.dirname(self.current_file_path)
                if file_dir not in preprocessor.include_paths:
                    preprocessor.include_paths.append(file_dir)

            preprocessed_code = preprocessor.preprocess_file(tmp_path)
            os.unlink(tmp_path)
            
            # Obtener ASM de librerías incluidas (smart includes)
            library_asm = preprocessor.get_smart_includes_asm(preprocessed_code)
            available_funcs = preprocessor.get_available_library_functions()

            # 2. Lexer (Generar lista de tokens para UI y para Parser)
            lexer = MyLexer()
            lexer.build()
            lexer.reset_counters()
            lexer.lexer.input(preprocessed_code)
            
            tokens_list = []
            while True:
                tok = lexer.lexer.token()
                if not tok:
                    break
                tokens_list.append(tok)
            
            lexer_stats = {
                'num_count': lexer.num_count,
                'string_count': lexer.string_count,
                'id_count': lexer.id_count,
                'kw_count': lexer.kw_count
            }

            # 3. Parser (ASM Generator + AST)
            # Necesitamos un iterador de tokens para el parser, ya que consumimos el lexer original
            class ListLexer:
                def __init__(self, tokens):
                    self.tokens = iter(tokens)
                    self.lineno = 1 # Dummy
                    self.lexpos = 0 # Dummy
                def token(self):
                    try:
                        return next(self.tokens)
                    except StopIteration:
                        return None
                def input(self, data): pass

            token_iterator = ListLexer(tokens_list)
            parser = Parser(MyLexer.tokens, library_functions=available_funcs)
            
            # Pasamos el iterador personalizado y el código de librerías
            result = parser.parse(preprocessed_code, lexer=token_iterator, library_asm=library_asm)
            
            asm_code = ""
            ast_tree = None
            
            if result:
                asm_code, ast_tree = result
                
                if self.assembly_callback:
                    self.assembly_callback(asm_code)
            else:
                if self.assembly_callback:
                    self.assembly_callback("; Error en compilación")

            # 4. Abrir ventana de fases con datos pre-calculados
            if self.compiler_window is None or not self.compiler_window.winfo_exists():
                self.compiler_window = CompilerPhasesWindow(self, preprocessed_code, tokens_list, lexer_stats, ast_tree, library_asm)
            else:
                self.compiler_window.update_data(preprocessed_code, tokens_list, lexer_stats, ast_tree, library_asm)

        except Exception as e:
            if self.assembly_callback:
                self.assembly_callback(f"; Error: {str(e)}")
            # Aún así intentamos abrir la ventana para mostrar hasta donde llegó (opcional)
            # CompilerPhasesWindow(self, preprocessed_code if 'preprocessed_code' in locals() else "", [], {}, None)

    def __build_text(self):
        text = ctk.CTkLabel(
            self,
            text = 'Código en alto nivel',
            font=Fonts.get_font(""),
            text_color="white"
        )
        text.grid(row = 0, column = 0)

    def __build_entry_text(self):
        self.text_entry = ctk.CTkTextbox(
            self,
            fg_color = '#2b2b2b'
        )
        self.text_entry.grid(row = 1, column = 0, sticky = 'nsew', padx = 12)
        self.text_entry.configure(
            font = Fonts.get_font("")
        )

    def __build_buttons(self):
        button_frame = ctk.CTkFrame(
            self,
            fg_color = 'transparent'
        )

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        button_frame.rowconfigure(0, weight=1)

        compile_image = ctk.CTkImage(
            light_image = Image.open(self.compile_icon),
            dark_image = Image.open(self.compile_icon),
            size = (40, 40)
        )
        boton_compilar = ctk.CTkButton(
            button_frame, 
            text='Compilar',
            image = compile_image,
            compound='right',
            fg_color='#4C44AC',
            text_color='white',
            corner_radius=50,
            font=Fonts.get_font(""),
            command=self.open_compiler_phases
        )
        boton_compilar.grid(row = 0, column = 0)

        upload_image = ctk.CTkImage(
            light_image = Image.open(self.upload_icon),
            dark_image = Image.open(self.upload_icon),
            size = (40, 40)
        )
        boton_subir = ctk.CTkButton(
            button_frame, 
            text='Subir',
            image = upload_image,
            compound='right',
            fg_color='#4C44AC',
            text_color='white',
            corner_radius=50,
            font=Fonts.get_font(""),
            command = self.load_file_wrapper
        )
        boton_subir.grid(row = 0, column = 1)

        clean_image = ctk.CTkImage(
            light_image=Image.open(self.clean_icon),
            dark_image = Image.open(self.clean_icon),
            size = (40, 40)
        )
        boton_limpiar = ctk.CTkButton(
            button_frame,
            text = 'Limpiar',
            image = clean_image,
            compound= 'right',
            fg_color='#4C44AC',
            text_color='white',
            corner_radius=50,
            font=Fonts.get_font(""),
            command = lambda: func.clean_content(self.text_entry)
        )
        boton_limpiar.grid(row = 0, column = 2)

        button_frame.grid(column = 0, row = 2, sticky = 'nsew', padx = 30)