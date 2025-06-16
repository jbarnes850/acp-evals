"""
Core task dataset for ACP evaluation benchmarks.

Production-realistic multi-step tasks that test real agent capabilities
using LLM-based semantic evaluation instead of keyword matching.
"""

# Core evaluation tasks spanning different categories with semantic evaluation
CORE_TASKS = [
    # Multi-step Information Synthesis (5 tasks)
    {
        "id": "info_synthesis_climate",
        "category": "information_synthesis",
        "prompt": "Research the latest climate change mitigation technologies developed in 2024-2025. Identify the top 3 most promising approaches, compare their effectiveness, and provide implementation timelines. Include specific companies or research institutions leading each approach.",
        "expected_evaluation": {
            "type": "semantic_llm",
            "criteria": {
                "identifies_recent_technologies": {"weight": 0.3, "description": "Lists current climate tech from 2024-2025"},
                "compares_effectiveness": {"weight": 0.25, "description": "Provides quantitative or qualitative comparison"},
                "includes_implementation_details": {"weight": 0.25, "description": "Realistic timelines and implementation steps"},
                "cites_specific_entities": {"weight": 0.2, "description": "Names companies, institutions, or research groups"}
            },
            "pass_threshold": 0.7
        },
        "expected_tools": ["web_search", "document_parser", "synthesizer"],
        "expected_steps": [
            {"action": "search", "target": "recent climate technologies"},
            {"action": "filter", "target": "2024-2025 developments"},
            {"action": "analyze", "target": "effectiveness comparison"},
            {"action": "synthesize", "target": "comprehensive report"}
        ],
        "difficulty": "hard",
        "production_context": "Climate research agent for policy makers"
    },
    {
        "id": "code_debug_production",
        "category": "code_debugging",
        "prompt": "Debug this Python microservice that's causing 500 errors in production:\n\n```python\ndef process_payment(amount, user_id, payment_method):\n    if amount <= 0:\n        return {'error': 'Invalid amount'}\n    \n    user = get_user(user_id)\n    if user['balance'] < amount:\n        return {'error': 'Insufficient funds'}\n    \n    result = charge_payment(payment_method, amount)\n    if result['success']:\n        user['balance'] -= amount\n        update_user(user)\n        log_transaction(user_id, amount, 'success')\n    return result\n```\n\nThe service handles 1000+ requests/minute. Recent error logs show race conditions and data inconsistency issues.",
        "expected_evaluation": {
            "type": "semantic_llm",
            "criteria": {
                "identifies_race_condition": {"weight": 0.4, "description": "Recognizes concurrent access issues with balance updates"},
                "proposes_locking_mechanism": {"weight": 0.3, "description": "Suggests database locks, transactions, or atomic operations"},
                "addresses_error_handling": {"weight": 0.2, "description": "Improves exception handling and rollback mechanisms"},
                "considers_scalability": {"weight": 0.1, "description": "Mentions performance impact of solutions"}
            },
            "pass_threshold": 0.75
        },
        "expected_tools": ["code_analyzer", "database_profiler", "transaction_manager"],
        "expected_steps": [
            {"action": "analyze", "target": "identify concurrency issues"},
            {"action": "design", "target": "atomic transaction pattern"},
            {"action": "implement", "target": "database locking"},
            {"action": "test", "target": "concurrent request simulation"}
        ],
        "difficulty": "expert",
        "production_context": "High-traffic payment processing service"
    },
    {
        "id": "data_pipeline_analysis",
        "category": "data_engineering",
        "prompt": "Our data pipeline processes 50GB of user behavior data daily. Recent reports show missing data for 2-3 hour windows, and downstream ML models are showing degraded performance. The pipeline: S3 → Spark → Feature Store → ML Training. Debug and propose a solution that includes monitoring and alerting.",
        "expected_evaluation": {
            "type": "semantic_llm",
            "criteria": {
                "identifies_failure_points": {"weight": 0.3, "description": "Pinpoints likely causes: network issues, Spark failures, resource constraints"},
                "proposes_monitoring_solution": {"weight": 0.25, "description": "Suggests specific metrics, alerts, and SLAs"},
                "addresses_data_recovery": {"weight": 0.25, "description": "Backfill strategy and data validation"},
                "includes_preventive_measures": {"weight": 0.2, "description": "Circuit breakers, retries, graceful degradation"}
            },
            "pass_threshold": 0.7
        },
        "expected_tools": ["spark_profiler", "s3_analyzer", "monitoring_dashboard", "alerting_system"],
        "expected_steps": [
            {"action": "investigate", "target": "missing data time windows"},
            {"action": "profile", "target": "Spark job performance"},
            {"action": "design", "target": "monitoring and alerting"},
            {"action": "implement", "target": "recovery mechanisms"}
        ],
        "difficulty": "hard",
        "production_context": "ML data pipeline for recommendation system"
    },
    {
        "id": "security_incident_response",
        "category": "security_operations",
        "prompt": "SECURITY ALERT: Unusual API access patterns detected. 10,000+ failed authentication attempts from 200+ IP addresses in the last hour, targeting /api/admin endpoints. Some attempts succeeded with valid user credentials. Current system: JWT tokens, rate limiting (100 req/min), basic IP blocking. Investigate and respond immediately.",
        "expected_evaluation": {
            "type": "semantic_llm",
            "criteria": {
                "recognizes_credential_stuffing": {"weight": 0.3, "description": "Identifies distributed credential stuffing attack"},
                "immediate_response_steps": {"weight": 0.25, "description": "Block suspicious IPs, force password resets, revoke tokens"},
                "investigation_methodology": {"weight": 0.25, "description": "Log analysis, user notification, breach assessment"},
                "long_term_hardening": {"weight": 0.2, "description": "MFA, advanced rate limiting, anomaly detection"}
            },
            "pass_threshold": 0.8
        },
        "expected_tools": ["security_dashboard", "ip_blocker", "token_manager", "log_analyzer"],
        "expected_steps": [
            {"action": "contain", "target": "block malicious IPs immediately"},
            {"action": "investigate", "target": "analyze attack patterns"},
            {"action": "remediate", "target": "force credential resets"},
            {"action": "harden", "target": "implement additional controls"}
        ],
        "difficulty": "expert",
        "production_context": "SOC analyst responding to live security incident"
    },
    {
        "id": "customer_escalation_complex",
        "category": "customer_operations",
        "prompt": "URGENT: Enterprise customer (500+ seats, $2M/year contract) reporting that their integration broke after our API update yesterday. Their CEO is involved. Issues: 1) Authentication tokens failing intermittently, 2) Webhook delivery delays (2+ hours), 3) Data sync showing 'corrupted data' errors. They're threatening to switch providers. Last 3 support tickets were 'resolved' but issues persist. Handle this escalation.",
        "expected_evaluation": {
            "type": "semantic_llm",
            "criteria": {
                "acknowledges_urgency": {"weight": 0.2, "description": "Recognizes enterprise impact and CEO involvement"},
                "technical_diagnosis": {"weight": 0.3, "description": "Systematically addresses each technical issue"},
                "escalation_management": {"weight": 0.25, "description": "Involves engineering, provides executive updates"},
                "retention_strategy": {"weight": 0.25, "description": "Compensation, prevention plan, relationship repair"}
            },
            "pass_threshold": 0.75
        },
        "expected_tools": ["api_monitor", "webhook_debugger", "customer_database", "escalation_system"],
        "expected_steps": [
            {"action": "acknowledge", "target": "immediate response to customer"},
            {"action": "diagnose", "target": "technical root cause analysis"},
            {"action": "coordinate", "target": "cross-team incident response"},
            {"action": "resolve", "target": "fix and relationship management"}
        ],
        "difficulty": "hard",
        "production_context": "Customer success managing enterprise crisis"
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
