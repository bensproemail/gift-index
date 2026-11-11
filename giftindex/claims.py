# The tradition's gift claims, with their downside and source label. Wording copied from the Field Guide (v1).
"""Nothing here is proven. Every entry carries a label: RA, BOOK, TEACHER, GK or MINE (see CLAUDE.md).
Channel wording summarizes Chetan Parkyn, Human Design: Discover the Person You Were Born to Be (BOOK);
the page number is kept so each line can be walked back to the book."""

# family -> (what the tradition claims, downside, source label)
FAMILY_CLAIMS = {
    'Spiritual': ("Initiation and awakening. Teachers call 25-51 the shaman's channel.", 'Competitiveness, shock, self-absorption', 'RA for the circuit, TEACHER for "shaman"'),
    'Transformational': ('Mutation and empowerment. Change arrives in pulses and spreads to others.', 'Melancholy, being misunderstood', 'RA'),
    'Entrepreneurial': ('"All about business": money, selling, bargains, ambition.', 'Materialism, manipulation, broken bargains', 'RA'),
    'Mastery': ('Testing patterns, practice toward mastery, leading by logic.', 'Criticism, worry, needing to be right', 'BOOK'),
    'Storyteller': ('Learning through experience and sharing the story.', 'Restlessness, confusion, unfinished cycles', 'BOOK'),
    'Caretaker': ('Nurture, protection and bonding.', 'Caretaking until empty, rushed intimacy', 'BOOK'),
    'Presence': ('Self-empowerment, survival instinct, charisma in action.', 'Busy for its own sake, acting without listening', 'BOOK'),
}

# channel -> (gift claim, off-course side, page in Parkyn)
CHANNEL_CLAIMS = {
    '10-34': ("Following one's own convictions with one's own energy", 'Guilt about being "selfish"', 76),
    '25-51': ('Courage to leap into the unknown', 'Competitive recklessness', 90),
    '1-8': ('Leading by creative example', 'Volunteering before being recognized', 67),
    '2-14': ('Power steered by a clear sense of direction', 'Pushing a direction no one is ready for', 68),
    '3-60': ('Change that comes in sudden pulses', 'Forcing change before the pulse arrives', 69),
    '12-22': ('Emotional openness and grace in words', 'Speaking in a mood', 79),
    '20-57': ('Intuition in the moment', 'Overriding the instant hunch', 86),
    '23-43': ('Breakthrough insight explained simply', 'Speaking too early and being misunderstood', 88),
    '24-61': ('Thinking that turns inspiration into insight', 'Mental loops that never land', 89),
    '28-38': ('Stubborn struggle for what gives life meaning', 'Fighting for its own sake', 94),
    '39-55': ('Emotions as creative fuel', 'Mood decides everything', 101),
    '19-49': ('Sensing needs; principles that hold a group together', 'Over-giving, then cutting people off', 84),
    '21-45': ('Material mastery and managing resources', 'Control and power struggles', 87),
    '26-44': ('Enterprising persuasion; selling what improves lives', 'Manipulation', 92),
    '32-54': ('Ambition; rising through the right connections', 'Workaholism driven by fear of failure', 97),
    '37-40': ('Community built on fair agreements and loyalty', 'Unbalanced bargains', 100),
    '4-63': ('Future-minded thinking that tests every pattern', 'Worry about everything that could go wrong', 70),
    '5-15': ('Natural rhythm and timing', "Being forced onto other people's clocks", 71),
    '7-31': ('Elected leadership people vote for', 'Leading without being chosen', 73),
    '9-52': ('Deep, sustained focus on one thing', 'Unable to start until everything is perfect', 74),
    '16-48': ('Talent that becomes mastery through practice', 'Waiting to feel ready, forever', 82),
    '17-62': ('Organizing facts into a clear opinion and plan', 'Over-explaining; needing to be right', 83),
    '18-58': ('Joyful drive to correct and improve things', 'Constant criticism', 83),
    '11-56': ('Curiosity and storytelling that share meaning', 'Dipping into everything, committing to nothing', 78),
    '13-33': ('Witness of experience; wisdom through retelling', 'Sharing before the experience is digested', 80),
    '29-46': ('Discovery through full commitment', 'Committing to the wrong thing', 95),
    '30-41': ('Imagination and desire that start new cycles', 'Getting lost in fantasy', 96),
    '35-36': ('Hunger for experience; growth through the new', 'Restless, unsatisfying novelty', 99),
    '42-53': ('Life in cycles: start, mature, finish', 'Starting new cycles before finishing old ones', 102),
    '47-64': ('Abstract thinking that makes sense of the past', 'Mental confusion and pressure', 103),
    '6-59': ('Bonding that creates new life and projects', 'Rushing intimacy', 72),
    '27-50': ('Caring values that protect the community', 'Caretaking until empty', 93),
    '10-20': ('Being oneself in the moment; awakening others by example', 'Performing a self rather than being one', 75),
    '10-57': ("Survival instinct; perfecting one's own way of living", 'Ignoring the quiet warning', 77),
    '20-34': ('Busy, charismatic power when doing what one loves', 'Busy for the sake of busy', 85),
    '34-57': ('Instant, powerful action guided by intuition', 'Acting without listening', 98),
}
CHANNEL_CLAIM_LABEL = 'BOOK'

# The four lead Gene Keys of a reading (Richard Rudd's names for them). A separate system: always labeled GK.
GK_SPHERES = [('Life\'s Work', 'personality', 'Sun'), ('Evolution', 'personality', 'Earth'),
              ('Radiance', 'design', 'Sun'), ('Purpose', 'design', 'Earth')]

# The four arrows, in the order chart.describe() writes them (TEACHER; not yet checked against Ra's text).
ARROW_NAMES = ['Motivation (Personality Sun)', 'Perspective (Personality Nodes)',
               'Determination (Design Sun)', 'Environment (Design Nodes)']
