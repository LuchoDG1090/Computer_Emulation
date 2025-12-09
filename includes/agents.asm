# Runtime library for Communicating Agents
# Implements the "Super Matrix" and agent operations

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================
# The "Super Matrix" is a 3D structure implemented in linear memory.
# Dimensions: [MAX_AGENTS][MAX_AGENTS][MAX_CHANNELS]
# However, for simplicity and memory efficiency, we will use a simpler structure:
# 1. AGENT_TABLE: Stores metadata for each agent (Parent ID, Name Ptr, etc.)
# 2. ADJACENCY_MATRIX: Stores connections. Matrix[OriginID][DestinyID] = ChannelID (or ptr to channel name)

# Constants
# MAX_AGENTS EQU 32
# AGENT_ENTRY_SIZE EQU 4  # ParentID (1), NamePtr (1), Reserved (2)
# MATRIX_SIZE EQU 1024    # 32 * 32

# ==============================================================================
# INITIALIZATION
# ==============================================================================
__AGENT_INIT:
    # Initialize Agent Counter
    MOVI R0, 0
    ST R0, __AGENT_COUNT
    RET

# ==============================================================================
# CREATE AGENT
# Arguments:
#   R1: Parent ID (-1 if none)
#   R2: Name Pointer (0 if none)
# Returns:
#   R0: New Agent ID
# ==============================================================================
__AGENT_CREATE:
    LD R0, __AGENT_COUNT
    
    # Check if max agents reached
    MOVI R3, 32
    CMP R0, R3
    JZ __AGENT_CREATE_FAIL
    
    # Calculate offset in AGENT_TABLE: ID * AGENT_ENTRY_SIZE
    MOVI R3, 4
    MUL R4, R0, R3
    
    # Store Parent ID
    MOVI R5, __AGENT_TABLE
    ADD R5, R5, R4
    ST R1, R5
    
    # Store Name Pointer (Offset + 1)
    MOVI R6, 1
    ADD R5, R5, R6
    ST R2, R5
    
    # Increment Agent Counter
    MOVI R3, 1
    ADD R3, R0, R3
    ST R3, __AGENT_COUNT
    
    RET

__AGENT_CREATE_FAIL:
    MOVI R0, -1
    RET

# ==============================================================================
# LINK AGENT
# Arguments:
#   R1: Origin ID
#   R2: Destiny ID
#   R3: Channel ID/Name Ptr
# ==============================================================================
__AGENT_LINK:
    # Calculate index in Adjacency Matrix: Origin * MAX_AGENTS + Destiny
    MOVI R4, 32
    MUL R5, R1, R4
    ADD R5, R5, R2
    
    # Store Channel ID at Matrix[Index]
    MOVI R6, __ADJACENCY_MATRIX
    ADD R6, R6, R5
    ST R3, R6
    
    RET

# ==============================================================================
# SEND MESSAGE
# Arguments:
#   R1: Message Type Ptr (String)
#   R2: Payload Ptr (Struct)
#   R3: Origin ID
#   R4: Destiny ID
# ==============================================================================
__AGENT_SEND:
    # Print "ACK "
    MOVI R5, __STR_ACK
    OUTS R5, 0xFFFF0008
    
    # Print Type
    OUTS R1, 0xFFFF0008
    
    # Print " inquiry from AGENT-"
    MOVI R5, __STR_FROM
    OUTS R5, 0xFFFF0008
    
    # Print Origin ID
    # OUT R3, 2  <-- This prints to port 2, which might not be console int output in this context
    # Use MMIO_CONSOLE_INT (0xFFFF0008) with subop 2 (signed int no newline) or 4 (unsigned int no newline)
    # OUT instruction: OUT value, target, func
    # func: bit 0 = mode (0=MMIO, 1=PORT), bits 1-3 = subop
    # To print int to console via MMIO:
    # Target = 0xFFFF0008
    # Func = 0 (MMIO mode) | (2 << 1) (subop 2: int no newline) = 4
    
    OUT R3, 0xFFFF0008, 4
    
    # Print " to AGENT-"
    MOVI R5, __STR_TO
    OUTS R5, 0xFFFF0008
    
    # Print Destiny ID
    OUT R4, 0xFFFF0008, 4
    
    # Print Newline
    MOVI R5, __STR_NEWLINE
    OUTS R5, 0xFFFF0008
    
    RET

# Strings for ACK message
__STR_ACK: DB "ACK ", 0
__STR_FROM: DB " inquiry from AGENT-", 0
__STR_TO: DB " to AGENT-", 0
__STR_NEWLINE: DB 10, 0

# ==============================================================================
# UNLINK AGENT
# Arguments:
#   R1: Origin ID
#   R2: Destiny ID
#   R3: Channel ID/Name Ptr
# ==============================================================================
__AGENT_UNLINK:
    # Calculate index in Adjacency Matrix: Origin * MAX_AGENTS + Destiny
    MOVI R4, 32
    MUL R5, R1, R4
    ADD R5, R5, R2
    
    # Clear Channel ID at Matrix[Index] (Set to 0)
    MOVI R6, __ADJACENCY_MATRIX
    ADD R6, R6, R5
    MOVI R7, 0
    ST R7, R6
    
    RET

# ==============================================================================
# MOVE AGENT (Reparent)
# Arguments:
#   R1: Agent ID
#   R2: New Parent ID
# ==============================================================================
__AGENT_MOVE:
    # Calculate offset in AGENT_TABLE: ID * AGENT_ENTRY_SIZE
    MOVI R3, 4
    MUL R4, R1, R3
    
    # Update Parent ID
    MOVI R5, __AGENT_TABLE
    ADD R5, R5, R4
    ST R2, R5
    
    RET

# ==============================================================================
# DUMP AGENTS
# Prints the list of agents and their parents.
# ==============================================================================
__AGENT_DUMP:
    # Print Header
    MOVI R5, __STR_DUMP_HEADER
    OUTS R5, 0xFFFF0008
    
    # Loop through agents
    MOVI R1, 0 # Counter
    LD R2, __AGENT_COUNT
    
__DUMP_LOOP:
    CMP R1, R2
    JNC __DUMP_END
    
    # Print "Agent "
    MOVI R5, __STR_AGENT_PREFIX
    OUTS R5, 0xFFFF0008
    
    # Print ID
    OUT R1, 0xFFFF0008, 4
    
    # Print ": Parent "
    MOVI R5, __STR_PARENT_PREFIX
    OUTS R5, 0xFFFF0008
    
    # Get Parent ID from Table
    MOVI R3, 4
    MUL R4, R1, R3
    MOVI R5, __AGENT_TABLE
    ADD R5, R5, R4
    LD R6, [R5]
    
    # Print Parent ID
    OUT R6, 0xFFFF0008, 2 # Signed int
    
    # Print Newline
    MOVI R5, __STR_NEWLINE
    OUTS R5, 0xFFFF0008
    
    ADDI R1, 1
    JMP __DUMP_LOOP
    
__DUMP_END:
    RET

__STR_DUMP_HEADER: DB "--- AGENT POSITIONS ---", 10, 0
__STR_AGENT_PREFIX: DB "Agent ", 0
__STR_PARENT_PREFIX: DB ": Parent ", 0

# ==============================================================================
# DATA SECTION (To be included in the main data section)
# ==============================================================================
__AGENT_COUNT: DW 0
__AGENT_TABLE: RESW 128  # 32 * 4
__ADJACENCY_MATRIX: RESW 1024 # 32 * 32
