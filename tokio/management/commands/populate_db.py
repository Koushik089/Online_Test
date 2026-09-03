# tokio/management/commands/populate_db.py
from django.core.management.base import BaseCommand
from tokio.models import Question

class Command(BaseCommand):
    help = 'Seeds the database with default high-quality questions for DBMS, CN, and OS'

    def handle(self, *args, **options):
        questions_data = [
            # ================== DBMS ==================
            {
                'subject': 'dbms',
                'question_text': 'Which of the following is not a type of database?',
                'option_a': 'Hierarchical',
                'option_b': 'Network',
                'option_c': 'Distributed',
                'option_d': 'Decentralized',
                'correct_answer': 'd'
            },
            {
                'subject': 'dbms',
                'question_text': 'What does SQL stand for?',
                'option_a': 'Structured Query Language',
                'option_b': 'Strong Question Language',
                'option_c': 'Simple Query Language',
                'option_d': 'Server Question Language',
                'correct_answer': 'a'
            },
            {
                'subject': 'dbms',
                'question_text': 'Which of the following is used to uniquely identify a record in a table?',
                'option_a': 'Foreign Key',
                'option_b': 'Primary Key',
                'option_c': 'Unique Key',
                'option_d': 'Index',
                'correct_answer': 'b'
            },
            {
                'subject': 'dbms',
                'question_text': 'Which command is used to remove all records from a table, including spaces?',
                'option_a': 'DELETE',
                'option_b': 'DROP',
                'option_c': 'REMOVE',
                'option_d': 'TRUNCATE',
                'correct_answer': 'd'
            },
            {
                'subject': 'dbms',
                'question_text': 'Which of the following is not a DML command?',
                'option_a': 'INSERT',
                'option_b': 'DELETE',
                'option_c': 'UPDATE',
                'option_d': 'CREATE',
                'correct_answer': 'd'
            },
            {
                'subject': 'dbms',
                'question_text': 'In normalization, which normal form eliminates transitive dependency?',
                'option_a': '1NF',
                'option_b': '2NF',
                'option_c': '3NF',
                'option_d': 'BCNF',
                'correct_answer': 'c'
            },
            {
                'subject': 'dbms',
                'question_text': 'What is a foreign key?',
                'option_a': 'A key that uniquely identifies a row',
                'option_b': 'A key in one table that refers to the primary key in another table',
                'option_c': 'A key used for encryption',
                'option_d': 'None of the above',
                'correct_answer': 'b'
            },
            {
                'subject': 'dbms',
                'question_text': 'Which of the following is not a constraint in SQL?',
                'option_a': 'NOT NULL',
                'option_b': 'UNIQUE',
                'option_c': 'INDEX',
                'option_d': 'CHECK',
                'correct_answer': 'c'
            },
            {
                'subject': 'dbms',
                'question_text': 'What is the purpose of the GROUP BY clause?',
                'option_a': 'To filter rows',
                'option_b': 'To group rows that have the same values',
                'option_c': 'To sort rows',
                'option_d': 'To delete rows',
                'correct_answer': 'b'
            },
            {
                'subject': 'dbms',
                'question_text': 'Which of these is an ACID property of a transaction?',
                'option_a': 'Atomicity',
                'option_b': 'Concurrency',
                'option_c': 'Deadlock',
                'option_d': 'Backup',
                'correct_answer': 'a'
            },

            # ================== COMPUTER NETWORKS ==================
            {
                'subject': 'computer_network',
                'question_text': 'Which layer of the OSI model is responsible for end-to-end communication?',
                'option_a': 'Network Layer',
                'option_b': 'Transport Layer',
                'option_c': 'Session Layer',
                'option_d': 'Data Link Layer',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the default port number for HTTP?',
                'option_a': '443',
                'option_b': '20',
                'option_c': '21',
                'option_d': '80',
                'correct_answer': 'd'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Which protocol is used for email transmission?',
                'option_a': 'HTTP',
                'option_b': 'SMTP',
                'option_c': 'FTP',
                'option_d': 'TCP',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the chemical symbol for Gold?',
                'option_a': 'Au',
                'option_b': 'Ag',
                'option_c': 'Gd',
                'option_d': 'Ga',
                'correct_answer': 'a'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Who wrote the play "Romeo and Juliet"?',
                'option_a': 'William Shakespeare',
                'option_b': 'Charles Dickens',
                'option_c': 'Jane Austen',
                'option_d': 'Mark Twain',
                'correct_answer': 'a'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the value of π (pi) up to two decimal places?',
                'option_a': '3.12',
                'option_b': '3.14',
                'option_c': '3.16',
                'option_d': '3.18',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Which planet is known as the Red Planet?',
                'option_a': 'Venus',
                'option_b': 'Mars',
                'option_c': 'Jupiter',
                'option_d': 'Saturn',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the main function of the CPU in a computer?',
                'option_a': 'Store data',
                'option_b': 'Process instructions',
                'option_c': 'Display graphics',
                'option_d': 'Manage network connections',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'In which year did World War II end?',
                'option_a': '1945',
                'option_b': '1939',
                'option_c': '1918',
                'option_d': '1950',
                'correct_answer': 'a'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the capital city of Australia?',
                'option_a': 'Sydney',
                'option_b': 'Melbourne',
                'option_c': 'Canberra',
                'option_d': 'Brisbane',
                'correct_answer': 'c'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What does HTML stand for?',
                'option_a': 'HyperText Markup Language',
                'option_b': 'Hyperlinks and Text Markup Language',
                'option_c': 'Home Tool Markup Language',
                'option_d': 'Hyperlinking Text Marking Language',
                'correct_answer': 'a'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Which gas is most abundant in the Earth\'s atmosphere?',
                'option_a': 'Oxygen',
                'option_b': 'Nitrogen',
                'option_c': 'Carbon Dioxide',
                'option_d': 'Hydrogen',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Who is known as the father of modern physics?',
                'option_a': 'Isaac Newton',
                'option_b': 'Albert Einstein',
                'option_c': 'Galileo Galilei',
                'option_d': 'Nikola Tesla',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the square root of 144?',
                'option_a': '10',
                'option_b': '11',
                'option_c': '12',
                'option_d': '13',
                'correct_answer': 'c'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Which element has the atomic number 1?',
                'option_a': 'Helium',
                'option_b': 'Hydrogen',
                'option_c': 'Oxygen',
                'option_d': 'Carbon',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the main language used for Android app development?',
                'option_a': 'Swift',
                'option_b': 'Kotlin',
                'option_c': 'JavaScript',
                'option_d': 'Ruby',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Which country hosted the 2016 Summer Olympics?',
                'option_a': 'China',
                'option_b': 'Brazil',
                'option_c': 'United Kingdom',
                'option_d': 'Russia',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the powerhouse of the cell?',
                'option_a': 'Nucleus',
                'option_b': 'Mitochondria',
                'option_c': 'Ribosome',
                'option_d': 'Chloroplast',
                'correct_answer': 'b'
            },
            {
                'subject': 'computer_network',
                'question_text': 'Which programming language is primarily used for iOS app development?',
                'option_a': 'Swift',
                'option_b': 'Java',
                'option_c': 'Python',
                'option_d': 'C#',
                'correct_answer': 'a'
            },
            {
                'subject': 'computer_network',
                'question_text': 'What is the boiling point of water at sea level in Celsius?',
                'option_a': '90°C',
                'option_b': '95°C',
                'option_c': '100°C',
                'option_d': '105°C',
                'correct_answer': 'c'
            },

            # ================== OPERATING SYSTEMS ==================
            {
                'subject': 'operating_system',
                'question_text': 'What is the primary function of an operating system?',
                'option_a': 'Manage hardware and software resources',
                'option_b': 'Develop software applications',
                'option_c': 'Provide internet connectivity',
                'option_d': 'Store user data permanently',
                'correct_answer': 'a'
            },
            {
                'subject': 'operating_system',
                'question_text': 'Which of the following is NOT an operating system?',
                'option_a': 'Windows',
                'option_b': 'Linux',
                'option_c': 'Oracle',
                'option_d': 'macOS',
                'correct_answer': 'c'
            },
            {
                'subject': 'operating_system',
                'question_text': 'What does GUI stand for in operating systems?',
                'option_a': 'Graphical User Interface',
                'option_b': 'General Utility Interface',
                'option_c': 'Graphical Utility Integration',
                'option_d': 'General User Interaction',
                'correct_answer': 'a'
            },
            {
                'subject': 'operating_system',
                'question_text': 'Which operating system is known for its open-source nature?',
                'option_a': 'Windows',
                'option_b': 'Linux',
                'option_c': 'macOS',
                'option_d': 'iOS',
                'correct_answer': 'b'
            },
            {
                'subject': 'operating_system',
                'question_text': 'What is the kernel in an operating system?',
                'option_a': 'User interface',
                'option_b': 'Core component managing system resources',
                'option_c': 'Application software',
                'option_d': 'Hardware device',
                'correct_answer': 'b'
            },
            {
                'subject': 'operating_system',
                'question_text': 'Which of the following is a type of operating system that supports multiple users simultaneously?',
                'option_a': 'Single-user OS',
                'option_b': 'Multi-user OS',
                'option_c': 'Real-time OS',
                'option_d': 'Batch OS',
                'correct_answer': 'b'
            },
            {
                'subject': 'operating_system',
                'question_text': 'What is virtual memory?',
                'option_a': 'Physical RAM installed on the computer',
                'option_b': 'A memory management technique that uses disk space as additional RAM',
                'option_c': 'Cache memory inside the CPU',
                'option_d': 'Memory used by the graphics card',
                'correct_answer': 'b'
            },
            {
                'subject': 'operating_system',
                'question_text': 'Which scheduling algorithm allocates the CPU to the process that requests it first?',
                'option_a': 'Shortest Job First (SJF)',
                'option_b': 'First-Come, First-Served (FCFS)',
                'option_c': 'Round Robin (RR)',
                'option_d': 'Priority Scheduling',
                'correct_answer': 'b'
            },
            {
                'subject': 'operating_system',
                'question_text': 'What is a deadlock in operating systems?',
                'option_a': 'A system crash due to a hardware failure',
                'option_b': 'A situation where a set of processes are blocked because each holds a resource and waits for another',
                'option_c': 'A high-speed network connection drop',
                'option_d': 'An infinite loop in a user application',
                'correct_answer': 'b'
            },
            {
                'subject': 'operating_system',
                'question_text': 'Which command is used to list files in a directory in Linux/Unix?',
                'option_a': 'dir',
                'option_b': 'ls',
                'option_c': 'list',
                'option_d': 'show',
                'correct_answer': 'b'
            }
        ]

        created_count = 0
        skipped_count = 0

        for q_data in questions_data:
            # Check for duplicate questions based on subject and question_text
            obj, created = Question.objects.get_or_create(
                subject=q_data['subject'],
                question_text=q_data['question_text'],
                defaults={
                    'option_a': q_data['option_a'],
                    'option_b': q_data['option_b'],
                    'option_c': q_data['option_c'],
                    'option_d': q_data['option_d'],
                    'correct_answer': q_data['correct_answer']
                }
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeding completed successfully! Created {created_count} new questions, skipped {skipped_count} duplicates.'
        ))
