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

    # Prompt for length: "N: "
    MOVI R8, 78           # 'N'
    OUT  R8, 0xFFFF0000
    MOVI R8, 58           # ':'
    OUT  R8, 0xFFFF0000
    MOVI R8, 32           # ' '
    OUT  R8, 0xFFFF0000
    # Read N from console (single integer)
    IN   R2, 0xFFFF0018   # R2 = N (if blank/invalid => 0)
    # If N == 0, fallback to default LEN
    CMP  R0, R2, R0
    JNZ  have_len
    LD   R2, LEN          # absolute load: assembler encodes as I-Type imm
have_len:

    # Prompt for numbers: "Numbers:\n"
    MOVI R8, 78           # 'N'
    OUT  R8, 0xFFFF0000
    MOVI R8, 117          # 'u'
    OUT  R8, 0xFFFF0000
    MOVI R8, 109          # 'm'
    OUT  R8, 0xFFFF0000
    MOVI R8, 98           # 'b'
    OUT  R8, 0xFFFF0000
    MOVI R8, 101          # 'e'
    OUT  R8, 0xFFFF0000
    MOVI R8, 114          # 'r'
    OUT  R8, 0xFFFF0000
    MOVI R8, 115          # 's'
    OUT  R8, 0xFFFF0000
    MOVI R8, 58           # ':'
    OUT  R8, 0xFFFF0000
    MOVI R8, 10           # '\n'
    OUT  R8, 0xFFFF0000

    # Read N integers individually into ARR using IN from console INT MMIO
    MOVI R11, 0           # i = 0
read_input_loop:
    CMP  R0, R11, R2
    JZ   after_input_read
    IN   R8, 0xFFFF0018   # read one int
    CP   R12, R11
    MUL  R12, R12, R7     # i*8
    ADD  R14, R1, R12     # &ARR[i]
    ST   R8, R14, 0
    ADDI R11, R11, 1
    JMP  read_input_loop
after_input_read:

    # Print before: "Before:\n" then array
    MOVI R8, 66           # 'B'
    OUT  R8, 0xFFFF0000
    MOVI R8, 101          # 'e'
    OUT  R8, 0xFFFF0000
    MOVI R8, 102          # 'f'
    OUT  R8, 0xFFFF0000
    MOVI R8, 111          # 'o'
    OUT  R8, 0xFFFF0000
    MOVI R8, 114          # 'r'
    OUT  R8, 0xFFFF0000
    MOVI R8, 101          # 'e'
    OUT  R8, 0xFFFF0000
    MOVI R8, 58           # ':'
    OUT  R8, 0xFFFF0000
    MOVI R8, 10           # '\n'
    OUT  R8, 0xFFFF0000
    # Print array with a loop because OUT array mode isn't allowed
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
    # Print after: "After:\n" then array
    MOVI R8, 65           # 'A'
    OUT  R8, 0xFFFF0000
    MOVI R8, 102          # 'f'
    OUT  R8, 0xFFFF0000
    MOVI R8, 116          # 't'
    OUT  R8, 0xFFFF0000
    MOVI R8, 101          # 'e'
    OUT  R8, 0xFFFF0000
    MOVI R8, 114          # 'r'
    OUT  R8, 0xFFFF0000
    MOVI R8, 58           # ':'
    OUT  R8, 0xFFFF0000
    MOVI R8, 10
    OUT  R8, 0xFFFF0000
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
