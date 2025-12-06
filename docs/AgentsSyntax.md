# Sintaxis de Agentes Comunicantes - Euclid-64

## Tipo de Dato: Agent

Los agentes se definen como un tipo de dato abstracto (ADT):

```c
adt Agent
    public:
        int id;
        string name;
    private:
        Agent parent;
endadt
```

## Operaciones Básicas

### 1. Creación de Agentes

**Sintaxis:**
```c
Agent agente = create agent;                    // Sin parámetros
Agent agente = create agent("nombre_nodo");     // Solo nombre
Agent agente = create agent(padre);             // Solo padre
Agent agente = create agent(padre, "nombre");   // Padre y nombre
```

**Ejemplos:**
```c
Agent a1 = create agent;
Agent a2 = create agent("servidor");
Agent a3 = create agent(a1);
Agent a4 = create agent(a1, "cliente");
```

**Mapeo a Python:**
```python
# Agent agente = create agent(padre, "nombre");
agente = sistema.add_agent(parent=padre, agent_name="nombre")
```

---

### 2. Creación de Enlaces

**Sintaxis:**
```c
link origen to destino via "canal";
```

**Ejemplos:**
```c
link a1 to a2 via "red";
link servidor to cliente via "http";
```

**Mapeo a Python:**
```python
# link origen to destino via "canal";
sistema.add_link(origen, destino, "canal")
```

---

### 3. Envío de Mensajes

**Sintaxis (estructura tipo JSON):**
```c
send {
    type: MSG_INFO,
    payload: {
        channel: "canal",
        origin: agente_origen,
        destiny: agente_destino
    }
};
```

**Tipos de mensaje válidos:**
- `MSG_INFO` - Solicitar información del agente
- `MSG_CHG_PARENT` - Cambiar padre del agente
- `MSG_DEL_LINK` - Eliminar enlace entre agentes
- `MSG_CRE_LINK` - Crear nuevo enlace

**Ejemplos:**
```c
// Solicitar información
send {
    type: MSG_INFO,
    payload: {
        channel: "red",
        origin: a1,
        destiny: a2
    }
};

// Eliminar enlace
send {
    type: MSG_DEL_LINK,
    payload: {
        channel: "http",
        origin: servidor,
        destiny: cliente
    }
};

// Crear enlace
send {
    type: MSG_CRE_LINK,
    payload: {
        channel: "nuevo_canal",
        origin: a1,
        destiny: a3
    }
};
```

**Mapeo a Python:**
```python
# send { type: MSG_INFO, payload: {...} };
mensaje = {
    "type": "INFO",
    "payload": {
        "channel": "red",
        "origin": a1,
        "destiny": a2
    }
}
sistema.send_message(mensaje)
```

---

### 4. Eliminación de Enlaces

**Sintaxis:**
```c
unlink origen from destino on "canal";
```

**Ejemplos:**
```c
unlink a1 from a2 on "red";
unlink servidor from cliente on "http";
```

**Mapeo a Python:**
```python
# unlink origen from destino on "canal";
sistema.break_link(origen, "canal", destino)
```

---

## Ejemplo Completo

```c
// Definir sistema de agentes comunicantes
agents
    // Crear agentes
    Agent servidor = create agent("main_server");
    Agent cliente1 = create agent(servidor, "client_1");
    Agent cliente2 = create agent(servidor, "client_2");
    
    // Crear enlaces
    link servidor to cliente1 via "conexion";
    link servidor to cliente2 via "conexion";
    link cliente1 to cliente2 via "peer";
    
    // Enviar mensajes
    send {
        type: MSG_INFO,
        payload: {
            channel: "conexion",
            origin: servidor,
            destiny: cliente1
        }
    };
    
    send {
        type: MSG_CRE_LINK,
        payload: {
            channel: "backup",
            origin: cliente1,
            destiny: cliente2
        }
    };
    
    // Eliminar enlace
    unlink servidor from cliente2 on "conexion";
    
    // Generar visualización
    run;
endagents
```

---

## Gramática Propuesta (Parser)

### Declaraciones de Agentes
```
agents_block : AGENTS statements ENDAGENTS

agent_creation : AGENT ID ASSIGN CREATE AGENT
               | AGENT ID ASSIGN CREATE AGENT LPAREN STRING RPAREN
               | AGENT ID ASSIGN CREATE AGENT LPAREN ID RPAREN
               | AGENT ID ASSIGN CREATE AGENT LPAREN ID COMMA STRING RPAREN

link_creation : LINK ID TO ID VIA STRING SEMI

unlink_stmt : UNLINK ID FROM ID ON STRING SEMI

send_message : SEND LBRACE message_struct RBRACE SEMI

message_struct : TYPE_KEY COLON msg_type COMMA
                 PAYLOAD_KEY COLON LBRACE payload_struct RBRACE

msg_type : MSG_INFO | MSG_CHG_PARENT | MSG_DEL_LINK | MSG_CRE_LINK

payload_struct : CHANNEL_KEY COLON STRING COMMA
                 ORIGIN_KEY COLON ID COMMA
                 DESTINY_KEY COLON ID

run_visualization : RUN SEMI
```

---

## Tokens del Lexer

### Palabras Reservadas
```python
'create', 'agent', 'link', 'unlink', 'send',
'to', 'from', 'on', 'via',
'agents', 'endagents', 'run',

# Claves de mensaje
'type', 'payload', 'channel', 'origin', 'destiny',

# Tipos de mensaje
'INFO', 'CHG_PARENT', 'DEL_LINK', 'CRE_LINK'
```

### Delimitadores
```python
'{', '}',  # Para estructuras JSON-like
'->',      # Arrow (opcional para enlaces alternativos)
```

---

## Mapeo Completo Python ↔ Lenguaje Alto Nivel

| Operación Python | Sintaxis Alto Nivel |
|------------------|---------------------|
| `sistema = CommunicatingAgents('G')` | `agents ... endagents` |
| `a = sistema.add_agent()` | `Agent a = create agent;` |
| `a = sistema.add_agent(agent_name="n")` | `Agent a = create agent("n");` |
| `a = sistema.add_agent(parent=p)` | `Agent a = create agent(p);` |
| `a = sistema.add_agent(parent=p, agent_name="n")` | `Agent a = create agent(p, "n");` |
| `sistema.add_link(a, b, "c")` | `link a to b via "c";` |
| `sistema.break_link(a, "c", b)` | `unlink a from b on "c";` |
| `sistema.send_message({...})` | `send {...};` |
| `sistema.generate_graphs()` | `run;` |

---

## Validaciones del Compilador

El parser debe validar:

1. **Tipo Agent declarado**: Solo variables de tipo `Agent` pueden usarse en operaciones de agentes
2. **Mensajes válidos**: Estructura JSON-like correcta con todas las claves obligatorias
3. **Tipos de mensaje**: Solo `MSG_INFO`, `MSG_CHG_PARENT`, `MSG_DEL_LINK`, `MSG_CRE_LINK`
4. **Canales como strings**: Los nombres de canal deben ser literales string
5. **Referencias válidas**: `origin` y `destiny` deben ser variables `Agent` existentes

---

## Generación de Código Assembly

Para cada operación de agentes, el compilador debe:

1. **Importar módulo Python**: 
   ```asm
   ; Llamada a función Python externa
   CALL __py_import_agents
   ```

2. **Crear agente**:
   ```asm
   ; Agent a = create agent("nombre");
   MOVI R0, #ptr_to_name_string
   CALL __py_add_agent
   ST [var_a], R0, #0  ; Guardar puntero al agente
   ```

3. **Crear enlace**:
   ```asm
   ; link a to b via "canal";
   LD R0, [var_a], #0
   LD R1, [var_b], #0
   MOVI R2, #ptr_to_canal_string
   CALL __py_add_link
   ```

4. **Enviar mensaje**:
   ```asm
   ; send {...};
   MOVI R0, #ptr_to_message_struct
   CALL __py_send_message
   ```

---

## Notas de Implementación

1. **Integración con Python**: Requiere bridge entre código assembly y módulo Python `CommunicatingAgent`
2. **Estructuras JSON**: El parser debe convertir sintaxis JSON-like a diccionarios Python
3. **Gestión de memoria**: Los objetos `Agent` residen en heap de Python, no en memoria de la máquina virtual
4. **Visualización**: El comando `run` genera archivos HTML con vis-network

