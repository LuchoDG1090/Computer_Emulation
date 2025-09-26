

# Computador: Euclid-64 
## **Empresa: Peñatech Labs**

##  Emulador de CPU

Este proyecto implementa un emulador de CPU que sigue la arquitectura Von Neumann con especificaciones puntuales para el curso de Lenguajes de Programación.

## Características de la Arquitectura

- **Modelo**: Von Neumann
- **Tamaño de instrucciones**: 64 bits
- **Endianness**: Little-endian
- **Registros principales**:
  - Program Counter (PC)
  - Instruction Register (IR)
  - Memory Address Register (MAR)
  - Memory Data Register (MDR)
  - Acumulador
  - Flag Register (8 bits: zero, carry, negative, positive, overflow, interrupt)
  - 16 registros de propósito general (R0-R15)

## Conjunto de Instrucciones

### Instrucciones ALU
- `ADD` - Suma
- `SUB` - Resta  
- `MUL` - Multiplicación
- `DIV` - División
- `AND` - AND lógico
- `OR` - OR lógico
- `XOR` - XOR lógico
- `NOT` - NOT lógico
- `SHL` - Desplazamiento izquierda
- `SHR` - Desplazamiento derecha
- `CMP` - Comparación

### Instrucciones de Transferencia de Datos
- `MOV` - Mover datos
- `LOAD` - Cargar desde memoria
- `STORE` - Almacenar en memoria
- `PUSH` - Empujar a pila
- `POP` - Sacar de pila

### Instrucciones de Control de Flujo
- `JMP` - Salto incondicional
- `JZ` - Salto si cero
- `JNZ` - Salto si no cero
- `JC` - Salto si carry
- `JNC` - Salto si no carry
- `CALL` - Llamada a subrutina
- `RET` - Retorno de subrutina

### Instrucciones de Sistema
- `HALT` - Detener CPU
- `NOP` - No operación

## Modos de Direccionamiento

- **Inmediato**: El operando es un valor constante
- **Registro**: El operando es un registro
- **Directo**: El operando es una dirección de memoria
- **Indirecto**: El operando es una dirección que contiene la dirección real
- **Indexado**: Dirección base + registro índice

## Formato de Instrucción (64 bits)

```
[63-56] Opcode (8 bits)
[55-52] RD - Registro destino (4 bits) 
[51-48] RS1 - Registro fuente 1 (4 bits)
[47-44] RS2 - Registro fuente 2 (4 bits)
[43-32] FUNC - Campo de funcion o modificador (12 bits)
[31-0]  IMM32 - Campo inmediato/direccion (32 bits)
```

## Tipos de Instrucción

Las instrucciones se clasifican en 4 tipos principales:

### R-Type (Registro-Registro)
- **Uso**: Operaciones ALU entre registros
- **Campos**: Opcode, RD, RS1, RS2, FUNC
- **Ejemplos**: ADD R2, R0, R1; SUB R3, R1, R2
- **FUNC**: Sub-opcodes para variantes de operación

### I-Type (Inmediato/Direccion) 
- **Uso**: Operaciones con inmediatos, LOAD/STORE
- **Campos**: Opcode, RD, RS1, FUNC, IMM32
- **Ejemplos**: MOV R0, #42; LOAD R1, #200
- **FUNC**: Modo de direccionamiento (0=inmediato, 1=registro)

### J-Type (Salto/Llamada)
- **Uso**: Saltos y llamadas a funciones
- **Campos**: Opcode, FUNC, IMM32
- **Ejemplos**: JMP #1000; CALL #500
- **IMM32**: Dirección de salto absoluta

### S-Type (Sistema/Efecto)
- **Uso**: Instrucciones de sistema
- **Campos**: Opcode, FUNC
- **Ejemplos**: HALT, NOP
- **FUNC**: Modificadores especiales

## Codificación de Registros

Los 16 registros R0-R15 se codifican en 4 bits usando representación binaria:
- R0 = 0000, R1 = 0001, R2 = 0010, ..., R15 = 1111




