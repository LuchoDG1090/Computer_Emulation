ALLOWED_MESSAGES = ("INFO",
                    "CHG_PARENT",
                    "DEL_LINK", 
                    "CRE_LINK")

class ManageMessages():
    def __init__(self) -> None:
        pass

        

    def __get_message_type(self, message: dict) -> str:
        try:
            msg_type = message["type"]
        except KeyError:
            raise ValueError("Not type of message given")

        if msg_type not in ALLOWED_MESSAGES:
            raise ValueError("Incorrect value for type of message")
        return message["type"]
    
    def __get_message_payload(self, message:dict) -> dict:
        try:
            msg_payload = message["payload"]
        except KeyError:
            raise ValueError("Not payload of message given")
        
        try:
            channel = message["payload"]["channel"]
            origin = message["payload"]["origin"]
            destiny = message["payload"]["destiny"]
        except KeyError:
            raise ValueError("Not given enough parameters on the payload")
        
        return channel, origin, destiny


    def _send_message_validations(self, message, agents, links) -> dict:
        if not isinstance(message, dict):
            raise ValueError("Wrong message format")
        
        message_type = self.__get_message_type(message = message)
        channel, origin, destiny = self.__get_message_payload(message = message)

        if message_type == "CRE_LINK":
            if origin in agents and destiny in agents:
                return [True, origin, destiny, message_type, channel]

        try:
            channel_connections = links[channel]
        except KeyError:
            print("Error: channel not available")
            return False

        connection_exists = False

        if (origin.id, destiny.id) in channel_connections or (destiny.id, origin.id) in channel_connections:
            connection_exists = True
                
        if message_type == "CHG_PARENT":
            print("parent_validation")

        if connection_exists:
            return [True, origin, destiny, message_type, channel]
        return [False]

        

        
        
