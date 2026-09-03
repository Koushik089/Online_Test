import os
import json
import random
import requests
from django.conf import settings

# A pool of high-quality local questions to fall back to when the API key is not present or offline.
LOCAL_QUESTION_POOL = [
    # --- Computer Networks ---
    {
        "subject": "computer_network",
        "difficulty": "easy",
        "question_text": "What is the primary function of the Domain Name System (DNS)?",
        "option_a": "To secure internet connection using encryption",
        "option_b": "To translate human-readable domain names into IP addresses",
        "option_c": "To route packets between different subnets",
        "option_d": "To manage session establishment between processes",
        "correct_answer": "b",
        "explanation": "DNS translates domain names like example.com into IP addresses like 192.0.2.1 so browsers can load internet resources.",
        "tags": "dns,protocols,basics"
    },
    {
        "subject": "computer_network",
        "difficulty": "medium",
        "question_text": "Which of the following transport layer protocols is connection-oriented and guarantees ordered delivery?",
        "option_a": "UDP",
        "option_b": "TCP",
        "option_c": "IP",
        "option_d": "ICMP",
        "correct_answer": "b",
        "explanation": "TCP (Transmission Control Protocol) is a connection-oriented protocol that guarantees delivery and order, unlike UDP which is connectionless.",
        "tags": "tcp,transport-layer,protocols"
    },
    {
        "subject": "computer_network",
        "difficulty": "hard",
        "question_text": "During a TCP handshake, Host A sends a SYN packet with Seq = 1000. Host B replies with a SYN-ACK. What will be the Acknowledgment Number (Ack) in Host B's reply?",
        "option_a": "1000",
        "option_b": "1001",
        "option_c": "1002",
        "option_d": "999",
        "correct_answer": "b",
        "explanation": "The acknowledgment number in TCP SYN-ACK is the sequence number of the received SYN packet incremented by 1 (1000 + 1 = 1001).",
        "tags": "tcp,handshake,sequence-numbers"
    },
    {
        "subject": "computer_network",
        "difficulty": "medium",
        "question_text": "What is the CIDR subnet mask for a /26 network suffix?",
        "option_a": "255.255.255.0",
        "option_b": "255.255.255.192",
        "option_c": "255.255.255.128",
        "option_d": "255.255.255.240",
        "correct_answer": "b",
        "explanation": "A /26 network uses 26 bits for the network portion. In binary, the last octet is 11000000, which translates to 192 in decimal.",
        "tags": "cidr,ip-addressing,subnetting"
    },

    # --- DBMS ---
    {
        "subject": "dbms",
        "difficulty": "easy",
        "question_text": "Which SQL constraint uniquely identifies each record in a database table?",
        "option_a": "FOREIGN KEY",
        "option_b": "PRIMARY KEY",
        "option_c": "UNIQUE",
        "option_d": "CHECK",
        "correct_answer": "b",
        "explanation": "A PRIMARY KEY constraint uniquely identifies each record in a table. Primary keys must contain UNIQUE values and cannot contain NULL values.",
        "tags": "sql,constraints,keys"
    },
    {
        "subject": "dbms",
        "difficulty": "medium",
        "question_text": "What normal form is a table in if it contains no multi-valued attributes and every non-key attribute is fully functionally dependent on the primary key?",
        "option_a": "First Normal Form (1NF)",
        "option_b": "Second Normal Form (2NF)",
        "option_c": "Third Normal Form (3NF)",
        "option_d": "Boyce-Codd Normal Form (BCNF)",
        "correct_answer": "b",
        "explanation": "Second Normal Form (2NF) requires the table to be in 1NF and have no partial dependencies, meaning every non-prime attribute is fully functionally dependent on the entire primary key.",
        "tags": "normalization,normal-forms,schema-design"
    },
    {
        "subject": "dbms",
        "difficulty": "hard",
        "question_text": "In a database transaction, which property ensures that the database remains in a consistent state after a successful commit or complete rollback?",
        "option_a": "Atomicity",
        "option_b": "Consistency",
        "option_c": "Isolation",
        "option_d": "Durability",
        "correct_answer": "b",
        "explanation": "Consistency ensures that a transaction takes the database from one valid state to another, maintaining all schema constraints and rules.",
        "tags": "acid,transactions,concurrency"
    },
    {
        "subject": "dbms",
        "difficulty": "medium",
        "question_text": "Which join type returns all records when there is a match in either left or right table records?",
        "option_a": "INNER JOIN",
        "option_b": "LEFT JOIN",
        "option_c": "RIGHT JOIN",
        "option_d": "FULL OUTER JOIN",
        "correct_answer": "d",
        "explanation": "A FULL OUTER JOIN returns all matching rows from both tables, plus any non-matching rows from either side.",
        "tags": "sql,joins,queries"
    },

    # --- Operating Systems ---
    {
        "subject": "operating_system",
        "difficulty": "easy",
        "question_text": "What is the term for a state where two or more processes are blocked, each waiting for a resource held by the other?",
        "option_a": "Starvation",
        "option_b": "Deadlock",
        "option_c": "Race Condition",
        "option_d": "Context Switch",
        "correct_answer": "b",
        "explanation": "A deadlock is a situation in which two or more competing actions are each waiting for the other to finish, and thus neither ever does.",
        "tags": "deadlock,concurrency,processes"
    },
    {
        "subject": "operating_system",
        "difficulty": "medium",
        "question_text": "Which page replacement algorithm replaces the page that has not been used for the longest period of time?",
        "option_a": "First-In, First-Out (FIFO)",
        "option_b": "Least Recently Used (LRU)",
        "option_c": "Optimal Page Replacement",
        "option_d": "Least Frequently Used (LFU)",
        "correct_answer": "b",
        "explanation": "LRU (Least Recently Used) keeps track of page usage and replaces the page that has gone unused for the longest duration.",
        "tags": "memory-management,page-replacement,paging"
    },
    {
        "subject": "operating_system",
        "difficulty": "hard",
        "question_text": "Under the Banker's Algorithm for deadlock avoidance, what is a state called if the system can allocate resources to all processes without entering a deadlock?",
        "option_a": "Stable State",
        "option_b": "Safe State",
        "option_c": "Secure State",
        "option_d": "Optimal State",
        "correct_answer": "b",
        "explanation": "A safe state exists if there is a sequence of allocations that allows all processes to finish execution without entering a deadlock.",
        "tags": "bankers-algorithm,deadlock-avoidance,resources"
    },
    {
        "subject": "operating_system",
        "difficulty": "medium",
        "question_text": "What is the primary purpose of a Translation Lookaside Buffer (TLB) in virtual memory?",
        "option_a": "To hold pages swapped out to the disk",
        "option_b": "To cache page table page translations for faster physical memory access",
        "option_c": "To schedule processes in the CPU queue",
        "option_d": "To synchronize thread communications",
        "correct_answer": "b",
        "explanation": "A TLB is a hardware cache that memory management units use to improve virtual-to-physical address translation speeds.",
        "tags": "tlb,virtual-memory,caching"
    }
]

def generate_questions(subject, difficulty, topic_keywords, count=5):
    """
    Generate questions using the Gemini API if GEMINI_API_KEY is defined in environment
    variables or Django settings. Otherwise, fallback to the local high-quality mock generator.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", None)
    
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            
            prompt = f"""
            Generate exactly {count} multiple-choice questions for the subject '{subject}' on the topic/keywords '{topic_keywords}' with difficulty '{difficulty}'.
            Return ONLY a valid JSON array of objects, with no markdown formatting, no code block tick marks, and no extra text.
            Each object must strictly have these fields:
            - "question_text": The text of the question.
            - "option_a": Option A text.
            - "option_b": Option B text.
            - "option_c": Option C text.
            - "option_d": Option D text.
            - "correct_answer": Correct answer choice, which must be exactly one of "a", "b", "c", "d" (lowercase).
            - "difficulty": The difficulty, which must be exactly "{difficulty}".
            - "explanation": A detailed explanation of why the correct answer is correct.
            - "tags": A comma-separated list of tags/keywords.
            
            Example output format:
            [
              {{
                "question_text": "What is 2+2?",
                "option_a": "3",
                "option_b": "4",
                "option_c": "5",
                "option_d": "6",
                "correct_answer": "b",
                "difficulty": "{difficulty}",
                "explanation": "Because 2 + 2 = 4.",
                "tags": "math,addition"
              }}
            ]
            """
            
            body = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            }
            
            response = requests.post(url, headers=headers, json=body, timeout=8)
            if response.status_code == 200:
                result_json = response.json()
                text_content = result_json['candidates'][0]['content']['parts'][0]['text']
                questions = json.loads(text_content.strip())
                if isinstance(questions, list) and len(questions) > 0:
                    # Clean up keys and values to match exactly what is required
                    cleaned_questions = []
                    for q in questions:
                        cleaned_questions.append({
                            "subject": subject,
                            "difficulty": q.get("difficulty", difficulty),
                            "question_text": q.get("question_text", "AI Generated Question"),
                            "option_a": q.get("option_a", "Option A"),
                            "option_b": q.get("option_b", "Option B"),
                            "option_c": q.get("option_c", "Option C"),
                            "option_d": q.get("option_d", "Option D"),
                            "correct_answer": q.get("correct_answer", "a").lower(),
                            "explanation": q.get("explanation", ""),
                            "tags": q.get("tags", topic_keywords),
                            "marks": 1
                        })
                    return cleaned_questions
        except Exception as e:
            # Fallback to local on error
            print(f"Gemini API generation failed: {e}. Falling back to local question pool.")
            
    # --- Local Fallback Generator ---
    matched = []
    
    # Filter by subject
    subject_filtered = [q for q in LOCAL_QUESTION_POOL if q["subject"] == subject]
    if not subject_filtered:
        subject_filtered = LOCAL_QUESTION_POOL
        
    # Filter by difficulty
    diff_filtered = [q for q in subject_filtered if q["difficulty"] == difficulty]
    if not diff_filtered:
        diff_filtered = subject_filtered
        
    # Filter by topic keywords
    if topic_keywords:
        keywords = [k.strip().lower() for k in topic_keywords.split(',') if k.strip()]
        for q in diff_filtered:
            q_text = q["question_text"].lower()
            q_tags = q["tags"].lower()
            if any(k in q_text or k in q_tags for k in keywords):
                matched.append(q)
                
    if not matched:
        matched = diff_filtered
        
    # Shuffle and select count
    random.shuffle(matched)
    selected = matched[:count]
    
    # If we still need more questions, fill with random ones from the pool
    while len(selected) < count:
        extra = random.choice(LOCAL_QUESTION_POOL)
        # Create a variant to avoid direct duplicate
        selected.append({
            "subject": subject,
            "difficulty": difficulty,
            "question_text": f"[AI Practice Variant] {extra['question_text']}",
            "option_a": extra["option_a"],
            "option_b": extra["option_b"],
            "option_c": extra["option_c"],
            "option_d": extra["option_d"],
            "correct_answer": extra["correct_answer"],
            "explanation": extra["explanation"],
            "tags": f"ai-variant,{extra['tags']}"
        })
        
    # Map questions count to return objects
    results = []
    for q in selected:
        results.append({
            "subject": subject,
            "difficulty": difficulty,
            "question_text": q["question_text"],
            "option_a": q["option_a"],
            "option_b": q["option_b"],
            "option_c": q["option_c"],
            "option_d": q["option_d"],
            "correct_answer": q["correct_answer"],
            "explanation": q.get("explanation", ""),
            "tags": q.get("tags", topic_keywords),
            "marks": 1
        })
    return results
