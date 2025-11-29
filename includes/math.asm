# Librería matemática básica

FUNC_pow:
    # Args: Stack [RetAddr, Base, Exponent]
    # Ret: R0 (resultado)
    
    POP R14      # Guardar dirección de retorno
    POP R0       # Base
    POP R1       # Exponente
    PUSH R14     # Restaurar dirección de retorno

    PUSH R2      # Guardar registros usados
    PUSH R3

    CP R2, R0    # Guardar base en R2
    
    # Check if exponent is 0
    MOVI R3, 0
    CMP R1, R3
    JNZ pow_check_1
    MOVI R0, 1
    JMP pow_end

  pow_check_1:
    # Loop start
    MOVI R3, 1
    CMP R1, R3
    JZ pow_end   # If exp == 1, done
    
    MUL R0, R0, R2 # R0 = R0 * base
    ADDI R1, R1, -1
    JMP pow_check_1

  pow_end:
    POP R3
    POP R2
    RET

FUNC_abs:
    # Args: Stack [RetAddr, Value]
    # Ret: R0
    
    POP R14
    POP R0
    PUSH R14
    
    PUSH R1
    MOVI R1, 0
    CMP R0, R1
    JS abs_neg
    JMP abs_end

  abs_neg:
    MOVI R1, -1
    MUL R0, R0, R1

  abs_end:
    POP R1
    RET

FUNC_max:
    # Args: Stack [RetAddr, A, B]
    # Ret: R0
    
    POP R14
    POP R0 # A
    POP R1 # B
    PUSH R14
    
    CMP R0, R1
    JS max_use_r1
    RET

  max_use_r1:
    CP R0, R1
    RET
