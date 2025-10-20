# Bubble sort demo
# Reads N and N space-separated numbers, sorts in ascending order using
# bubble sort, and prints before/after.

# --------------------
# Data
# --------------------
ORG 1028

LEN:    DW 5                  # default length
ARR:    DW 5, 3, 8, 1, 4      # default values (overwritten by input)


# --------------------
# Code
# --------------------
ORG 3700

START:
    # Constants / bases
    MOVI R1, ARR          # base address of array
    MOVI R7, 8            # word size bytes

    # Prompt: "Bubble Sort - Ordenamiento de numeros\n"
    MOVI R5, msg1
    OUTS R5, 0xFFFF0008
    
    # Prompt: "Ingrese la cantidad de numeros: "
    MOVI R5, msg2
    OUTS R5, 0xFFFF0008
    
    # Read N from console (single integer)
    IN   R2, 0xFFFF0018   # R2 = N
    # If N == 0, fallback to default LEN
    CMP  R0, R2, R0
    JNZ  have_len
    LD   R2, LEN          # absolute load: assembler encodes as I-Type imm
have_len:

    # Prompt: "Ingrese los numeros separados por espacio:\n"
    MOVI R5, msg3
    OUTS R5, 0xFFFF0008

    # Read up to 100 integers from one line (space-separated) into ARR
    # La instrucción IN leerá hasta N números (el usuario ingresará exactamente N)
    IN   R15, R1, 100     # Read up to 100 integers into array at R1
    # R15 ahora contiene cuántos números se leyeron realmente
    CP   R2, R15          # Actualizar R2 con la cantidad real leída
after_input_read:

    # Print before: "Array original: "
    MOVI R5, msg4
    OUTS R5, 0xFFFF0008
    
    # Print array with a loop (OUT array mode requires literal count)
    MOVI R11, 0           # i=0
print_before_loop:
    CMP  R0, R11, R2
    JZ   after_before_print
    # load A[i]
    CP   R12, R11
    MUL  R12, R12, R7
    ADD  R14, R1, R12
    LD   R8, R14, 0
    OUT  R8, 0, 4         # print int no newline (subop=2)
    # space between numbers
    MOVI R9, 32
    OUT  R9, 0xFFFF0000
    ADDI R11, R11, 1
    JMP  print_before_loop
after_before_print:
    MOVI R8, 10
    OUT  R8, 0xFFFF0000

    # Bubble sort: repeat passes while any swap occurs
outer_pass:
    MOVI R3, 0            # swapped = 0
    MOVI R11, 0           # j = 0
    # compute limit = N - 1 into R10
    CP   R10, R2
    ADDI R10, R10, -1

inner_loop:
    # Load A[j]
    CP   R12, R11         # R12 = j
    MUL  R12, R12, R7     # j*8
    ADD  R14, R1, R12     # &A[j]
    LD   R8, R14, 0       # A[j]
    # Load A[j+1]
    ADDI R15, R14, 8      # &A[j+1]
    LD   R9, R15, 0
    # Compare A[j] vs A[j+1]; if A[j] > A[j+1] then swap
    CMP  R0, R8, R9       # sets ZERO if equal, NEG if A[j] < A[j+1]
    JZ   no_swap
    JS   no_swap
    # swap
    ST   R9, R14, 0       # A[j] = right
    ST   R8, R15, 0       # A[j+1] = left
    MOVI R3, 1            # swapped = 1
no_swap:
    ADDI R11, R11, 1      # j++
    CMP  R0, R11, R10     # if j < N-1 keep looping
    JS   inner_loop

    # if swapped == 0 -> done
    CMP  R0, R3, R0
    JZ   sorted
    JMP  outer_pass

sorted:
    # Print after: "Array ordenado: "
    MOVI R5, msg5
    OUTS R5, 0xFFFF0008
    
    # Print sorted array with a loop
    MOVI R11, 0
print_after_loop:
    CMP  R0, R11, R2
    JZ   after_after_print
    CP   R12, R11
    MUL  R12, R12, R7
    ADD  R14, R1, R12
    LD   R8, R14, 0
    OUT  R8, 0, 4
    MOVI R9, 32
    OUT  R9, 0xFFFF0000
    ADDI R11, R11, 1
    JMP  print_after_loop
after_after_print:
    MOVI R8, 10
    OUT  R8, 0xFFFF0000

    HALT

# --------------------
# Strings
# --------------------
ORG 0xF000
msg1: DB "=== Bubble Sort - Ordenamiento de numeros ===\n", 0
msg2: DB "Ingrese la cantidad de numeros: ", 0
msg3: DB "Ingrese los numeros separados por espacio:\n", 0
msg4: DB "\nArray original: ", 0
msg5: DB "Array ordenado: ", 0
