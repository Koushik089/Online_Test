from django.core.management.base import BaseCommand
from tokio.models import Question


QUESTIONS = [
    # ── DBMS (10) ──────────────────────────────────────────────────────────────
    {
        "subject": "dbms",
        "question_text": "Which of the following is NOT a type of SQL JOIN?",
        "option_a": "INNER JOIN", "option_b": "OUTER JOIN",
        "option_c": "CROSS JOIN", "option_d": "CIRCULAR JOIN",
        "correct_answer": "d", "difficulty": "easy",
        "explanation": "CIRCULAR JOIN does not exist in SQL.",
        "tags": "sql,join", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "ACID stands for:",
        "option_a": "Atomicity, Consistency, Isolation, Durability",
        "option_b": "Atomicity, Concurrency, Integrity, Durability",
        "option_c": "Access, Consistency, Isolation, Data",
        "option_d": "Atomicity, Consistency, Integration, Data",
        "correct_answer": "a", "difficulty": "easy",
        "explanation": "ACID = Atomicity, Consistency, Isolation, Durability.",
        "tags": "transactions,acid", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "Which normal form eliminates partial dependencies?",
        "option_a": "1NF", "option_b": "2NF", "option_c": "3NF", "option_d": "BCNF",
        "correct_answer": "b", "difficulty": "medium",
        "explanation": "2NF removes partial dependencies on a composite primary key.",
        "tags": "normalization", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "A foreign key in a relational table refers to:",
        "option_a": "Primary key of the same table",
        "option_b": "Primary key of another table",
        "option_c": "Any unique column",
        "option_d": "An indexed column",
        "correct_answer": "b", "difficulty": "easy",
        "explanation": "A foreign key references the primary key of another (or the same) table.",
        "tags": "keys,relational", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "Which SQL command is used to remove all rows from a table without logging individual row deletions?",
        "option_a": "DELETE", "option_b": "DROP", "option_c": "TRUNCATE", "option_d": "REMOVE",
        "correct_answer": "c", "difficulty": "medium",
        "explanation": "TRUNCATE removes all rows quickly without logging each deletion.",
        "tags": "sql,ddl", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "In an ER diagram, a diamond shape represents:",
        "option_a": "Entity", "option_b": "Attribute", "option_c": "Relationship", "option_d": "Key",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "Diamond shapes denote relationships between entities in ER diagrams.",
        "tags": "er-diagram", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "Which isolation level prevents dirty reads but allows non-repeatable reads?",
        "option_a": "READ UNCOMMITTED", "option_b": "READ COMMITTED",
        "option_c": "REPEATABLE READ", "option_d": "SERIALIZABLE",
        "correct_answer": "b", "difficulty": "hard",
        "explanation": "READ COMMITTED prevents dirty reads but non-repeatable reads can still occur.",
        "tags": "transactions,isolation", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "Which of the following is a DDL command?",
        "option_a": "SELECT", "option_b": "INSERT", "option_c": "ALTER", "option_d": "UPDATE",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "ALTER is a DDL command used to modify table structure.",
        "tags": "sql,ddl", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "A relation is in BCNF if for every non-trivial functional dependency X → Y:",
        "option_a": "Y is a superkey", "option_b": "X is a superkey",
        "option_c": "X is a primary key", "option_d": "Y is a foreign key",
        "correct_answer": "b", "difficulty": "hard",
        "explanation": "In BCNF, the left-hand side of every non-trivial FD must be a superkey.",
        "tags": "normalization,bcnf", "marks": 1,
    },
    {
        "subject": "dbms",
        "question_text": "Which command is used to grant privileges to a user in SQL?",
        "option_a": "ALLOW", "option_b": "PERMIT", "option_c": "GRANT", "option_d": "ASSIGN",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "GRANT is the SQL DCL command used to give privileges to users.",
        "tags": "sql,dcl", "marks": 1,
    },

    # ── COMPUTER NETWORK (10) ──────────────────────────────────────────────────
    {
        "subject": "computer_network",
        "question_text": "Which layer of the OSI model is responsible for routing?",
        "option_a": "Data Link", "option_b": "Transport", "option_c": "Network", "option_d": "Session",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "The Network layer (Layer 3) handles logical addressing and routing.",
        "tags": "osi,routing", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "What does DNS stand for?",
        "option_a": "Data Network Service", "option_b": "Domain Name System",
        "option_c": "Dynamic Node Server", "option_d": "Distributed Name Service",
        "correct_answer": "b", "difficulty": "easy",
        "explanation": "DNS = Domain Name System, translates domain names to IP addresses.",
        "tags": "dns,protocols", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "Which protocol is used to assign IP addresses automatically?",
        "option_a": "FTP", "option_b": "SMTP", "option_c": "DHCP", "option_d": "ARP",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "DHCP (Dynamic Host Configuration Protocol) automatically assigns IP addresses.",
        "tags": "dhcp,ip", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "The maximum number of hosts in a /24 subnet is:",
        "option_a": "254", "option_b": "256", "option_c": "255", "option_d": "512",
        "correct_answer": "a", "difficulty": "medium",
        "explanation": "A /24 subnet has 256 addresses; subtract network and broadcast = 254 usable hosts.",
        "tags": "subnetting,ip", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "TCP is different from UDP because TCP is:",
        "option_a": "Faster", "option_b": "Connection-oriented", "option_c": "Stateless", "option_d": "Unreliable",
        "correct_answer": "b", "difficulty": "easy",
        "explanation": "TCP is connection-oriented and guarantees delivery; UDP is connectionless.",
        "tags": "tcp,udp,transport", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "Which device operates at the Data Link layer?",
        "option_a": "Router", "option_b": "Hub", "option_c": "Switch", "option_d": "Repeater",
        "correct_answer": "c", "difficulty": "medium",
        "explanation": "Switches operate at Layer 2 (Data Link) using MAC addresses.",
        "tags": "osi,switch", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "HTTP uses which port by default?",
        "option_a": "21", "option_b": "25", "option_c": "80", "option_d": "443",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "HTTP uses port 80; HTTPS uses port 443.",
        "tags": "http,ports", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "Which protocol is used to send emails?",
        "option_a": "POP3", "option_b": "IMAP", "option_c": "SMTP", "option_d": "FTP",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "SMTP (Simple Mail Transfer Protocol) is used to send emails.",
        "tags": "smtp,email", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "What is the purpose of ARP?",
        "option_a": "Resolve IP to MAC address", "option_b": "Resolve MAC to IP address",
        "option_c": "Assign IP addresses", "option_d": "Encrypt network traffic",
        "correct_answer": "a", "difficulty": "medium",
        "explanation": "ARP (Address Resolution Protocol) maps an IP address to a MAC address.",
        "tags": "arp,ip,mac", "marks": 1,
    },
    {
        "subject": "computer_network",
        "question_text": "Which routing protocol uses the Bellman-Ford algorithm?",
        "option_a": "OSPF", "option_b": "BGP", "option_c": "RIP", "option_d": "EIGRP",
        "correct_answer": "c", "difficulty": "hard",
        "explanation": "RIP (Routing Information Protocol) uses the Bellman-Ford distance-vector algorithm.",
        "tags": "routing,rip", "marks": 1,
    },

    # ── OPERATING SYSTEM (10) ──────────────────────────────────────────────────
    {
        "subject": "operating_system",
        "question_text": "Which scheduling algorithm gives the shortest average waiting time?",
        "option_a": "FCFS", "option_b": "Round Robin", "option_c": "SJF", "option_d": "Priority",
        "correct_answer": "c", "difficulty": "medium",
        "explanation": "SJF (Shortest Job First) minimizes average waiting time among non-preemptive algorithms.",
        "tags": "scheduling,cpu", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "A deadlock can occur only if all four Coffman conditions hold. Which is NOT one of them?",
        "option_a": "Mutual Exclusion", "option_b": "Hold and Wait",
        "option_c": "Preemption", "option_d": "Circular Wait",
        "correct_answer": "c", "difficulty": "medium",
        "explanation": "The four conditions are Mutual Exclusion, Hold & Wait, No Preemption, and Circular Wait.",
        "tags": "deadlock", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "Virtual memory allows a process to use more memory than physically available by using:",
        "option_a": "Cache", "option_b": "Registers", "option_c": "Disk as extended RAM", "option_d": "ROM",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "Virtual memory uses disk space (swap) to extend the apparent size of RAM.",
        "tags": "virtual-memory,paging", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "Which page replacement algorithm suffers from Belady's anomaly?",
        "option_a": "LRU", "option_b": "Optimal", "option_c": "FIFO", "option_d": "LFU",
        "correct_answer": "c", "difficulty": "hard",
        "explanation": "FIFO can have more page faults with more frames — known as Belady's anomaly.",
        "tags": "paging,page-replacement", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "A process moves from the running state to the waiting state when:",
        "option_a": "It is preempted by the scheduler",
        "option_b": "It requests I/O or waits for an event",
        "option_c": "It finishes execution",
        "option_d": "A new process is created",
        "correct_answer": "b", "difficulty": "easy",
        "explanation": "A process enters the waiting state when it needs I/O or waits for a resource.",
        "tags": "process,states", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "Which of the following is an example of a non-preemptive scheduling algorithm?",
        "option_a": "Round Robin", "option_b": "SRTF", "option_c": "FCFS", "option_d": "Preemptive Priority",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "FCFS (First Come First Served) is non-preemptive; once a process runs it completes.",
        "tags": "scheduling,fcfs", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "Thrashing occurs when:",
        "option_a": "CPU utilization is very high",
        "option_b": "Processes spend more time paging than executing",
        "option_c": "Too many processes are in the ready queue",
        "option_d": "The OS runs out of disk space",
        "correct_answer": "b", "difficulty": "hard",
        "explanation": "Thrashing happens when excessive paging causes very low CPU utilization.",
        "tags": "virtual-memory,thrashing", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "A semaphore with an initial value of 1 is called a:",
        "option_a": "Counting semaphore", "option_b": "Binary semaphore",
        "option_c": "Mutex lock", "option_d": "Both B and C",
        "correct_answer": "d", "difficulty": "medium",
        "explanation": "A binary semaphore (value 0 or 1) behaves like a mutex lock.",
        "tags": "synchronization,semaphore", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "Which system call is used to create a new process in Unix/Linux?",
        "option_a": "exec()", "option_b": "spawn()", "option_c": "fork()", "option_d": "create()",
        "correct_answer": "c", "difficulty": "easy",
        "explanation": "fork() creates a child process that is a copy of the parent process.",
        "tags": "process,unix,syscall", "marks": 1,
    },
    {
        "subject": "operating_system",
        "question_text": "Internal fragmentation occurs in which memory allocation scheme?",
        "option_a": "Segmentation", "option_b": "Fixed-size partitioning",
        "option_c": "Dynamic partitioning", "option_d": "Paging with variable page size",
        "correct_answer": "b", "difficulty": "medium",
        "explanation": "Fixed-size partitions waste space when a process is smaller than the partition — internal fragmentation.",
        "tags": "memory,fragmentation", "marks": 1,
    },
]


class Command(BaseCommand):
    help = "Seed 10 questions each for dbms, computer_network, operating_system"

    def handle(self, *args, **kwargs):
        inserted = 0
        skipped = 0
        for q in QUESTIONS:
            _, created = Question.objects.get_or_create(
                subject=q["subject"],
                question_text=q["question_text"],
                defaults={k: v for k, v in q.items() if k not in ("subject", "question_text")},
            )
            if created:
                inserted += 1
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"Done. Inserted: {inserted}, Skipped (already exist): {skipped}"
        ))
