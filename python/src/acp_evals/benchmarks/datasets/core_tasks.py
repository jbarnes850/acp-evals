"""
Core task dataset for ACP evaluation benchmarks.

20-30 carefully selected tasks across multiple categories that reveal
agent capabilities and limitations.
"""

# Core evaluation tasks spanning different categories
CORE_TASKS = [
    # Information Retrieval (5 tasks)
    {
        "id": "ir_return_policy",
        "category": "information_retrieval",
        "prompt": "What is the return policy for electronics at most retail stores?",
        "expected": ["30 days", "receipt", "original packaging"],
        "difficulty": "easy",
    },
    {
        "id": "ir_capital_facts",
        "category": "information_retrieval",
        "prompt": "What is the capital of France and when was it established as the capital?",
        "expected": ["Paris", "987", "Capet"],
        "difficulty": "medium",
    },
    {
        "id": "ir_tech_definition",
        "category": "information_retrieval",
        "prompt": "What is machine learning in simple terms?",
        "expected": ["learn", "data", "patterns", "without explicit programming"],
        "difficulty": "easy",
    },
    {
        "id": "ir_historical_event",
        "category": "information_retrieval",
        "prompt": "What year did World War II end and which countries signed the surrender?",
        "expected": ["1945", "Japan", "Germany"],
        "difficulty": "medium",
    },
    {
        "id": "ir_scientific_fact",
        "category": "information_retrieval",
        "prompt": "What is the speed of light in a vacuum?",
        "expected": ["299,792,458", "meters per second", "3×10^8"],
        "difficulty": "easy",
    },

    # Coding Tasks (5 tasks)
    {
        "id": "code_string_reverse",
        "category": "coding",
        "prompt": "Write a Python function to reverse a string without using slicing.",
        "expected": ["def", "reverse", "for", "return"],
        "difficulty": "easy",
    },
    {
        "id": "code_fibonacci",
        "category": "coding",
        "prompt": "Write a function to calculate the nth Fibonacci number.",
        "expected": ["def", "fibonacci", "if n <= 1", "return"],
        "difficulty": "medium",
    },
    {
        "id": "code_list_sum",
        "category": "coding",
        "prompt": "Write a function that returns the sum of all numbers in a list.",
        "expected": ["def", "sum", "for", "return"],
        "difficulty": "easy",
    },
    {
        "id": "code_palindrome",
        "category": "coding",
        "prompt": "Write a function to check if a string is a palindrome.",
        "expected": ["def", "palindrome", "==", "return"],
        "difficulty": "medium",
    },
    {
        "id": "code_sort_dict",
        "category": "coding",
        "prompt": "Write code to sort a dictionary by its values in descending order.",
        "expected": ["sorted", "key=", "reverse=True"],
        "difficulty": "medium",
    },

    # Reasoning Tasks (5 tasks)
    {
        "id": "reason_logic_flowers",
        "category": "reasoning",
        "prompt": "If all roses are flowers and some flowers fade quickly, can we conclude that all roses fade quickly?",
        "expected": ["no", "some", "not all"],
        "difficulty": "medium",
    },
    {
        "id": "reason_math_pattern",
        "category": "reasoning",
        "prompt": "What is the next number in the sequence: 2, 4, 8, 16, ?",
        "expected": ["32", "multiply", "double"],
        "difficulty": "easy",
    },
    {
        "id": "reason_word_problem",
        "category": "reasoning",
        "prompt": "If a train travels 60 miles in 1.5 hours, what is its average speed?",
        "expected": ["40", "miles per hour", "mph"],
        "difficulty": "easy",
    },
    {
        "id": "reason_logical_puzzle",
        "category": "reasoning",
        "prompt": "Three friends - Alice, Bob, and Charlie - are different ages. Alice is older than Bob. Charlie is younger than Bob. Who is the oldest?",
        "expected": ["Alice"],
        "difficulty": "easy",
    },
    {
        "id": "reason_probability",
        "category": "reasoning",
        "prompt": "If you flip a fair coin 3 times, what is the probability of getting at least one heads?",
        "expected": ["7/8", "0.875", "87.5%"],
        "difficulty": "hard",
    },

    # General Assistance (5 tasks)
    {
        "id": "assist_trip_planning",
        "category": "assistance",
        "prompt": "Help me plan a 3-day trip to Paris. What are the must-see attractions?",
        "expected": ["Eiffel Tower", "Louvre", "Notre-Dame", "Arc de Triomphe"],
        "difficulty": "medium",
    },
    {
        "id": "assist_recipe",
        "category": "assistance",
        "prompt": "Give me a simple recipe for chocolate chip cookies.",
        "expected": ["flour", "butter", "sugar", "chocolate chips", "bake"],
        "difficulty": "easy",
    },
    {
        "id": "assist_email_draft",
        "category": "assistance",
        "prompt": "Help me write a professional email to decline a job offer politely.",
        "expected": ["thank you", "appreciate", "opportunity", "decision"],
        "difficulty": "medium",
    },
    {
        "id": "assist_debug_help",
        "category": "assistance",
        "prompt": "My Python code gives a 'list index out of range' error. What are common causes?",
        "expected": ["accessing", "index", "doesn't exist", "length", "bounds"],
        "difficulty": "medium",
    },
    {
        "id": "assist_meeting_agenda",
        "category": "assistance",
        "prompt": "Create an agenda for a 1-hour project kickoff meeting.",
        "expected": ["introductions", "objectives", "timeline", "questions"],
        "difficulty": "medium",
    },

    # Abstract/Creative Tasks (5 tasks)
    {
        "id": "creative_story_start",
        "category": "creative",
        "prompt": "Write the opening sentence of a mystery novel set in a library.",
        "expected": {
            "required": ["library"],
            "optional": ["mystery", "book", "quiet", "dust"],
        },
        "difficulty": "medium",
    },
    {
        "id": "creative_analogy",
        "category": "creative",
        "prompt": "Create an analogy: Learning to code is like...",
        "expected": {
            "required": ["like"],
            "optional": ["learn", "practice", "language", "build"],
        },
        "difficulty": "medium",
    },
    {
        "id": "creative_product_name",
        "category": "creative",
        "prompt": "Suggest a catchy name for a new eco-friendly water bottle brand.",
        "expected": {
            "required": [],  # Any creative name is acceptable
            "optional": ["eco", "green", "pure", "flow", "hydro"],
        },
        "difficulty": "hard",
    },
    {
        "id": "creative_slogan",
        "category": "creative",
        "prompt": "Create a slogan for a 24-hour gym.",
        "expected": {
            "required": [],
            "optional": ["24", "always", "never", "anytime", "open"],
        },
        "difficulty": "medium",
    },
    {
        "id": "creative_haiku",
        "category": "creative",
        "prompt": "Write a haiku about artificial intelligence.",
        "expected": {
            "required": [],  # Check structure instead
            "optional": ["AI", "artificial", "intelligence", "machine", "learn"],
        },
        "difficulty": "hard",
    },
]

# Distractor contexts for context scaling tests
DISTRACTOR_CONTEXTS = [
    # Restaurant/Food contexts
    """Restaurant Menu: Our special today is grilled salmon with asparagus, served with a
    lemon butter sauce. We also have a vegetarian pasta option with fresh tomatoes and basil.
    Desserts include chocolate lava cake and seasonal fruit tart. Happy hour is from 4-6 PM
    with half-price appetizers.""",

    # Car maintenance contexts
    """Car Maintenance Guide: Change your oil every 5,000 miles or 6 months, whichever comes
    first. Check tire pressure monthly and rotate tires every 6,000-8,000 miles. Replace air
    filters every 12,000 miles. Brake pads typically last 25,000-70,000 miles depending on
    driving conditions.""",

    # Recipe contexts
    """Cookie Recipe: To make chocolate chip cookies, cream together 1 cup butter with 3/4 cup
    sugar. Add 2 eggs and 1 tsp vanilla. Mix in 2.25 cups flour, 1 tsp baking soda, and 1 tsp
    salt. Fold in 2 cups chocolate chips. Bake at 375°F for 9-11 minutes until golden brown.""",

    # Weather contexts
    """Weather Report: Today's forecast shows partly cloudy skies with a high of 72°F and a low
    of 58°F. There's a 20% chance of afternoon showers. Winds will be from the northwest at
    10-15 mph. UV index is moderate, so sunscreen is recommended for extended outdoor activities.""",

    # Sports contexts
    """Sports Update: In last night's game, the home team defeated the visitors 4-2. The star
    player scored two goals in the second period. The team now leads the division with 45 points
    and has won 8 of their last 10 games. Next game is Thursday at 7 PM.""",

    # Travel contexts
    """Travel Tips: When packing for international travel, remember to check passport expiration
    dates at least 6 months before departure. Pack essentials in carry-on luggage. Arrive at the
    airport 3 hours early for international flights. Don't forget travel adapters for electronics.""",

    # Gardening contexts
    """Gardening Guide: Plant tomatoes after the last frost when soil temperature reaches 60°F.
    Space plants 24-36 inches apart. Water deeply once or twice per week. Add mulch to retain
    moisture and prevent weeds. Harvest when tomatoes are fully colored but still firm.""",

    # Technology news contexts
    """Tech News: The latest smartphone features a 6.7-inch display with 120Hz refresh rate.
    It includes a triple camera system with 108MP main sensor. Battery life is rated at 5000mAh
    with fast charging support. Available in three colors starting at $899.""",

    # Historical facts contexts
    """Historical Fact: The Great Wall of China was built over many centuries, with the first
    sections constructed around 7th century BC. The wall stretches approximately 13,000 miles
    including all branches. It was built to protect against invasions and to control trade routes.""",

    # Science contexts
    """Science Fact: Water molecules consist of two hydrogen atoms and one oxygen atom (H2O).
    Water freezes at 0°C (32°F) and boils at 100°C (212°F) at sea level. It's the only natural
    substance found in all three states - solid, liquid, and gas - at Earth's surface temperatures.""",

    # Fashion contexts
    """Fashion Trends: This season's colors include sage green, dusty pink, and navy blue.
    Oversized blazers and wide-leg pants are making a comeback. Sustainable fashion continues
    to grow with more brands using recycled materials. Layering remains key for transitional weather.""",

    # Health tips contexts
    """Health Tips: Adults should aim for 7-9 hours of sleep per night. Regular exercise of at
    least 150 minutes per week is recommended. Stay hydrated by drinking 8 glasses of water daily.
    Include a variety of fruits and vegetables in your diet for optimal nutrition.""",

    # Movie reviews contexts
    """Movie Review: The latest action film features stunning visual effects and a compelling
    storyline. The lead actor delivers a powerful performance, though the pacing slows in the
    middle act. Runtime is 2 hours 15 minutes. Critics rate it 7.5/10. Now showing in theaters.""",

    # Music contexts
    """Music News: The band's new album debuts at number one on the charts. It features 12 tracks
    including collaborations with several guest artists. The lead single has already gone platinum.
    A world tour is planned starting next spring with 50 dates across 20 countries.""",

    # Pet care contexts
    """Pet Care: Dogs should be walked at least twice daily for exercise and bathroom needs.
    Feed adult dogs twice per day with high-quality dog food. Regular vet checkups are important
    for preventive care. Grooming needs vary by breed but most dogs benefit from monthly baths.""",
]
