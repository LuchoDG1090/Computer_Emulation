import messages
from color import Color
from help_module import Help

if __name__ == '__main__':
    messages.Messages().print_general_info()
    messages.Messages().print_instruction_info()
    while True:
        try:
            command = input('>> ')
        except EOFError:
            messages.Messages().print_exit_msg()
        except KeyboardInterrupt:
            messages.Messages().print_exit_msg()
        else:
            if command == 'exit()':
                print(Color.ROJO)
                print("Adios.")
                print(Color.RESET_COLOR)
                break
            elif command == 'clear()':
                print(Color.RESET_ALL)
            elif command == 'helpv()':
                Help().get_cli_help()
                Help().get_machine_help_verbose()
            elif command == 'help()':
                Help().get_cli_help()
                Help().get_machine_help()
            elif command == 'helpcli()':
                Help().get_cli_help()
            elif command == 'helpins()':
                Help().get_machine_help()
            elif command == 'helpinsv()':
                Help().get_machine_help_verbose()
            else:
                pass
            