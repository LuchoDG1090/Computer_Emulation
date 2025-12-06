

# Computador: Euclid-64 

Sistema completo de emulación computacional con arquitectura Von Neumann de 64 bits, incluyendo CPU, memoria, ensamblador, compilador de alto nivel y almacenamiento secundario.

---

## 📋 Componentes del Sistema

### 🖥️ CPU (Central Processing Unit)
- **Arquitectura**: Von Neumann de 64 bits
- **Endianness**: Little-endian
- **Punto flotante**: IEEE 754 double precision
- **Registros**:
  - 16 registros de propósito general (R0-R15)
  - Program Counter (PC)
  - Instruction Register (IR)
  - Memory Address/Data Registers (MAR/MDR)
  - Stack Pointer (R14)
  - Base Pointer (R15)
  - Flag Register (8 bits: zero, carry, negative, positive, overflow, interrupt)

### 💾 Memoria
- **Modelo**: Espacio unificado (código + datos)
- **Gestión**: Heap lineal con HEAP_PTR (sin liberación)
- **Pila**: Crece hacia abajo desde región alta
- **Linker**: Soporte para programas relocatables
- **Loader**: Carga binarios con mapas de memoria

### 🔧 Ensamblador
- **Sintaxis**: Euclid-64 Assembly
- **Características**:
  - Etiquetas simbólicas
  - Directivas de sección (.data, .text)
  - Generación de binarios y mapas de memoria
  - Soporte para relocatables y absolutos

### 🎯 Compilador de Alto Nivel
- **Parser**: LALR(1) usando PLY (Python Lex-Yacc)
- **Características**:
  - Tipos de datos: int, float, bool, char, string
  - Arreglos estáticos y dinámicos (primitivos y TDAs)
  - Tipos Abstractos de Datos (ADT) con visibilidad public/private
  - Funciones con parámetros y valores de retorno
  - Estructuras de control: if/else, while, for
  - Operadores: aritméticos, lógicos, relacionales, bitwise
  - Preprocesador: #include, #define
  - Smart includes: Extracción automática de funciones usadas

### 💿 Disco Virtual (SimpleDisk)
- **Formato**: disk.img (4KB header JSON + datos secuenciales)
- **Funciones**:
  - Almacenamiento de programas precompilados
  - Gestión via CLI (disk_manager.py)
  - Integración automática con preprocesador
  - Comandos: format, write, read, delete, list, info, compact

### 🔌 Entrada/Salida
- **Puertos MMIO**: Entrada/salida mapeada en memoria
- **Operaciones**:
  - Caracteres individuales (IN/OUT)
  - Enteros (IN/OUT)
  - Bloques de datos (INS/OUTS)

---

## 🛠️ Conjunto de Instrucciones (ISA)

### Formato de Instrucción (64 bits)
```
[63-56] Opcode (8 bits)
[55-52] RD - Registro destino (4 bits) 
[51-48] RS1 - Registro fuente 1 (4 bits)
[47-44] RS2 - Registro fuente 2 (4 bits)
[43-32] FUNC - Campo función (12 bits)
[31-0]  IMM32 - Inmediato/Dirección (32 bits)
```

### Operaciones Aritméticas y Lógicas
**Enteros:**
- `ADD RD, RS1, RS2` - Suma
- `SUB RD, RS1, RS2` - Resta
- `MUL RD, RS1, RS2` - Multiplicación
- `DIV RD, RS1, RS2` - División
- `ADDI RD, RS1, #IMM` - Suma con inmediato

**Punto Flotante (IEEE 754):**
- `FADD RD, RS1, RS2` - Suma flotante
- `FSUB RD, RS1, RS2` - Resta flotante
- `FMUL RD, RS1, RS2` - Multiplicación flotante
- `FDIV RD, RS1, RS2` - División flotante

**Operaciones Lógicas:**
- `AND RD, RS1, RS2` - AND lógico
- `OR RD, RS1, RS2` - OR lógico
- `XOR RD, RS1, RS2` - XOR lógico
- `NOT RD, RS1` - NOT lógico

**Desplazamientos:**
- `SHL RD, RS1, RS2` - Desplazamiento izquierda
- `SHR RD, RS1, RS2` - Desplazamiento derecha

### Transferencia de Datos
- `MOVI RD, #IMM` - Mover inmediato a registro
- `CP RD, RS1` - Copiar registro
- `LD RD, RS1, #OFFSET` - Cargar desde memoria
- `ST RS1, RD, #OFFSET` - Almacenar en memoria
- `PUSH RS` - Empujar a pila
- `POP RD` - Sacar de pila

### Control de Flujo
**Saltos Incondicionales:**
- `JMP #ADDR` - Salto incondicional
- `CALL #ADDR` - Llamada a función
- `RET` - Retorno de función

**Saltos Condicionales:**
- `JZ #ADDR` - Saltar si cero (zero flag)
- `JNZ #ADDR` - Saltar si no cero
- `JC #ADDR` - Saltar si carry
- `JNC #ADDR` - Saltar si no carry
- `JS #ADDR` - Saltar si negativo (signed)

**Comparación:**
- `CMP RS1, RS2` - Comparar y actualizar flags

### Entrada/Salida
- `IN RD, #PORT` - Leer desde puerto
- `OUT #PORT, RS` - Escribir a puerto
- `INS RD, #PORT, #COUNT` - Lectura en bloque
- `OUTS #PORT, RS, #COUNT` - Escritura en bloque

### Sistema
- `HALT` - Detener CPU
- `NOP` - No operación

---

## 📝 Lenguaje de Alto Nivel

### Tipos de Datos
```c
int x = 10;
float pi = 3.14159;
bool flag = true;
char letra = 'A';
string mensaje = "Hola Mundo";
```

### Arreglos
```c
// Arreglos estáticos
int numeros[10];
float matrix[3][3];

// Arreglos dinámicos
int n = 5;
int dinamico[n];
```

### Estructuras de Control

**Condicionales:**
```c
if (x > 10)
    y = 1;
else
    y = 0;
endif
```

**Bucles:**
```c
// While
while (i < 10)
    i = i + 1;
endwhile

// For con rango
for (i in 0..9)
    output(i);
endfor
```

**Control de Bucles:**
```c
break;      // Salir del bucle
continue;   // Siguiente iteración
```

### Funciones
```c
func suma(int a, int b) -> int
    return a + b;
endfunc

func saludar(string nombre) -> void
    output("Hola, ");
    output(nombre);
endfunc
```

### Tipos Abstractos de Datos (ADT)
```c
adt Punto
    public:
        int x;
        int y;
    
    private:
        int id;
endadt

// Uso
Punto p;
p.x = 10;
p.y = 20;

// Arreglos de TDAs
Punto puntos[5];
puntos[0].x = 100;
```

### Operadores

**Aritméticos:**
- `+` `-` `*` `/` `%`
- `++` `--` (incremento/decremento)

**Relacionales:**
- `==` `!=` `<` `<=` `>` `>=`

**Lógicos:**
- `&&` `||` `!`

**Bitwise:**
- `&` `|` `^` `~` `<<` `>>`

### Entrada/Salida
```c
input(variable);           // Leer valor
output(expresion);         // Escribir valor
```

### Preprocesador
```c
#include <math>            // Incluir desde disco virtual
#include "archivo.txt"     // Incluir archivo local
#define PI 3.14159        // Definir constante
```

---

## 🗂️ Gestión de Disco Virtual

### Comandos de disk_manager.py

```bash
# Crear/formatear disco
python tools\disk_manager.py format

# Escribir programa al disco
python tools\disk_manager.py write math includes\math.asm

# Leer programa del disco
python tools\disk_manager.py read math

# Listar todos los programas
python tools\disk_manager.py list

# Información del disco
python tools\disk_manager.py info

# Eliminar programa
python tools\disk_manager.py delete math

# Compactar disco (defragmentar)
python tools\disk_manager.py compact
```

---

## 🚀 Uso del Sistema

### Compilación de Programas
```bash
# Compilar archivo de alto nivel
python tests\compile_pipeline.py programa.txt --output build

# Guardar en disco virtual
python tools\disk_manager.py write programa build\programa.asm
```

### Ejecución
```bash
# Ejecutar programa compilado
python main.py
```

---

## 📊 Tipos de Instrucción

### R-Type (Registro-Registro)
- **Uso**: Operaciones ALU entre registros
- **Campos**: Opcode, RD, RS1, RS2, FUNC
- **Ejemplos**: `ADD R2, R0, R1`, `MUL R3, R1, R2`

### I-Type (Inmediato/Memoria)
- **Uso**: Operaciones con inmediatos, acceso a memoria
- **Campos**: Opcode, RD, RS1, FUNC, IMM32
- **Ejemplos**: `MOVI R0, #42`, `LD R1, R2, #100`

### J-Type (Saltos)
- **Uso**: Saltos y llamadas a funciones
- **Campos**: Opcode, FUNC, IMM32
- **Ejemplos**: `JMP #1000`, `CALL #500`

### S-Type (Sistema)
- **Uso**: Instrucciones de sistema
- **Campos**: Opcode, FUNC
- **Ejemplos**: `HALT`, `NOP`

---

## 🎓 Características Avanzadas

### Smart Includes
El preprocesador analiza automáticamente las librerías incluidas y extrae **solo las funciones utilizadas**, reduciendo el tamaño del código generado.

### Gestión de Memoria
- **Heap**: Asignación lineal con `HEAP_PTR`
- **Stack**: Gestión automática para llamadas a función
- **Arrays dinámicos**: Asignación en tiempo de ejecución

### Optimizaciones
- Extracción inteligente de funciones de librería
- Generación eficiente de código assembly
- Gestión automática de offsets en TDAs

---

## 📁 Estructura del Proyecto
```
Computer_Emulation/
├── src/
│   ├── cpu/          # Emulador de CPU
│   ├── memory/       # Gestión de memoria, linker, loader
│   ├── assembler/    # Ensamblador Euclid-64
│   ├── compiler/     # Compilador de alto nivel
│   ├── disk/         # Sistema de disco virtual
│   └── user_interface/ # GUI y CLI
├── tools/
│   └── disk_manager.py  # Gestor de disco virtual
├── tests/            # Programas de prueba
├── programs/         # Programas de ejemplo
└── disk.img          # Disco virtual




