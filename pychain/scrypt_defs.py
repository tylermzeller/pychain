# To reference all definitions in the file, please see
# https://github.com/bitcoin/bitcoin/tree/master/src/script

# Maximum number of bytes pushable to the stack
MAX_SCRIPT_ELEMENT_SIZE = 520;

# Maximum number of non-push operations per script
MAX_OPS_PER_SCRIPT = 201;

# Maximum script length in bytes
MAX_SCRIPT_SIZE = 10000;

# Maximum number of values on script interpreter stack
MAX_STACK_SIZE = 1000;

# push value
OP_0 = 0x00
OP_FALSE = OP_0
OP_PUSHDATA1 = 0x4c
OP_PUSHDATA2 = 0x4d
OP_PUSHDATA4 = 0x4e
OP_1NEGATE = 0x4f
OP_RESERVED = 0x50
OP_1 = 0x51
OP_TRUE=OP_1
OP_2 = 0x52
OP_3 = 0x53
OP_4 = 0x54
OP_5 = 0x55
OP_6 = 0x56
OP_7 = 0x57
OP_8 = 0x58
OP_9 = 0x59
OP_10 = 0x5a
OP_11 = 0x5b
OP_12 = 0x5c
OP_13 = 0x5d
OP_14 = 0x5e
OP_15 = 0x5f
OP_16 = 0x60

# control
OP_NOP = 0x61
OP_VER = 0x62
OP_IF = 0x63
OP_NOTIF = 0x64
OP_VERIF = 0x65
OP_VERNOTIF = 0x66
OP_ELSE = 0x67
OP_ENDIF = 0x68
OP_VERIFY = 0x69
OP_RETURN = 0x6a

# stack ops
OP_TOALTSTACK = 0x6b
OP_FROMALTSTACK = 0x6c
OP_2DROP = 0x6d
OP_2DUP = 0x6e
OP_3DUP = 0x6f
OP_2OVER = 0x70
OP_2ROT = 0x71
OP_2SWAP = 0x72
OP_IFDUP = 0x73
OP_DEPTH = 0x74
OP_DROP = 0x75
OP_DUP = 0x76
OP_NIP = 0x77
OP_OVER = 0x78
OP_PICK = 0x79
OP_ROLL = 0x7a
OP_ROT = 0x7b
OP_SWAP = 0x7c
OP_TUCK = 0x7d

# splice ops
OP_CAT = 0x7e
OP_SUBSTR = 0x7f
OP_LEFT = 0x80
OP_RIGHT = 0x81
OP_SIZE = 0x82

# bit logic
OP_INVERT = 0x83
OP_AND = 0x84
OP_OR = 0x85
OP_XOR = 0x86
OP_EQUAL = 0x87
OP_EQUALVERIFY = 0x88
OP_RESERVED1 = 0x89
OP_RESERVED2 = 0x8a

# numeric
OP_1ADD = 0x8b
OP_1SUB = 0x8c
OP_2MUL = 0x8d
OP_2DIV = 0x8e
OP_NEGATE = 0x8f
OP_ABS = 0x90
OP_NOT = 0x91
OP_0NOTEQUAL = 0x92

OP_ADD = 0x93
OP_SUB = 0x94
OP_MUL = 0x95
OP_DIV = 0x96
OP_MOD = 0x97
OP_LSHIFT = 0x98
OP_RSHIFT = 0x99

OP_BOOLAND = 0x9a
OP_BOOLOR = 0x9b
OP_NUMEQUAL = 0x9c
OP_NUMEQUALVERIFY = 0x9d
OP_NUMNOTEQUAL = 0x9e
OP_LESSTHAN = 0x9f
OP_GREATERTHAN = 0xa0
OP_LESSTHANOREQUAL = 0xa1
OP_GREATERTHANOREQUAL = 0xa2
OP_MIN = 0xa3
OP_MAX = 0xa4

OP_WITHIN = 0xa5

# crypto
OP_RIPEMD160 = 0xa6
OP_SHA1 = 0xa7
OP_SHA256 = 0xa8
OP_HASH160 = 0xa9
OP_HASH256 = 0xaa
OP_CODESEPARATOR = 0xab
OP_CHECKSIG = 0xac
OP_CHECKSIGVERIFY = 0xad
OP_CHECKMULTISIG = 0xae
OP_CHECKMULTISIGVERIFY = 0xaf

# expansion
OP_NOP1 = 0xb0
OP_CHECKLOCKTIMEVERIFY = 0xb1
OP_NOP2 = OP_CHECKLOCKTIMEVERIFY
OP_CHECKSEQUENCEVERIFY = 0xb2
OP_NOP3 = OP_CHECKSEQUENCEVERIFY
OP_NOP4 = 0xb3
OP_NOP5 = 0xb4
OP_NOP6 = 0xb5
OP_NOP7 = 0xb6
OP_NOP8 = 0xb7
OP_NOP9 = 0xb8
OP_NOP10 = 0xb9

OP_INVALIDOPCODE = 0xff

MAX_OPCODE = OP_NOP10

class ScryptError:
    class SCRIPT_ERR_OK: pass
    class SCRIPT_ERR_UNKNOWN_ERROR: pass
    class SCRIPT_ERR_EVAL_FALSE: pass
    class SCRIPT_ERR_OP_RETURN: pass

    # Max sizes
    class SCRIPT_ERR_SCRIPT_SIZE: pass
    class SCRIPT_ERR_PUSH_SIZE: pass
    class SCRIPT_ERR_OP_COUNT: pass
    class SCRIPT_ERR_STACK_SIZE: pass
    class SCRIPT_ERR_SIG_COUNT: pass
    class SCRIPT_ERR_PUBKEY_COUNT: pass

    # Failed verify operations
    class SCRIPT_ERR_VERIFY: pass
    class SCRIPT_ERR_EQUALVERIFY: pass
    class SCRIPT_ERR_CHECKMULTISIGVERIFY: pass
    class SCRIPT_ERR_CHECKSIGVERIFY: pass
    class SCRIPT_ERR_NUMEQUALVERIFY: pass

    # Logical/Format/Canonical errors
    class SCRIPT_ERR_BAD_OPCODE: pass
    class SCRIPT_ERR_DISABLED_OPCODE: pass
    class SCRIPT_ERR_INVALID_STACK_OPERATION: pass
    class SCRIPT_ERR_INVALID_ALTSTACK_OPERATION: pass
    class SCRIPT_ERR_UNBALANCED_CONDITIONAL: pass

    # CHECKLOCKTIMEVERIFY and CHECKSEQUENCEVERIFY
    class SCRIPT_ERR_NEGATIVE_LOCKTIME: pass
    class SCRIPT_ERR_UNSATISFIED_LOCKTIME: pass

    # Malleability
    class SCRIPT_ERR_SIG_HASHTYPE: pass
    class SCRIPT_ERR_SIG_DER: pass
    class SCRIPT_ERR_MINIMALDATA: pass
    class SCRIPT_ERR_SIG_PUSHONLY: pass
    class SCRIPT_ERR_SIG_HIGH_S: pass
    class SCRIPT_ERR_SIG_NULLDUMMY: pass
    class SCRIPT_ERR_PUBKEYTYPE: pass
    class SCRIPT_ERR_CLEANSTACK: pass
    class SCRIPT_ERR_MINIMALIF: pass
    class SCRIPT_ERR_SIG_NULLFAIL: pass

    # softfork safeness
    class SCRIPT_ERR_DISCOURAGE_UPGRADABLE_NOPS: pass
    class SCRIPT_ERR_DISCOURAGE_UPGRADABLE_WITNESS_PROGRAM: pass

    # segregated witness
    class SCRIPT_ERR_WITNESS_PROGRAM_WRONG_LENGTH: pass
    class SCRIPT_ERR_WITNESS_PROGRAM_WITNESS_EMPTY: pass
    class SCRIPT_ERR_WITNESS_PROGRAM_MISMATCH: pass
    class SCRIPT_ERR_WITNESS_MALLEATED: pass
    class SCRIPT_ERR_WITNESS_MALLEATED_P2SH: pass
    class SCRIPT_ERR_WITNESS_UNEXPECTED: pass
    class SCRIPT_ERR_WITNESS_PUBKEYTYPE: pass

    # Constant scriptCode
    class SCRIPT_ERR_OP_CODESEPARATOR: pass
    class SCRIPT_ERR_SIG_FINDANDDELETE: pass

    class SCRIPT_ERR_ERROR_COUNT: pass
