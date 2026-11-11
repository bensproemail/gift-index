# Fixed Human Design tables: the wheel, centers, channels, circuits and the seven gift families.
"""All lookups the chart counter needs. No astronomy in this file."""

# Gate order around the wheel, starting at 2 deg Aquarius (302 deg of tropical longitude).
WHEEL = [41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17, 21, 51, 42, 3, 27, 24, 2, 23, 8, 20, 16, 35,
         45, 12, 15, 52, 39, 53, 62, 56, 31, 33, 7, 4, 29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
         28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58, 38, 54, 61, 60]
START_DEG = 302.0
GATE_DEG = 360.0 / 64          # 5.625
UNITS_PER_GATE = 6 * 6 * 6 * 5  # line x color x tone x base = 1080
UNITS_PER_DEG = UNITS_PER_GATE / GATE_DEG  # 192
TOTAL_UNITS = 64 * UNITS_PER_GATE          # 69120

CENTER_NAMES = ['Head', 'Ajna', 'Throat', 'G', 'Heart', 'Sacral', 'SolarPlexus', 'Spleen', 'Root']
CENTERS = {
    'Head': [64, 61, 63],
    'Ajna': [47, 24, 4, 17, 43, 11],
    'Throat': [62, 23, 56, 35, 12, 45, 33, 8, 31, 20, 16],
    'G': [7, 1, 13, 10, 25, 15, 46, 2],
    'Heart': [21, 40, 26, 51],
    'Sacral': [34, 5, 14, 29, 59, 9, 3, 42, 27],
    'SolarPlexus': [36, 22, 37, 6, 49, 55, 30],
    'Spleen': [48, 57, 44, 50, 32, 28, 18],
    'Root': [53, 60, 52, 19, 39, 41, 58, 38, 54],
}
CENTER_OF = {g: c for c, gs in CENTERS.items() for g in gs}
CENTER_INDEX = {c: i for i, c in enumerate(CENTER_NAMES)}

CHANNELS = [(1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31), (9, 52), (10, 20), (10, 34),
            (10, 57), (11, 56), (12, 22), (13, 33), (16, 48), (17, 62), (18, 58), (19, 49), (20, 34),
            (20, 57), (21, 45), (23, 43), (24, 61), (25, 51), (26, 44), (27, 50), (28, 38), (29, 46),
            (30, 41), (32, 54), (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64)]
CHANNEL_KEYS = ['%d-%d' % c for c in CHANNELS]

# Common channel names (Ra Uru Hu's keynote names as widely published).
CHANNEL_NAMES = {
    '1-8': 'Inspiration', '2-14': 'The Beat', '3-60': 'Mutation', '4-63': 'Logic', '5-15': 'Rhythm',
    '6-59': 'Mating (Intimacy)', '7-31': 'The Alpha', '9-52': 'Concentration', '10-20': 'Awakening',
    '10-34': 'Exploration', '10-57': 'Perfected Form', '11-56': 'Curiosity', '12-22': 'Openness',
    '13-33': 'The Prodigal', '16-48': 'The Wavelength (Talent)', '17-62': 'Acceptance',
    '18-58': 'Judgment', '19-49': 'Synthesis', '20-34': 'Charisma', '20-57': 'The Brainwave',
    '21-45': 'Money', '23-43': 'Structuring', '24-61': 'Awareness', '25-51': 'Initiation',
    '26-44': 'Surrender', '27-50': 'Preservation', '28-38': 'Struggle', '29-46': 'Discovery',
    '30-41': 'Recognition', '32-54': 'Transformation', '34-57': 'Power', '35-36': 'Transitoriness',
    '37-40': 'Community', '39-55': 'Emoting', '42-53': 'Maturation', '47-64': 'Abstraction',
}

# The seven circuit structures of the BodyGraph. Each of the 36 channels sits in exactly one.
CIRCUITS = {
    'Individual / Knowing': ['24-61', '23-43', '12-22', '39-55', '28-38', '20-57', '3-60', '2-14', '1-8'],
    'Individual / Centering': ['25-51', '10-34'],
    'Individual / Integration': ['20-34', '34-57', '10-20', '10-57'],
    'Tribal / Ego': ['26-44', '21-45', '37-40', '19-49', '32-54'],
    'Tribal / Defense': ['27-50', '6-59'],
    'Collective / Logic': ['4-63', '17-62', '9-52', '5-15', '7-31', '18-58', '16-48'],
    'Collective / Sensing': ['47-64', '11-56', '42-53', '29-46', '13-33', '30-41', '35-36'],
}

# Gift families (Ben, Nov 11 2026: full set, all equal). One family per circuit structure.
FAMILIES = [
    ('Spiritual', 'Individual / Centering'),
    ('Transformational', 'Individual / Knowing'),
    ('Entrepreneurial', 'Tribal / Ego'),
    ('Mastery', 'Collective / Logic'),
    ('Storyteller', 'Collective / Sensing'),
    ('Caretaker', 'Tribal / Defense'),
    ('Presence', 'Individual / Integration'),
]
FAMILY_NAMES = [f for f, _ in FAMILIES]
FAMILY_OF_CHANNEL = {ch: fam for fam, circ in FAMILIES for ch in CIRCUITS[circ]}

BODIES = ['Sun', 'Earth', 'NorthNode', 'SouthNode', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter',
          'Saturn', 'Uranus', 'Neptune', 'Pluto']

TYPES = ['Generator', 'Manifesting Generator', 'Projector', 'Manifestor', 'Reflector']
AUTHORITIES = ['Emotional', 'Sacral', 'Splenic', 'Ego Manifested', 'Ego Projected', 'Self-Projected',
               'Mental', 'Lunar']
DEFINITIONS = ['None', 'Single', 'Split', 'Triple Split', 'Quadruple Split']
PROFILES = ['1/3', '1/4', '2/4', '2/5', '3/5', '3/6', '4/6', '4/1', '5/1', '5/2', '6/2', '6/3']
ANGLES = ['Right Angle', 'Juxtaposition', 'Left Angle']
