import customtkinter as ctk
from .design_variable_elements import Fonts

class CompilerPhasesWindow(ctk.CTkToplevel):
    def __init__(self, parent, preprocessed_code, tokens_list, lexer_stats, ast_tree, fg_color = '#0C1826', **kwargs):
        super().__init__(parent, fg_color = fg_color)
        self.title("Fases del Compilador")
        self.geometry("1000x600")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = (screen_width - 1000) // 2
        y = (screen_height - 600) // 2

        self.geometry(f"1000x600+{x}+{y}")
        self.iconify()
        
        self.preprocessed_code = preprocessed_code
        self.tokens_list = tokens_list
        self.lexer_stats = lexer_stats
        self.ast_tree = ast_tree
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.tab_preprocessor = self.tab_view.add("Preprocesador")
        self.tab_lexer = self.tab_view.add("Lexer")
        self.tab_parser = self.tab_view.add("Parser")
        
        self.setup_preprocessor_tab()
        self.setup_lexer_tab()
        self.setup_parser_tab()
        
        self.populate_views()

    def update_data(self, preprocessed_code, tokens_list, lexer_stats, ast_tree):
        self.preprocessed_code = preprocessed_code
        self.tokens_list = tokens_list
        self.lexer_stats = lexer_stats
        self.ast_tree = ast_tree
        
        # Limpiar vistas anteriores
        self.preprocessor_text.delete("0.0", "end")
        self.lexer_text.delete("0.0", "end")
        self.parser_text.delete("0.0", "end")
        
        self.populate_views()
        
        # Traer al frente si está minimizada o detrás
        self.deiconify()
        self.lift()

    def setup_preprocessor_tab(self):
        self.tab_preprocessor.grid_columnconfigure(0, weight=1)
        self.tab_preprocessor.grid_rowconfigure(0, weight=1)
        
        self.preprocessor_text = ctk.CTkTextbox(self.tab_preprocessor, font=Fonts.get_font(""))
        self.preprocessor_text.grid(row=0, column=0, sticky="nsew")
        
    def setup_lexer_tab(self):
        self.tab_lexer.grid_columnconfigure(0, weight=1)
        self.tab_lexer.grid_rowconfigure(0, weight=1)
        
        # Usar fuente monoespaciada para que la tabla se alinee correctamente
        self.lexer_text = ctk.CTkTextbox(self.tab_lexer, font=("Consolas", 12))
        self.lexer_text.grid(row=0, column=0, sticky="nsew")
        
    def setup_parser_tab(self):
        self.tab_parser.grid_columnconfigure(0, weight=1)
        self.tab_parser.grid_rowconfigure(0, weight=1)
        
        self.parser_text = ctk.CTkTextbox(self.tab_parser, font=("Consolas", 12))
        self.parser_text.grid(row=0, column=0, sticky="nsew")

    def render_tree(self, node, prefix="", is_last=True, is_root=True):
        """
        Renderiza un nodo del AST en formato de árbol tipo 'tree' de Linux.
        """
        tree_str = ""
        
        if is_root:
            current_line = f"{self.get_node_label(node)}\n"
            # Para los hijos del nodo raíz, el prefijo base es vacío
            new_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            current_line = f"{prefix}{connector}{self.get_node_label(node)}\n"
            # Para los hijos de este nodo, agregamos indentación
            new_prefix = prefix + ("    " if is_last else "│   ")
            
        tree_str += current_line
        
        # Obtener hijos
        children = self.get_children(node)
        count = len(children)
        
        for i, child in enumerate(children):
            is_last_child = (i == count - 1)
            tree_str += self.render_tree(child, new_prefix, is_last_child, is_root=False)
            
        return tree_str

    def get_node_label(self, node):
        if isinstance(node, dict):
            node_type = node.get("type", "Unknown")
            # Personalizar etiquetas según el tipo
            if node_type == "Program":
                return "Program"
            elif node_type == "Declaration":
                return f"Declaration ({node.get('var_type')} {node.get('name')})"
            elif node_type == "BinaryOp":
                return f"BinaryOp ({node.get('op')})"
            elif node_type == "Literal":
                return f"Literal ({node.get('value')})"
            elif node_type == "Identifier":
                return f"Identifier ({node.get('name')})"
            elif node_type == "Assignment":
                return "Assignment"
            elif node_type == "If":
                return "If Statement"
            elif node_type == "While":
                return "While Loop"
            elif node_type == "FunctionDecl":
                header = node.get("header", {})
                return f"FunctionDecl ({header.get('name')})"
            elif node_type == "FuncCall":
                return f"FuncCall ({node.get('name')})"
            return node_type
        elif isinstance(node, list):
            return "Block"
        else:
            return str(node)

    def get_children(self, node):
        children = []
        if isinstance(node, dict):
            # Definir qué campos son hijos según el tipo
            node_type = node.get("type")
            if node_type == "Program":
                children = node.get("body", [])
                if not isinstance(children, list):
                    children = [children]
            elif node_type == "Declaration":
                if "init" in node:
                    children.append(node["init"])
            elif node_type == "BinaryOp":
                children = [node.get("left"), node.get("right")]
            elif node_type == "Assignment":
                children = [node.get("target"), node.get("value")]
            elif node_type == "If":
                children.append(node.get("condition"))
                children.append(node.get("then"))
                if "else" in node:
                    children.append(node.get("else"))
            elif node_type == "While":
                children = [node.get("condition"), node.get("body")]
            elif node_type == "FunctionDecl":
                children = [node.get("body")] # Params están en header, body es lo principal
            elif node_type == "FuncCall":
                children = node.get("args", [])
            elif node_type == "ExpressionStmt":
                children = [node.get("expression")]
            # Agregar más casos según sea necesario
        elif isinstance(node, list):
            children = node
            
        # Filtrar Nones
        return [c for c in children if c is not None]

    def populate_views(self):
        # 1. Preprocessor
        self.preprocessor_text.insert("0.0", self.preprocessed_code)

        # 2. Lexer
        lexer_output = f"{'Tipo':<20} | {'Valor':<30} | {'Linea':<5} | {'Pos':<5}\n"
        lexer_output += "-" * 70 + "\n"
        
        for tok in self.tokens_list:
            lexer_output += f"{tok.type:<20} | {str(tok.value):<30} | {tok.lineno:<5} | {tok.lexpos:<5}\n"
        
        lexer_output += "\n" + "="*50 + "\n"
        lexer_output += f"Numeros: {self.lexer_stats.get('num_count', 0)}\n"
        lexer_output += f"Strings: {self.lexer_stats.get('string_count', 0)}\n"
        lexer_output += f"IDs: {self.lexer_stats.get('id_count', 0)}\n"
        lexer_output += f"Keywords: {self.lexer_stats.get('kw_count', 0)}\n"
        
        self.lexer_text.insert("0.0", lexer_output)

        # 3. Parser (AST Visualization)
        if self.ast_tree:
            # Renderizar como árbol de texto
            tree_view = self.render_tree(self.ast_tree)
            self.parser_text.insert("0.0", tree_view)
        else:
            self.parser_text.insert("0.0", "Error al generar el AST (ver consola o logs para detalles).")
