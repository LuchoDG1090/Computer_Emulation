

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




