from ghostsec import create_app, db, bcrypt
from ghostsec.models import (
    User, PythonExercise, KaliLab, Achievement,
    CTFChallenge, LearningModule, MalwareAnalysisLab,
    PenTestLab, CPPExercise
)
from datetime import datetime
from cryptography.fernet import Fernet
import os
import json
from dotenv import load_dotenv

def create_initial_python_exercises():
    exercises = [
        {
            'title': 'Hello, Security!',
            'description': 'Write your first security-focused Python program.',
            'difficulty': 'Beginner',
            'category': 'Basics',
            'starter_code': 'def greet_hacker():\n    # Your code here\n    pass',
            'solution': 'def greet_hacker():\n    return "Welcome to GhostSec!"',
            'test_cases': json.dumps([
                {'input': [], 'expected': 'Welcome to GhostSec!'}
            ]),
            'points': 10,
            'hints': json.dumps(['Think about a simple return statement']),
            'order': 1
        },
        {
            'title': 'Password Validator',
            'description': 'Create a function to validate password strength.',
            'difficulty': 'Intermediate',
            'category': 'Security',
            'starter_code': 'def validate_password(password):\n    # Your code here\n    pass',
            'solution': '''def validate_password(password):
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return has_upper and has_lower and has_digit and has_special''',
            'test_cases': json.dumps([
                {'input': ['Weak123!'], 'expected': True},
                {'input': ['weak'], 'expected': False},
                {'input': ['NoSpecial1'], 'expected': False}
            ]),
            'points': 20,
            'hints': json.dumps([
                'Check for minimum length',
                'Look for uppercase, lowercase, digits, and special characters'
            ]),
            'order': 2
        }
    ]
    
    for exercise_data in exercises:
        exercise = PythonExercise(**exercise_data)
        db.session.add(exercise)

def create_initial_kali_labs():
    labs = [
        {
            'title': 'Setting Up Your Kali Environment',
            'description': 'Learn how to set up and configure your Kali Linux environment for penetration testing.',
            'difficulty': 'Beginner',
            'category': 'Setup',
            'tools_required': json.dumps(['VirtualBox', 'Kali Linux ISO']),
            'instructions': '''1. Download VirtualBox
2. Download Kali Linux ISO
3. Create a new Virtual Machine
4. Configure system resources
5. Install Kali Linux
6. Update system packages
7. Configure basic security settings''',
            'solution_guide': 'Step-by-step guide for Kali Linux installation and configuration...',
            'points': 20,
            'estimated_time': 60,
            'prerequisites': json.dumps([])
        },
        {
            'title': 'Network Scanning with Nmap',
            'description': 'Master the basics of network scanning using Nmap.',
            'difficulty': 'Intermediate',
            'category': 'Network Security',
            'tools_required': json.dumps(['nmap']),
            'instructions': '''1. Understanding Nmap syntax
2. Basic host discovery
3. Port scanning techniques
4. Service version detection
5. OS fingerprinting
6. Saving and analyzing results''',
            'solution_guide': 'Detailed guide for network scanning techniques...',
            'points': 30,
            'estimated_time': 90,
            'prerequisites': json.dumps([1])  # Requires "Setting Up Your Kali Environment"
        }
    ]
    
    for lab_data in labs:
        lab = KaliLab(**lab_data)
        db.session.add(lab)

def create_initial_malware_labs():
    labs = [
        {
            'title': 'Introduction to Safe Malware Analysis',
            'description': 'Learn the fundamentals of safe malware analysis and setup a secure analysis environment.',
            'category': 'Analysis',
            'difficulty': 'Beginner',
            'malware_type': 'General',
            'tools_required': json.dumps(['VirtualBox', 'REMnux', 'IDA Free']),
            'environment_setup': '''1. Install VirtualBox
2. Download and import REMnux VM
3. Configure network isolation
4. Set up shared folders with write protection
5. Install analysis tools
6. Configure system snapshots''',
            'analysis_steps': '''1. Initial environment setup
2. Basic static analysis techniques
3. Safe dynamic analysis procedures
4. Network traffic monitoring
5. Memory analysis basics''',
            'safety_precautions': '''1. Always work in an isolated environment
2. Never execute malware on your host machine
3. Use network isolation
4. Regular backups and snapshots
5. Proper handling of malware samples''',
            'points': 30,
            'estimated_time': 120,
            'prerequisites': json.dumps([])
        },
        {
            'title': 'Modern Ransomware Analysis',
            'description': 'Study and analyze modern ransomware behavior and protection techniques.',
            'category': 'Modern Types',
            'difficulty': 'Intermediate',
            'malware_type': 'Ransomware',
            'tools_required': json.dumps(['IDA Pro', 'Process Monitor', 'Wireshark']),
            'environment_setup': 'Detailed setup instructions for ransomware analysis environment...',
            'analysis_steps': '''1. Initial static analysis
2. Behavioral analysis
3. Network communication analysis
4. Encryption mechanism analysis
5. Recovery possibilities assessment''',
            'safety_precautions': 'Comprehensive safety measures for ransomware analysis...',
            'points': 50,
            'estimated_time': 180,
            'prerequisites': json.dumps([1])
        }
    ]
    
    for lab_data in labs:
        lab = MalwareAnalysisLab(**lab_data)
        db.session.add(lab)

def create_initial_pentest_labs():
    labs = [
        {
            'title': 'Web Application Penetration Testing',
            'description': 'Learn systematic approach to web application security testing.',
            'category': 'Web',
            'difficulty': 'Beginner',
            'target_setup': 'Instructions for setting up vulnerable web application...',
            'tools_required': json.dumps(['Burp Suite', 'OWASP ZAP', 'SQLMap']),
            'methodology': '''1. Information Gathering
2. Vulnerability Scanning
3. SQL Injection Testing
4. XSS Testing
5. Authentication Testing
6. Authorization Testing
7. Session Management Testing''',
            'objectives': json.dumps([
                'Identify common web vulnerabilities',
                'Perform manual and automated testing',
                'Document findings properly',
                'Suggest remediation steps'
            ]),
            'points': 40,
            'estimated_time': 150,
            'prerequisites': json.dumps([])
        },
        {
            'title': 'Network Penetration Testing',
            'description': 'Master the art of network security assessment.',
            'category': 'Network',
            'difficulty': 'Intermediate',
            'target_setup': 'Instructions for setting up vulnerable network environment...',
            'tools_required': json.dumps(['Nmap', 'Metasploit', 'Wireshark']),
            'methodology': '''1. Network Discovery
2. Port Scanning
3. Service Enumeration
4. Vulnerability Assessment
5. Exploitation
6. Post Exploitation
7. Documentation''',
            'objectives': json.dumps([
                'Perform comprehensive network reconnaissance',
                'Identify and exploit vulnerabilities',
                'Maintain access and cover tracks',
                'Document findings and suggest fixes'
            ]),
            'points': 60,
            'estimated_time': 240,
            'prerequisites': json.dumps([1])
        }
    ]
    
    for lab_data in labs:
        lab = PenTestLab(**lab_data)
        db.session.add(lab)

def create_initial_cpp_exercises():
    exercises = [
        {
            'title': 'Secure Memory Management',
            'description': 'Learn proper memory management techniques in C++.',
            'category': 'Memory Management',
            'difficulty': 'Beginner',
            'language': 'C++',
            'starter_code': '''class SecureBuffer {
    // TODO: Implement secure buffer with proper memory management
private:
    char* buffer;
    size_t size;
public:
    SecureBuffer(size_t size);
    ~SecureBuffer();
    // Add necessary methods
};''',
            'solution': '''class SecureBuffer {
private:
    char* buffer;
    size_t size;
public:
    SecureBuffer(size_t size) : size(size) {
        buffer = new char[size];
        std::memset(buffer, 0, size);
    }
    
    ~SecureBuffer() {
        if (buffer) {
            std::memset(buffer, 0, size);
            delete[] buffer;
        }
    }
    
    // Prevent copying
    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;
    
    // Allow moving
    SecureBuffer(SecureBuffer&& other) noexcept
        : buffer(other.buffer), size(other.size) {
        other.buffer = nullptr;
        other.size = 0;
    }
    
    SecureBuffer& operator=(SecureBuffer&& other) noexcept {
        if (this != &other) {
            delete[] buffer;
            buffer = other.buffer;
            size = other.size;
            other.buffer = nullptr;
            other.size = 0;
        }
        return *this;
    }
};''',
            'test_cases': json.dumps([
                {'input': [], 'expected': 'No memory leaks'},
                {'input': ['move'], 'expected': 'Proper move semantics'}
            ]),
            'memory_constraints': 'Must properly clean up memory and prevent leaks',
            'security_focus': '''1. Secure memory handling
2. Prevention of buffer overflows
3. RAII principles
4. Move semantics''',
            'points': 25,
            'hints': json.dumps([
                'Remember to clear sensitive data before freeing memory',
                'Implement RAII pattern',
                'Consider move semantics for efficiency'
            ]),
            'order': 1
        },
        {
            'title': 'Buffer Overflow Prevention',
            'description': 'Learn to write C code that prevents buffer overflow vulnerabilities.',
            'category': 'Security',
            'difficulty': 'Intermediate',
            'language': 'C',
            'starter_code': '''void process_input(char* input, size_t input_size) {
    char buffer[64];
    // TODO: Implement secure input processing
}''',
            'solution': '''void process_input(char* input, size_t input_size) {
    char buffer[64];
    if (input == NULL || input_size > sizeof(buffer) - 1) {
        return;
    }
    
    strncpy(buffer, input, sizeof(buffer) - 1);
    buffer[sizeof(buffer) - 1] = '\\0';
    
    // Process buffer safely...
}''',
            'test_cases': json.dumps([
                {'input': ['short string', 12], 'expected': 'Success'},
                {'input': ['very long string...', 1000], 'expected': 'Prevented overflow'}
            ]),
            'memory_constraints': 'Stack buffer limited to 64 bytes',
            'security_focus': '''1. Buffer overflow prevention
2. Input validation
3. Safe string handling
4. Boundary checking''',
            'points': 35,
            'hints': json.dumps([
                'Always validate input size',
                'Use strncpy instead of strcpy',
                'Null-terminate strings explicitly'
            ]),
            'order': 2
        }
    ]
    
    for exercise_data in exercises:
        exercise = CPPExercise(**exercise_data)
        db.session.add(exercise)

def create_initial_achievements():
    achievements = [
        {
            'name': 'First Steps',
            'description': 'Complete your first Python exercise',
            'category': 'Python',
            'points': 10,
            'criteria': json.dumps({'python_exercises_completed': 1})
        },
        {
            'name': 'Script Kiddie',
            'description': 'Complete 5 Python exercises',
            'category': 'Python',
            'points': 50,
            'criteria': json.dumps({'python_exercises_completed': 5})
        },
        {
            'name': 'Kali Warrior',
            'description': 'Complete 3 Kali Linux labs',
            'category': 'Kali',
            'points': 100,
            'criteria': json.dumps({'kali_labs_completed': 3})
        },
        {
            'name': 'Flag Hunter',
            'description': 'Capture 5 flags in CTF challenges',
            'category': 'CTF',
            'points': 150,
            'criteria': json.dumps({'ctf_flags_captured': 5})
        }
    ]
    
    for achievement_data in achievements:
        achievement = Achievement(**achievement_data)
        db.session.add(achievement)

def create_additional_achievements():
    achievements = [
        {
            'name': 'Malware Hunter',
            'description': 'Complete 3 malware analysis labs',
            'category': 'Malware',
            'points': 100,
            'criteria': json.dumps({'malware_labs_completed': 3})
        },
        {
            'name': 'Network Ninja',
            'description': 'Complete 5 penetration testing labs',
            'category': 'PenTest',
            'points': 150,
            'criteria': json.dumps({'pentest_labs_completed': 5})
        },
        {
            'name': 'Memory Master',
            'description': 'Complete all C++ memory management exercises',
            'category': 'C++',
            'points': 120,
            'criteria': json.dumps({'cpp_memory_exercises_completed': 'all'})
        }
    ]
    
    for achievement_data in achievements:
        achievement = Achievement(**achievement_data)
        db.session.add(achievement)

def init_database():
    # Generate encryption key if not exists
    if not os.getenv('ENCRYPTION_KEY'):
        encryption_key = Fernet.generate_key()
        with open('.env', 'a') as f:
            f.write(f"\nENCRYPTION_KEY={encryption_key.decode()}")
    
    # Load environment variables
    load_dotenv()
    
    app = create_app()
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@ghostsec.com').first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash('Anonymous@23!').decode('utf-8')
            admin = User(
                username='admin',
                email='admin@ghostsec.com',
                password=hashed_password,
                is_admin=True,
                date_joined=datetime.utcnow()
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            admin.password = bcrypt.generate_password_hash('Anonymous@23!').decode('utf-8')
            db.session.commit()
            print("Admin password updated!")
        
        # Initialize learning content
        if not PythonExercise.query.first():
            print("Creating initial Python exercises...")
            create_initial_python_exercises()
        
        if not KaliLab.query.first():
            print("Creating initial Kali Linux labs...")
            create_initial_kali_labs()
        
        if not MalwareAnalysisLab.query.first():
            print("Creating initial Malware Analysis labs...")
            create_initial_malware_labs()
        
        if not PenTestLab.query.first():
            print("Creating initial Penetration Testing labs...")
            create_initial_pentest_labs()
        
        if not CPPExercise.query.first():
            print("Creating initial C/C++ exercises...")
            create_initial_cpp_exercises()
        
        if not Achievement.query.first():
            print("Creating achievements...")
            create_initial_achievements()
            create_additional_achievements()
        
        # Commit all changes
        db.session.commit()
        print("Database initialized successfully!")
        print("\nDefault admin credentials:")
        print("Email: admin@ghostsec.com")
        print("Password: Anonymous@23!")

if __name__ == '__main__':
    init_database()
