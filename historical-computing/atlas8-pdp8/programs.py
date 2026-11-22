"""Small authentic PDP-8 word-code exercises, octal, no cross compiler."""

PROGRAMS = {
    'add': {
        'entry': 0o200,
        'description': 'Add two constants; expect AC=0015 and HLT.',
        'lines': [
            (0o200, [0o7200, 0o1210, 0o1211, 0o7402]),
            (0o210, [0o0007, 0o0006]),
        ],
    },
    'hello': {
        'entry': 0o200,
        'description': 'Native PDP-8 teletype print loop (HELLO PDP-8).',
        'lines': [
            (0o010, [0o0277]),  # autoindex source pointer
            (0o200, [0o6040, 0o7200, 0o1410, 0o7440, 0o5206,
                     0o7402, 0o6041, 0o5206, 0o6046, 0o5201]),
            (0o300, [ord(x) for x in 'HELLO PDP-8\r\n'] + [0]),
        ],
    },
    'count': {
        'entry': 0o200,
        'description': 'ISZ loop increments 7775 to zero and halts.',
        'lines': [
            (0o200, [0o2210, 0o5200, 0o7402]),
            (0o210, [0o7775]),
        ],
    },
}


def load_demo(cpu, name):
    if name not in PROGRAMS:
        raise ValueError('unknown demo: ' + name)
    p = PROGRAMS[name]
    cpu.reset(clear_memory=True)
    for addr, words in p['lines']:
        cpu.load_words(addr, words)
    cpu.pc = p['entry']
    return p['description']

# ---------------------------------------------------------------------------
# Programmable desk-calculator lesson: executable PDP-8 machine words.
# Data: A at 0250, B at 0251, result at 0252, loop counter at 0253.
# The 12-bit arithmetic wraps modulo 4096; signed display is a UI convention.
# ---------------------------------------------------------------------------
CALC_A = 0o250
CALC_B = 0o251
CALC_RESULT = 0o252
CALC_COUNT = 0o253
CALC_ORIGIN = 0o200
CALC_PROGRAMS = {
    'add': [0o7300, 0o1250, 0o1251, 0o3252, 0o1252, 0o7402],
    'subtract': [0o7300, 0o1251, 0o7040, 0o7001,
                 0o1250, 0o3252, 0o1252, 0o7402],
    # Repeated addition, with a two's-complement ISZ loop counter.
    # B=0 is handled explicitly to avoid a 4096-iteration zero loop.
    'multiply': [
        0o7300,  # 0200 CLA CLL
        0o1251,  # 0201 TAD B
        0o7440,  # 0202 SZA
        0o5206,  # 0203 JMP NONZERO
        0o3252,  # 0204 DCA RESULT (zero)
        0o7402,  # 0205 HLT
        0o7040,  # 0206 CMA
        0o7001,  # 0207 IAC
        0o3253,  # 0210 DCA COUNT
        0o7300,  # 0211 CLA CLL
        0o1252,  # 0212 TAD RESULT
        0o1250,  # 0213 TAD A
        0o3252,  # 0214 DCA RESULT
        0o2253,  # 0215 ISZ COUNT
        0o5211,  # 0216 JMP LOOP
        0o7300,  # 0217 CLA CLL
        0o1252,  # 0220 TAD RESULT
        0o7402,  # 0221 HLT
    ],
}

# Real console interaction: OSR reads the 12 physical front-panel switches.
PROGRAMS['switchadd'] = {
    'entry': 0o200,
    'description': 'Desk calculator: OSR reads switches; TAD adds constant at 0250.',
    'lines': [(0o200, [0o7300, 0o7404, 0o1250, 0o7402]),
              (0o250, [0o0007])],
}


def load_calculator(cpu, operation, a, b):
    """Load a genuine machine-language arithmetic program, no host arithmetic."""
    if operation not in CALC_PROGRAMS:
        raise ValueError('calculator operation must be add, subtract or multiply')
    if type(a) is not int or not 0 <= a <= 0o7777:
        raise ValueError('A must be a 12-bit unsigned integer (0..4095)')
    if type(b) is not int or not 0 <= b <= 0o7777:
        raise ValueError('B must be a 12-bit unsigned integer (0..4095)')
    cpu.reset(clear_memory=True)
    cpu.load_words(CALC_ORIGIN, CALC_PROGRAMS[operation])
    cpu.poke(CALC_A, a)
    cpu.poke(CALC_B, b)
    cpu.poke(CALC_RESULT, 0)
    cpu.poke(CALC_COUNT, 0)
    cpu.pc = CALC_ORIGIN
    return CALC_PROGRAMS[operation]
