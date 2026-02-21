"""
VidyaSetu AI — Fallback Challenges
Grade and subject calibrated questions for all 5 grades x 5 subjects
Structure: FALLBACK_CHALLENGES[subject][grade] = [list of questions]
"""

import random

FALLBACK_CHALLENGES = {

    # ══════════════════════════════════════════════════════
    # MATH
    # ══════════════════════════════════════════════════════
    "Math": {
        1: [
            {
                "question": "Viddy has 3 mangoes 🥭. His friend gives him 2 more. How many mangoes does Viddy have now?",
                "options": ["4", "5", "6", "3"],
                "correct": "5",
                "explanation": "3 + 2 = 5. We add them together! 🎉",
                "trait": "math"
            },
            {
                "question": "There are 5 birds 🐦 on a tree. 2 fly away. How many are left?",
                "options": ["2", "3", "4", "5"],
                "correct": "3",
                "explanation": "5 - 2 = 3. Two birds flew away so 3 stay! ⭐",
                "trait": "math"
            },
            {
                "question": "Which number comes after 7?",
                "options": ["6", "8", "9", "5"],
                "correct": "8",
                "explanation": "After 7 comes 8! We count: 6, 7, 8... 🌟",
                "trait": "math"
            },
            {
                "question": "How many sides does a triangle have?",
                "options": ["2", "3", "4", "5"],
                "correct": "3",
                "explanation": "A triangle has 3 sides! Tri means three! 🔺",
                "trait": "math"
            },
        ],
        2: [
            {
                "question": "Meena had 15 toffees 🍬. She gave 6 to her friend. How many are left?",
                "options": ["7", "8", "9", "10"],
                "correct": "9",
                "explanation": "15 - 6 = 9. We subtract to find what's left! ⭐",
                "trait": "math"
            },
            {
                "question": "What is 4 × 3?",
                "options": ["7", "10", "12", "14"],
                "correct": "12",
                "explanation": "4 groups of 3 = 12. Count: 3, 6, 9, 12! 🌟",
                "trait": "math"
            },
            {
                "question": "Which shape has 4 equal sides?",
                "options": ["Rectangle", "Triangle", "Square", "Circle"],
                "correct": "Square",
                "explanation": "A square has 4 equal sides and 4 corners! ⬛",
                "trait": "math"
            },
            {
                "question": "Raju bought a pencil for ₹5 and an eraser for ₹3. How much did he spend?",
                "options": ["₹6", "₹7", "₹8", "₹9"],
                "correct": "₹8",
                "explanation": "5 + 3 = 8 rupees! We add the costs together. 💰",
                "trait": "math"
            },
        ],
        3: [
            {
                "question": "What is 24 ÷ 6?",
                "options": ["3", "4", "5", "6"],
                "correct": "4",
                "explanation": "24 ÷ 6 = 4. If you share 24 things equally among 6 people, each gets 4! 🎯",
                "trait": "math"
            },
            {
                "question": "In a fraction ¾, what is the numerator?",
                "options": ["4", "3", "7", "1"],
                "correct": "3",
                "explanation": "The numerator is the TOP number in a fraction. In ¾, the top is 3! 📚",
                "trait": "math"
            },
            {
                "question": "What is the perimeter of a square with side 5 cm?",
                "options": ["10 cm", "15 cm", "20 cm", "25 cm"],
                "correct": "20 cm",
                "explanation": "Perimeter = 4 × side = 4 × 5 = 20 cm! We add all 4 sides. ✏️",
                "trait": "math"
            },
            {
                "question": "Which number is between 450 and 500?",
                "options": ["400", "449", "475", "510"],
                "correct": "475",
                "explanation": "475 comes between 450 and 500 on the number line! 🔢",
                "trait": "math"
            },
        ],
        4: [
            {
                "question": "What is 15% of 200?",
                "options": ["20", "25", "30", "35"],
                "correct": "30",
                "explanation": "15% of 200 = (15/100) × 200 = 30. Percent means per hundred! 💡",
                "trait": "math"
            },
            {
                "question": "The area of a rectangle is 48 cm². If length is 8 cm, what is the breadth?",
                "options": ["4 cm", "5 cm", "6 cm", "7 cm"],
                "correct": "6 cm",
                "explanation": "Area = length × breadth. So breadth = 48 ÷ 8 = 6 cm! 📐",
                "trait": "math"
            },
            {
                "question": "Which of these is a prime number?",
                "options": ["9", "15", "17", "21"],
                "correct": "17",
                "explanation": "17 has only 2 factors: 1 and 17 itself. That makes it prime! 🔢",
                "trait": "math"
            },
            {
                "question": "What is the LCM of 4 and 6?",
                "options": ["8", "10", "12", "24"],
                "correct": "12",
                "explanation": "Multiples of 4: 4,8,12. Multiples of 6: 6,12. First common one is 12! 🎯",
                "trait": "math"
            },
        ],
        5: [
            {
                "question": "A shopkeeper buys an item for ₹400 and sells it for ₹500. What is the profit percentage?",
                "options": ["20%", "25%", "30%", "15%"],
                "correct": "25%",
                "explanation": "Profit = 500-400 = ₹100. Profit% = (100/400)×100 = 25%! 📊",
                "trait": "math"
            },
            {
                "question": "What is the volume of a cube with side 3 cm?",
                "options": ["9 cm³", "18 cm³", "27 cm³", "36 cm³"],
                "correct": "27 cm³",
                "explanation": "Volume of cube = side³ = 3×3×3 = 27 cm³! 📦",
                "trait": "math"
            },
            {
                "question": "The ratio of boys to girls in a class is 3:2. If there are 30 students, how many are girls?",
                "options": ["10", "12", "15", "18"],
                "correct": "12",
                "explanation": "Total parts = 5. Girls = (2/5) × 30 = 12! Ratios divide the total. 🎯",
                "trait": "math"
            },
            {
                "question": "What is the average of 10, 20, 30, 40, 50?",
                "options": ["25", "30", "35", "40"],
                "correct": "30",
                "explanation": "Average = Sum ÷ Count = (10+20+30+40+50) ÷ 5 = 150 ÷ 5 = 30! 📈",
                "trait": "math"
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # SCIENCE / EVS
    # ══════════════════════════════════════════════════════
    "Science/EVS": {
        1: [
            {
                "question": "Which animal gives us milk? 🐄",
                "options": ["Dog", "Cat", "Cow", "Fish"],
                "correct": "Cow",
                "explanation": "Cows give us milk! We drink it every day! 🥛",
                "trait": "logical_reasoning"
            },
            {
                "question": "What do plants need to grow? 🌱",
                "options": ["Toys", "Sunlight and Water", "Books", "Music"],
                "correct": "Sunlight and Water",
                "explanation": "Plants need sunlight and water to grow big and strong! ☀️💧",
                "trait": "logical_reasoning"
            },
            {
                "question": "Which is the biggest source of light in the sky?",
                "options": ["Moon", "Stars", "Sun", "Clouds"],
                "correct": "Sun",
                "explanation": "The Sun gives us light and warmth every day! ☀️",
                "trait": "logical_reasoning"
            },
        ],
        2: [
            {
                "question": "Which part of the plant makes food using sunlight?",
                "options": ["Root", "Stem", "Leaf", "Flower"],
                "correct": "Leaf",
                "explanation": "Leaves use sunlight to make food for the plant — like a mini kitchen! 🍃",
                "trait": "logical_reasoning"
            },
            {
                "question": "What do we breathe in to stay alive?",
                "options": ["Carbon Dioxide", "Oxygen", "Smoke", "Steam"],
                "correct": "Oxygen",
                "explanation": "We breathe in oxygen! Plants give us oxygen — that's why trees are important! 🌳",
                "trait": "logical_reasoning"
            },
            {
                "question": "Which of these is a living thing?",
                "options": ["Rock", "Water", "Butterfly", "Chair"],
                "correct": "Butterfly",
                "explanation": "A butterfly is living — it grows, eats, and moves on its own! 🦋",
                "trait": "logical_reasoning"
            },
        ],
        3: [
            {
                "question": "What is the process by which plants make their own food called?",
                "options": ["Respiration", "Digestion", "Photosynthesis", "Evaporation"],
                "correct": "Photosynthesis",
                "explanation": "Photosynthesis! Plants use sunlight, water and CO₂ to make food. Photo means light! 🌿",
                "trait": "logical_reasoning"
            },
            {
                "question": "Which state of matter has no fixed shape or volume?",
                "options": ["Solid", "Liquid", "Gas", "Ice"],
                "correct": "Gas",
                "explanation": "Gas spreads everywhere — it has no fixed shape or volume, like air! 💨",
                "trait": "logical_reasoning"
            },
            {
                "question": "What is the main function of roots in a plant?",
                "options": ["Making food", "Absorbing water and minerals", "Producing flowers", "Making seeds"],
                "correct": "Absorbing water and minerals",
                "explanation": "Roots absorb water and minerals from soil and anchor the plant firmly! 🌱",
                "trait": "logical_reasoning"
            },
        ],
        4: [
            {
                "question": "Which organ pumps blood throughout the body?",
                "options": ["Lungs", "Brain", "Heart", "Kidney"],
                "correct": "Heart",
                "explanation": "The heart pumps blood to all parts of the body — it beats about 72 times per minute! ❤️",
                "trait": "logical_reasoning"
            },
            {
                "question": "What type of force keeps planets moving around the Sun?",
                "options": ["Magnetic force", "Frictional force", "Gravitational force", "Electric force"],
                "correct": "Gravitational force",
                "explanation": "Gravity from the Sun keeps planets in their orbits — the same force that makes things fall down! 🪐",
                "trait": "logical_reasoning"
            },
            {
                "question": "Which gas do plants release during photosynthesis?",
                "options": ["Carbon Dioxide", "Nitrogen", "Oxygen", "Hydrogen"],
                "correct": "Oxygen",
                "explanation": "Plants release oxygen during photosynthesis — that's why forests are called the lungs of the Earth! 🌍",
                "trait": "logical_reasoning"
            },
        ],
        5: [
            {
                "question": "What is the function of chlorophyll in plants?",
                "options": ["Absorb water", "Absorb sunlight for photosynthesis", "Transport food", "Protect leaves"],
                "correct": "Absorb sunlight for photosynthesis",
                "explanation": "Chlorophyll is the green pigment that absorbs sunlight to power photosynthesis! 🌿",
                "trait": "logical_reasoning"
            },
            {
                "question": "Which part of the cell controls all its activities?",
                "options": ["Cell wall", "Cytoplasm", "Nucleus", "Vacuole"],
                "correct": "Nucleus",
                "explanation": "The nucleus is the control centre of the cell — like the brain of the cell! 🔬",
                "trait": "logical_reasoning"
            },
            {
                "question": "What happens to water during evaporation?",
                "options": ["It turns to ice", "It turns to gas/vapour", "It becomes heavier", "It disappears"],
                "correct": "It turns to gas/vapour",
                "explanation": "During evaporation, liquid water absorbs heat and turns into water vapour — part of the water cycle! 💧",
                "trait": "logical_reasoning"
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # ENGLISH
    # ══════════════════════════════════════════════════════
    "English": {
        1: [
            {
                "question": "Which of these is a name of a person? 👦",
                "options": ["Run", "Arjun", "Happy", "Big"],
                "correct": "Arjun",
                "explanation": "Arjun is a name! Names of people are called Proper Nouns! 🌟",
                "trait": "pattern_recognition"
            },
            {
                "question": "Which word shows action? 🏃",
                "options": ["Mango", "Jump", "Red", "School"],
                "correct": "Jump",
                "explanation": "Jump is something you DO! Words that show action are called VERBS! ⭐",
                "trait": "pattern_recognition"
            },
            {
                "question": "How many letters are in the word CAT?",
                "options": ["2", "3", "4", "5"],
                "correct": "3",
                "explanation": "C-A-T has 3 letters! Let's count them together! 🐱",
                "trait": "pattern_recognition"
            },
        ],
        2: [
            {
                "question": "Which sentence uses a full stop correctly?",
                "options": ["The cat sat", "The cat sat.", "the cat sat.", "The cat sat!"],
                "correct": "The cat sat.",
                "explanation": "A sentence ends with a full stop (.) and starts with a capital letter! ✍️",
                "trait": "pattern_recognition"
            },
            {
                "question": "Which word is the opposite of 'hot'?",
                "options": ["Warm", "Cold", "Big", "Fast"],
                "correct": "Cold",
                "explanation": "Cold is the opposite of hot! Opposites are called Antonyms! 🌡️",
                "trait": "pattern_recognition"
            },
            {
                "question": "Which of these is a describing word (adjective)?",
                "options": ["Run", "Mango", "Beautiful", "Quickly"],
                "correct": "Beautiful",
                "explanation": "Beautiful describes something! Words that describe are adjectives! 🌸",
                "trait": "pattern_recognition"
            },
        ],
        3: [
            {
                "question": "Which sentence is in past tense?",
                "options": ["She sings daily.", "She will sing.", "She sang yesterday.", "She is singing."],
                "correct": "She sang yesterday.",
                "explanation": "'Sang' tells us it happened in the PAST. Past tense = something already done! 📅",
                "trait": "pattern_recognition"
            },
            {
                "question": "What is the plural of 'child'?",
                "options": ["Childs", "Childes", "Children", "Childrens"],
                "correct": "Children",
                "explanation": "Child → Children is an irregular plural! Not all words just add 's'! 📚",
                "trait": "pattern_recognition"
            },
            {
                "question": "Which word is a synonym of 'happy'?",
                "options": ["Sad", "Angry", "Joyful", "Tired"],
                "correct": "Joyful",
                "explanation": "Joyful means the same as happy! Words with similar meanings are synonyms! 😊",
                "trait": "pattern_recognition"
            },
        ],
        4: [
            {
                "question": "Identify the conjunction in: 'I like tea but she prefers coffee.'",
                "options": ["I", "like", "but", "prefers"],
                "correct": "but",
                "explanation": "'But' joins two sentences/ideas together — that makes it a conjunction! 🔗",
                "trait": "pattern_recognition"
            },
            {
                "question": "Which of these is a compound sentence?",
                "options": [
                    "She ran fast.",
                    "She ran fast and she won the race.",
                    "Running fast helps win.",
                    "The fast runner won."
                ],
                "correct": "She ran fast and she won the race.",
                "explanation": "A compound sentence has two independent clauses joined by a conjunction (and, but, or)! ✍️",
                "trait": "pattern_recognition"
            },
            {
                "question": "What is the passive voice of: 'Ram ate the apple'?",
                "options": [
                    "The apple ate Ram.",
                    "The apple was eaten by Ram.",
                    "Ram is eating the apple.",
                    "Ram will eat the apple."
                ],
                "correct": "The apple was eaten by Ram.",
                "explanation": "In passive voice, the object becomes the subject. The apple (object) comes first! 📖",
                "trait": "pattern_recognition"
            },
        ],
        5: [
            {
                "question": "Which figure of speech is used in: 'The wind whispered through the trees'?",
                "options": ["Simile", "Metaphor", "Personification", "Alliteration"],
                "correct": "Personification",
                "explanation": "Wind can't actually whisper — giving human qualities to non-human things is Personification! 🌬️",
                "trait": "pattern_recognition"
            },
            {
                "question": "What does the prefix 'un-' mean in the word 'unhappy'?",
                "options": ["Very", "Not", "Again", "Before"],
                "correct": "Not",
                "explanation": "Un- means NOT. Unhappy = not happy. Other examples: unkind, unfair, unable! 📚",
                "trait": "pattern_recognition"
            },
            {
                "question": "Which type of noun is 'team' in: 'The team won the match'?",
                "options": ["Proper noun", "Abstract noun", "Collective noun", "Material noun"],
                "correct": "Collective noun",
                "explanation": "A collective noun names a GROUP of things/people. Team, flock, herd are collective nouns! 🏏",
                "trait": "pattern_recognition"
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # HINDI
    # ══════════════════════════════════════════════════════
    "Hindi": {
        1: [
            {
                "question": "इनमें से कौन सा फल है? 🍎",
                "options": ["कुर्सी", "आम", "किताब", "पेन"],
                "correct": "आम",
                "explanation": "आम एक फल है! आम बहुत मीठा होता है! 🥭",
                "trait": "pattern_recognition"
            },
            {
                "question": "'अ' से शुरू होने वाला शब्द कौन सा है?",
                "options": ["बिल्ली", "आम", "घर", "पानी"],
                "correct": "आम",
                "explanation": "आम 'अ' से शुरू होता है! बहुत अच्छे! ⭐",
                "trait": "pattern_recognition"
            },
            {
                "question": "इनमें से कौन सा जानवर है? 🐄",
                "options": ["मेज़", "गाय", "कमरा", "पेड़"],
                "correct": "गाय",
                "explanation": "गाय एक जानवर है! गाय हमें दूध देती है! 🥛",
                "trait": "pattern_recognition"
            },
        ],
        2: [
            {
                "question": "संज्ञा किसे कहते हैं?",
                "options": ["काम करने वाले शब्द को", "किसी के नाम को", "विशेषता बताने वाले को", "कोई नहीं"],
                "correct": "किसी के नाम को",
                "explanation": "किसी व्यक्ति, वस्तु या स्थान के नाम को संज्ञा कहते हैं! जैसे: राम, दिल्ली, आम! 📚",
                "trait": "pattern_recognition"
            },
            {
                "question": "'राम स्कूल जाता है।' — इस वाक्य में क्रिया कौन सी है?",
                "options": ["राम", "स्कूल", "जाता है", "इनमें से कोई नहीं"],
                "correct": "जाता है",
                "explanation": "'जाता है' काम बताता है इसलिए यह क्रिया है! क्रिया = काम बताने वाला शब्द! 🌟",
                "trait": "pattern_recognition"
            },
        ],
        3: [
            {
                "question": "'खुश' शब्द का विलोम (opposite) क्या है?",
                "options": ["प्रसन्न", "दुखी", "अच्छा", "बड़ा"],
                "correct": "दुखी",
                "explanation": "खुश का विलोम दुखी है! विलोम शब्द उल्टे अर्थ वाले शब्द होते हैं! 📖",
                "trait": "pattern_recognition"
            },
            {
                "question": "वचन बदलो — 'लड़की' का बहुवचन क्या होगा?",
                "options": ["लड़कियाँ", "लड़कियों", "लड़कीएँ", "लड़कीस"],
                "correct": "लड़कियाँ",
                "explanation": "लड़की → लड़कियाँ! एक से ज़्यादा के लिए बहुवचन होता है! 📚",
                "trait": "pattern_recognition"
            },
            {
                "question": "इनमें से सर्वनाम कौन सा है?",
                "options": ["राम", "दिल्ली", "वह", "आम"],
                "correct": "वह",
                "explanation": "'वह' संज्ञा की जगह आता है इसलिए सर्वनाम है! जैसे: वह, हम, तुम, मैं! 🌟",
                "trait": "pattern_recognition"
            },
        ],
        4: [
            {
                "question": "'कमल' शब्द का पर्यायवाची (synonym) क्या है?",
                "options": ["सूरज", "पद्म", "नदी", "पहाड़"],
                "correct": "पद्म",
                "explanation": "पद्म, कमल का पर्यायवाची है! पद्म भी कमल के फूल को कहते हैं! 🌸",
                "trait": "pattern_recognition"
            },
            {
                "question": "लिंग बदलो — 'राजा' का स्त्रीलिंग क्या है?",
                "options": ["रानी", "राजकुमारी", "राज्ञी", "देवी"],
                "correct": "रानी",
                "explanation": "राजा (पुल्लिंग) → रानी (स्त्रीलिंग)! लिंग बदलने से शब्द का रूप बदलता है! 👑",
                "trait": "pattern_recognition"
            },
        ],
        5: [
            {
                "question": "मुहावरे का अर्थ बताओ — 'आँखें खुलना'",
                "options": ["नींद से जागना", "सच्चाई का पता चलना", "आँखें बड़ी होना", "रोना बंद करना"],
                "correct": "सच्चाई का पता चलना",
                "explanation": "'आँखें खुलना' का अर्थ है सच्चाई या हकीकत का पता चलना! मुहावरे का शाब्दिक अर्थ नहीं होता! 📚",
                "trait": "pattern_recognition"
            },
            {
                "question": "काल पहचानो — 'बच्चे कल खेलेंगे।'",
                "options": ["भूतकाल", "वर्तमान काल", "भविष्यकाल", "सामान्यकाल"],
                "correct": "भविष्यकाल",
                "explanation": "'खेलेंगे' भविष्य में होने वाले काम को बताता है! कल = आने वाला समय = भविष्यकाल! 🕐",
                "trait": "pattern_recognition"
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # GENERAL KNOWLEDGE
    # ══════════════════════════════════════════════════════
    "General Knowledge": {
        1: [
            {
                "question": "What colour is the sky on a sunny day? ☀️",
                "options": ["Green", "Red", "Blue", "Yellow"],
                "correct": "Blue",
                "explanation": "The sky is blue on a sunny day! Have you looked up today? 🌤️",
                "trait": "logical_reasoning"
            },
            {
                "question": "How many days are in a week?",
                "options": ["5", "6", "7", "8"],
                "correct": "7",
                "explanation": "There are 7 days in a week: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday! 📅",
                "trait": "logical_reasoning"
            },
            {
                "question": "What is the national animal of India? 🐯",
                "options": ["Lion", "Elephant", "Tiger", "Peacock"],
                "correct": "Tiger",
                "explanation": "The Tiger is India's national animal! We must protect them! 🐯",
                "trait": "logical_reasoning"
            },
        ],
        2: [
            {
                "question": "Which is the capital of India?",
                "options": ["Mumbai", "Chennai", "New Delhi", "Kolkata"],
                "correct": "New Delhi",
                "explanation": "New Delhi is the capital of India — that's where our government is! 🏛️",
                "trait": "logical_reasoning"
            },
            {
                "question": "What is the national bird of India?",
                "options": ["Sparrow", "Peacock", "Parrot", "Eagle"],
                "correct": "Peacock",
                "explanation": "The Peacock is India's national bird! It has beautiful colourful feathers! 🦚",
                "trait": "logical_reasoning"
            },
            {
                "question": "How many months are in a year?",
                "options": ["10", "11", "12", "13"],
                "correct": "12",
                "explanation": "There are 12 months in a year! January to December! 📅",
                "trait": "logical_reasoning"
            },
        ],
        3: [
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Jupiter", "Mars", "Saturn"],
                "correct": "Mars",
                "explanation": "Mars looks red because its soil has iron oxide (rust)! ISRO sent Mangalyaan there! 🔴",
                "trait": "logical_reasoning"
            },
            {
                "question": "Who wrote the Indian National Anthem?",
                "options": ["Mahatma Gandhi", "Rabindranath Tagore", "Jawaharlal Nehru", "B.R. Ambedkar"],
                "correct": "Rabindranath Tagore",
                "explanation": "Jana Gana Mana was written by Rabindranath Tagore who also won the Nobel Prize! 🎵",
                "trait": "logical_reasoning"
            },
            {
                "question": "Which is the longest river in India?",
                "options": ["Yamuna", "Brahmaputra", "Ganga", "Godavari"],
                "correct": "Ganga",
                "explanation": "The Ganga is India's longest river flowing through many states! It's also sacred! 🌊",
                "trait": "logical_reasoning"
            },
        ],
        4: [
            {
                "question": "Who was the first Prime Minister of India?",
                "options": ["Sardar Patel", "B.R. Ambedkar", "Jawaharlal Nehru", "Mahatma Gandhi"],
                "correct": "Jawaharlal Nehru",
                "explanation": "Jawaharlal Nehru was India's first PM in 1947. Children called him Chacha Nehru! 🌹",
                "trait": "logical_reasoning"
            },
            {
                "question": "What does CPU stand for in computers?",
                "options": [
                    "Central Processing Unit",
                    "Computer Personal Unit",
                    "Central Program Unit",
                    "Core Processing Unit"
                ],
                "correct": "Central Processing Unit",
                "explanation": "CPU is the brain of the computer — it processes all instructions! 💻",
                "trait": "logical_reasoning"
            },
            {
                "question": "In which year did India gain independence?",
                "options": ["1945", "1947", "1950", "1952"],
                "correct": "1947",
                "explanation": "India became independent on 15th August 1947! We celebrate it every year! 🇮🇳",
                "trait": "logical_reasoning"
            },
        ],
        5: [
            {
                "question": "Which Indian mathematician is famous for discovering zero?",
                "options": ["Aryabhatta", "Brahmagupta", "Ramanujan", "Bhaskaracharya"],
                "correct": "Aryabhatta",
                "explanation": "Aryabhatta was the ancient Indian mathematician who introduced zero and the decimal system! 🔢",
                "trait": "logical_reasoning"
            },
            {
                "question": "What is the approximate distance of Earth from the Sun?",
                "options": ["15 million km", "150 million km", "1500 million km", "1.5 million km"],
                "correct": "150 million km",
                "explanation": "Earth is about 150 million km from the Sun — this distance is called 1 Astronomical Unit (AU)! 🌍",
                "trait": "logical_reasoning"
            },
            {
                "question": "Which Article of the Indian Constitution abolishes untouchability?",
                "options": ["Article 14", "Article 17", "Article 21", "Article 32"],
                "correct": "Article 17",
                "explanation": "Article 17 abolishes untouchability in all forms — a fundamental right for every Indian citizen! ⚖️",
                "trait": "logical_reasoning"
            },
        ],
    },

    # ══════════════════════════════════════════════════════
    # IQ / EQ FALLBACKS (grade-neutral, used for profile games)
    # ══════════════════════════════════════════════════════
    "iq": [
        {
            "question": "Look at the pattern: 2, 4, 6, 8, ___. What comes next?",
            "options": ["9", "10", "11", "12"],
            "correct": "10",
            "explanation": "We add 2 each time! 8 + 2 = 10. This is called an even number pattern! 🔢",
            "trait": "pattern_recognition"
        },
        {
            "question": "Which shape has no corners?",
            "options": ["Square", "Triangle", "Circle", "Rectangle"],
            "correct": "Circle",
            "explanation": "A circle has no corners and no edges — it's perfectly round! ⭕",
            "trait": "pattern_recognition"
        },
        {
            "question": "If all Roses are Flowers, and some Flowers are Red, are some Roses Red?",
            "options": ["Yes always", "Maybe", "No never", "Cannot say"],
            "correct": "Maybe",
            "explanation": "We can't be sure — some roses MIGHT be red but we don't know for certain! 🌹",
            "trait": "logical_reasoning"
        },
    ],

    "eq": [
        {
            "question": "Your friend is crying because they lost their favourite pencil. What do you do?",
            "options": ["Laugh at them", "Ignore them", "Ask if you can help find it", "Take their other pencil"],
            "correct": "Ask if you can help find it",
            "explanation": "Helping a sad friend shows kindness and empathy — that makes you a great friend! 💙",
            "trait": "empathy"
        },
        {
            "question": "You finished your work early. Your classmate is still struggling. What do you do?",
            "options": ["Show off your work", "Quietly offer to help", "Do nothing", "Tell the teacher they're slow"],
            "correct": "Quietly offer to help",
            "explanation": "Offering help shows empathy and social awareness — two very important life skills! 🌟",
            "trait": "social_skills"
        },
        {
            "question": "You made a mistake in class and everyone noticed. How do you feel and what do you do?",
            "options": [
                "Feel embarrassed and cry",
                "Pretend it didn't happen",
                "Acknowledge it, laugh it off and learn from it",
                "Blame someone else"
            ],
            "correct": "Acknowledge it, laugh it off and learn from it",
            "explanation": "Being able to handle mistakes calmly shows great self-awareness and emotional strength! 💪",
            "trait": "self_awareness"
        },
    ],
}


# ── Smart fallback selector ───────────────────────────────────────────────────
def get_random_fallback(subject: str = "General Knowledge", challenge_type: str = "iq", grade: int = 3) -> dict:
    """
    Get a grade and subject appropriate fallback challenge.

    Args:
        subject        : student's selected subject
        challenge_type : 'iq' or 'eq' (for profile games)
        grade          : student's grade (1-5)

    Returns:
        A single challenge dict with question, options, correct, explanation, trait
    """
    # For IQ/EQ profile games — use the flat lists
    if challenge_type in ("iq", "eq"):
        pool = FALLBACK_CHALLENGES.get(challenge_type, FALLBACK_CHALLENGES["iq"])
        return random.choice(pool)

    # For subject-based challenges — use grade-specific questions
    subject_pool = FALLBACK_CHALLENGES.get(subject)

    if not subject_pool:
        # Unknown subject — fallback to IQ
        return random.choice(FALLBACK_CHALLENGES["iq"])

    # Get grade-specific questions
    grade_pool = subject_pool.get(grade)

    if not grade_pool:
        # Grade not found — use nearest available grade
        available_grades = sorted(subject_pool.keys())
        nearest_grade    = min(available_grades, key=lambda g: abs(g - grade))
        grade_pool       = subject_pool[nearest_grade]

    return random.choice(grade_pool)