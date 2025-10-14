from src.user_interface.gui.components import reloc

def set_content(content: str):
    text_box = reloc.RelocCodeFrame.get_entry_text()
    text_box.textbox.insert("1.0", content)