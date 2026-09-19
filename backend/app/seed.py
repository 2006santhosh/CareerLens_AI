"""
Seed script. Populates a curated (not exhaustive, but non-trivial) dataset:
~70 canonical skills, 8 careers with weighted skill requirements, a
prerequisite dependency graph, learning resources, MCQ assessments for the
core DevOps-track skills, and one fully-populated demo student so a judge
can log in and immediately see a real end-to-end story.

Run with: python -m app.seed
"""
import random
from datetime import datetime, timedelta

from .database import SessionLocal, engine, Base
from . import models
from .auth import hash_password

random.seed(42)

# ---------------------------------------------------------------------------
# Canonical skills: name -> category
# ---------------------------------------------------------------------------
SKILLS = {
    # Programming languages
    "Python": "Programming", "Java": "Programming", "JavaScript": "Programming",
    "TypeScript": "Programming", "C++": "Programming", "Go": "Programming",
    "SQL": "Programming", "Bash Scripting": "Programming", "R": "Programming",

    # Web / Frontend
    "React": "Web Development", "HTML/CSS": "Web Development", "Vue.js": "Web Development",
    "Node.js": "Web Development", "REST APIs": "Web Development", "GraphQL": "Web Development",
    "Responsive Design": "Web Development",

    # Backend frameworks
    "FastAPI": "Backend", "Django": "Backend", "Flask": "Backend",
    "Spring Boot": "Backend", "Express.js": "Backend",

    # Database
    "PostgreSQL": "Database", "MongoDB": "Database", "Redis": "Database",
    "MySQL": "Database", "Database Design": "Database", "Data Modeling": "Database",

    # Version control / collaboration
    "Git": "Tools & Collaboration", "GitHub": "Tools & Collaboration", "Agile/Scrum": "Tools & Collaboration",

    # Cloud / DevOps
    "AWS": "Cloud", "Azure": "Cloud", "Google Cloud Platform": "Cloud",
    "Cloud Computing": "Cloud", "Docker": "DevOps", "Kubernetes": "DevOps",
    "CI/CD": "DevOps", "Terraform": "DevOps", "Linux": "DevOps",
    "Networking": "Networking", "Monitoring & Logging": "DevOps", "Ansible": "DevOps",

    # Data / ML
    "Machine Learning": "Data & AI", "Deep Learning": "Data & AI", "Data Analysis": "Data & AI",
    "Data Visualization": "Data & AI", "Pandas": "Data & AI", "NumPy": "Data & AI",
    "TensorFlow": "Data & AI", "PyTorch": "Data & AI", "Natural Language Processing": "Data & AI",
    "Statistics": "Data & AI", "Big Data (Spark)": "Data & AI",

    # Security
    "Cybersecurity": "Security", "Network Security": "Security", "Ethical Hacking": "Security",
    "Cryptography": "Security", "OWASP Top 10": "Security",

    # Mobile
    "Android Development": "Mobile", "iOS Development": "Mobile", "Flutter": "Mobile",
    "React Native": "Mobile",

    # System design / architecture
    "System Design": "System Design", "Microservices": "System Design",
    "API Design": "System Design", "Object-Oriented Design": "System Design",

    # Testing / QA
    "Unit Testing": "Quality & Testing", "Test Automation": "Quality & Testing", "Debugging": "Quality & Testing",

    # Soft / professional
    "Technical Communication": "Professional Skills", "Problem Solving": "Professional Skills",
    "Project Management": "Professional Skills",

    # Data structures / CS fundamentals
    "Data Structures": "CS Fundamentals", "Algorithms": "CS Fundamentals",
    "Operating Systems": "CS Fundamentals", "Computer Networks": "CS Fundamentals",
}

DIFFICULTY_OVERRIDES = {
    "Kubernetes": "Advanced", "Terraform": "Advanced", "Deep Learning": "Advanced",
    "Machine Learning": "Advanced", "System Design": "Advanced", "Microservices": "Advanced",
    "Cryptography": "Advanced", "Big Data (Spark)": "Advanced",
    "Git": "Beginner", "HTML/CSS": "Beginner", "Linux": "Beginner", "Python": "Beginner",
}

# prerequisite -> [skills it unlocks]
DEPENDENCIES = {
    "Linux": ["Docker", "Networking", "Bash Scripting"],
    "Networking": ["Cloud Computing", "AWS", "Network Security"],
    "Docker": ["Kubernetes", "CI/CD"],
    "Git": ["GitHub", "CI/CD"],
    "AWS": ["Terraform", "Cloud Computing"],
    "Cloud Computing": ["Kubernetes", "Terraform"],
    "Python": ["Django", "Flask", "FastAPI", "Data Analysis", "Machine Learning", "Pandas", "NumPy"],
    "JavaScript": ["React", "Node.js", "TypeScript", "Vue.js"],
    "React": ["React Native"],
    "Node.js": ["Express.js"],
    "SQL": ["PostgreSQL", "MySQL", "Database Design", "Data Modeling"],
    "Data Structures": ["Algorithms", "System Design"],
    "Algorithms": ["System Design"],
    "Statistics": ["Machine Learning", "Data Analysis"],
    "Machine Learning": ["Deep Learning", "Natural Language Processing"],
    "Pandas": ["Data Analysis", "Data Visualization"],
    "REST APIs": ["API Design", "Microservices", "GraphQL"],
    "Cybersecurity": ["Ethical Hacking", "Network Security", "OWASP Top 10"],
    "CI/CD": ["Monitoring & Logging"],
    "Unit Testing": ["Test Automation"],
}

# ---------------------------------------------------------------------------
# Careers: name -> {description, responsibilities, skills: {name: (required_level, importance)}}
# ---------------------------------------------------------------------------
CAREERS = {
    "DevOps Engineer": {
        "description": "Builds and maintains the infrastructure, automation, and deployment pipelines "
                        "that let engineering teams ship software reliably and quickly.",
        "responsibilities": "Design CI/CD pipelines\nManage cloud infrastructure as code\n"
                             "Monitor system reliability\nAutomate deployments\nRespond to incidents",
        "skills": {
            "Linux": (80, "High"), "Git": (80, "High"), "Networking": (75, "High"),
            "Docker": (85, "High"), "CI/CD": (85, "High"), "AWS": (80, "High"),
            "Kubernetes": (75, "High"), "Terraform": (70, "Medium"), "Python": (60, "Medium"),
            "Bash Scripting": (65, "Medium"), "Monitoring & Logging": (65, "Medium"),
            "Ansible": (55, "Low"), "System Design": (55, "Medium"),
        },
    },
    "Full Stack Developer": {
        "description": "Builds complete web applications spanning the user interface, backend "
                        "services, and the database layer that connects them.",
        "responsibilities": "Build frontend interfaces\nDesign backend APIs\nModel and query databases\n"
                             "Write tests\nDeploy applications",
        "skills": {
            "JavaScript": (80, "High"), "React": (80, "High"), "Node.js": (70, "High"),
            "HTML/CSS": (75, "High"), "REST APIs": (75, "High"), "SQL": (70, "High"),
            "Git": (75, "Medium"), "TypeScript": (65, "Medium"), "PostgreSQL": (65, "Medium"),
            "System Design": (55, "Medium"), "Docker": (45, "Low"), "Unit Testing": (55, "Medium"),
        },
    },
    "Backend Developer": {
        "description": "Designs and implements the server-side logic, APIs, and data layer that "
                        "power applications.",
        "responsibilities": "Design REST/GraphQL APIs\nModel databases\nOptimize performance\n"
                             "Ensure security and reliability\nWrite automated tests",
        "skills": {
            "Python": (75, "High"), "SQL": (80, "High"), "REST APIs": (85, "High"),
            "FastAPI": (65, "Medium"), "Django": (55, "Medium"), "PostgreSQL": (75, "High"),
            "Redis": (55, "Medium"), "System Design": (70, "High"), "Microservices": (60, "Medium"),
            "Git": (70, "Medium"), "Docker": (60, "Medium"), "Unit Testing": (65, "Medium"),
        },
    },
    "Data Scientist": {
        "description": "Analyzes data and builds models to extract insight and drive data-informed "
                        "decisions.",
        "responsibilities": "Explore and clean datasets\nBuild predictive models\nCommunicate insights\n"
                             "Design experiments\nDeploy models to production",
        "skills": {
            "Python": (80, "High"), "Statistics": (80, "High"), "Machine Learning": (80, "High"),
            "Pandas": (75, "High"), "NumPy": (70, "Medium"), "Data Visualization": (70, "Medium"),
            "SQL": (65, "Medium"), "Deep Learning": (55, "Medium"), "Data Analysis": (80, "High"),
            "Big Data (Spark)": (45, "Low"), "Technical Communication": (60, "Medium"),
        },
    },
    "Machine Learning Engineer": {
        "description": "Builds, trains, and deploys machine learning systems into production "
                        "environments.",
        "responsibilities": "Build ML pipelines\nTrain and evaluate models\nDeploy models to production\n"
                             "Monitor model performance\nCollaborate with data scientists",
        "skills": {
            "Python": (85, "High"), "Machine Learning": (85, "High"), "Deep Learning": (75, "High"),
            "TensorFlow": (65, "Medium"), "PyTorch": (65, "Medium"), "Statistics": (65, "Medium"),
            "Data Structures": (60, "Medium"), "Algorithms": (60, "Medium"), "Docker": (60, "Medium"),
            "System Design": (60, "Medium"), "SQL": (55, "Low"), "Natural Language Processing": (45, "Low"),
        },
    },
    "Cloud Engineer": {
        "description": "Designs, deploys, and manages scalable cloud infrastructure and services.",
        "responsibilities": "Architect cloud solutions\nManage infrastructure as code\nEnsure security "
                             "and cost efficiency\nAutomate provisioning\nMonitor cloud resources",
        "skills": {
            "AWS": (85, "High"), "Cloud Computing": (85, "High"), "Terraform": (75, "High"),
            "Networking": (75, "High"), "Linux": (70, "High"), "Docker": (65, "Medium"),
            "Kubernetes": (65, "Medium"), "Azure": (50, "Low"), "Python": (55, "Medium"),
            "System Design": (60, "Medium"), "Monitoring & Logging": (60, "Medium"),
        },
    },
    "Cybersecurity Analyst": {
        "description": "Protects systems and networks from security threats by monitoring, analyzing, "
                        "and responding to incidents.",
        "responsibilities": "Monitor systems for threats\nPerform vulnerability assessments\n"
                             "Respond to incidents\nHarden infrastructure\nEnsure compliance",
        "skills": {
            "Cybersecurity": (85, "High"), "Network Security": (80, "High"), "Networking": (75, "High"),
            "Ethical Hacking": (65, "Medium"), "Cryptography": (60, "Medium"), "Linux": (70, "High"),
            "OWASP Top 10": (65, "Medium"), "Python": (50, "Medium"), "Computer Networks": (65, "Medium"),
        },
    },
    "Mobile App Developer": {
        "description": "Builds native or cross-platform mobile applications for iOS and Android.",
        "responsibilities": "Build mobile UIs\nIntegrate with backend APIs\nOptimize performance\n"
                             "Test across devices\nPublish to app stores",
        "skills": {
            "React Native": (70, "Medium"), "Flutter": (65, "Medium"), "Android Development": (60, "Medium"),
            "iOS Development": (55, "Low"), "JavaScript": (65, "Medium"), "REST APIs": (70, "High"),
            "Git": (65, "Medium"), "Object-Oriented Design": (60, "Medium"), "Unit Testing": (50, "Low"),
        },
    },
}

RESOURCES = [
    # (skill, title, type, hours, url)
    ("Linux", "Linux Journey — Interactive Fundamentals", "Tutorial", 6, "https://linuxjourney.com/"),
    ("Linux", "The Linux Command Line (free book)", "Documentation", 8, "https://linuxcommand.org/tlcl.php"),
    ("Docker", "Docker Official Get Started Guide", "Documentation", 5, "https://docs.docker.com/get-started/"),
    ("Docker", "Docker Curriculum", "Tutorial", 6, "https://docker-curriculum.com/"),
    ("Kubernetes", "Kubernetes Official Tutorials", "Documentation", 10, "https://kubernetes.io/docs/tutorials/"),
    ("Kubernetes", "Kubernetes the Hard Way", "Project", 12, "https://github.com/kelseyhightower/kubernetes-the-hard-way"),
    ("CI/CD", "GitHub Actions Documentation", "Documentation", 5, "https://docs.github.com/en/actions"),
    ("CI/CD", "Build a CI/CD pipeline project", "Project", 6, "https://roadmap.sh/devops"),
    ("AWS", "AWS Cloud Practitioner Essentials", "Course", 10, "https://aws.amazon.com/training/digital/"),
    ("Terraform", "Terraform Official Tutorials", "Documentation", 8, "https://developer.hashicorp.com/terraform/tutorials"),
    ("Networking", "Computer Networking Course (freeCodeCamp)", "Video", 8, "https://www.freecodecamp.org/"),
    ("Python", "Python Official Tutorial", "Documentation", 8, "https://docs.python.org/3/tutorial/"),
    ("Bash Scripting", "Bash Scripting Tutorial", "Tutorial", 4, "https://ryanstutorials.net/bash-scripting-tutorial/"),
    ("Monitoring & Logging", "Prometheus Getting Started", "Documentation", 5, "https://prometheus.io/docs/introduction/overview/"),
    ("React", "React Official Docs", "Documentation", 8, "https://react.dev/learn"),
    ("Node.js", "Node.js Official Guides", "Documentation", 6, "https://nodejs.org/en/docs/guides"),
    ("SQL", "SQLBolt Interactive Lessons", "Tutorial", 5, "https://sqlbolt.com/"),
    ("PostgreSQL", "PostgreSQL Official Tutorial", "Documentation", 6, "https://www.postgresql.org/docs/current/tutorial.html"),
    ("Machine Learning", "Andrew Ng's Machine Learning Specialization", "Course", 20, "https://www.coursera.org/specializations/machine-learning-introduction"),
    ("Statistics", "Khan Academy Statistics", "Course", 10, "https://www.khanacademy.org/math/statistics-probability"),
    ("System Design", "System Design Primer", "Documentation", 10, "https://github.com/donnemartin/system-design-primer"),
    ("Git", "Pro Git Book (free)", "Documentation", 5, "https://git-scm.com/book/en/v2"),
]

# ---------------------------------------------------------------------------
# Assessments: (skill, title, [(prompt, options, correct_idx, explanation)])
# ---------------------------------------------------------------------------
ASSESSMENTS = {
    "Docker": [
        ("What does the Docker command `docker build` do?",
         ["Runs a container", "Builds an image from a Dockerfile", "Pushes an image to a registry", "Lists running containers"],
         1, "`docker build` reads a Dockerfile and produces a new image."),
        ("Which file defines how a Docker image is built?",
         ["docker-compose.yml", ".dockerignore", "Dockerfile", "image.json"],
         2, "A Dockerfile contains the instructions used to build an image."),
        ("What is the purpose of a Docker volume?",
         ["To scale containers horizontally", "To persist data outside a container's lifecycle", "To define network rules", "To compress images"],
         1, "Volumes let data survive beyond a single container's lifecycle."),
        ("Which command lists all running containers?",
         ["docker ps", "docker images", "docker run", "docker inspect"],
         0, "`docker ps` lists currently running containers."),
        ("What does `docker-compose up` do?",
         ["Removes all containers", "Builds and starts services defined in docker-compose.yml", "Pushes images to Docker Hub", "Stops the Docker daemon"],
         1, "It builds/starts every service declared in the compose file."),
        ("What is a multi-stage Docker build primarily used for?",
         ["Running multiple containers at once", "Reducing final image size by discarding build-only dependencies", "Increasing container CPU allocation", "Enabling GPU access"],
         1, "Multi-stage builds keep only what's needed in the final image, shrinking it."),
        ("Which base image type is typically smallest?",
         ["ubuntu:latest", "debian:latest", "alpine", "centos:latest"],
         2, "Alpine-based images are minimal and significantly smaller."),
        ("What does EXPOSE in a Dockerfile do?",
         ["Opens a port on the host automatically", "Documents which port the container listens on", "Starts a web server", "Grants root access"],
         1, "EXPOSE is documentation; you still need -p to publish the port to the host."),
        ("How do you view logs of a running container?",
         ["docker logs <container>", "docker view <container>", "docker status <container>", "docker inspect <container>"],
         0, "`docker logs` streams a container's stdout/stderr."),
        ("What does the container's network mode 'bridge' provide?",
         ["Direct host network access", "An isolated internal network with NAT to the host", "No networking at all", "A VPN to the internet"],
         1, "Bridge mode is Docker's default isolated network with NAT."),
    ],
    "Linux": [
        ("Which command lists files in a directory, including hidden ones?",
         ["ls", "ls -a", "cd", "pwd"], 1, "`ls -a` shows all files, including dotfiles."),
        ("What does `chmod 755 file.sh` do?",
         ["Deletes the file", "Sets read/write/execute for owner and read/execute for others", "Renames the file", "Compresses the file"],
         1, "755 = rwxr-xr-x."),
        ("Which command shows currently running processes?",
         ["ps aux", "lsblk", "df -h", "who"], 0, "`ps aux` lists all running processes."),
        ("What is the purpose of the `grep` command?",
         ["Compress files", "Search text using patterns", "Manage users", "Schedule jobs"], 1, "grep searches text for matching patterns."),
        ("Which command shows disk usage of the filesystem?",
         ["df -h", "top", "cat", "kill"], 0, "`df -h` shows filesystem disk usage in human-readable form."),
        ("What does `sudo` allow a user to do?",
         ["Send email", "Execute a command with elevated privileges", "Compress files faster", "Format a disk automatically"],
         1, "sudo runs a command as another user, typically root."),
        ("Which symbol redirects command output to a file, overwriting it?",
         [">>", ">", "|", "<"], 1, "`>` overwrites; `>>` appends."),
        ("What does `kill -9 <pid>` do?",
         ["Pauses a process", "Forcefully terminates a process", "Restarts a process", "Lists a process's memory"],
         1, "Signal 9 (SIGKILL) forcefully terminates a process."),
    ],
    "Python": [
        ("What data type is returned by `type([])`?",
         ["dict", "tuple", "list", "set"], 2, "An empty `[]` literal creates a list."),
        ("Which keyword defines a function in Python?",
         ["func", "def", "function", "lambda"], 1, "Functions are defined with `def`."),
        ("What does list comprehension `[x*2 for x in range(3)]` produce?",
         ["[0, 1, 2]", "[0, 2, 4]", "[2, 4, 6]", "[1, 2, 3]"], 1, "range(3) gives 0,1,2; doubled gives 0,2,4."),
        ("Which module is commonly used for handling JSON in Python?",
         ["json", "pickle", "os", "re"], 0, "The built-in `json` module encodes/decodes JSON."),
        ("What exception is raised when dividing by zero?",
         ["ValueError", "ZeroDivisionError", "TypeError", "IndexError"], 1, "Python raises ZeroDivisionError."),
        ("What does `self` refer to inside a class method?",
         ["The class itself", "The current instance of the class", "A global variable", "The parent class"], 1, "`self` refers to the current instance."),
    ],
    "AWS": [
        ("Which AWS service provides scalable object storage?",
         ["EC2", "S3", "RDS", "Lambda"], 1, "S3 is AWS's object storage service."),
        ("What is Amazon EC2 primarily used for?",
         ["Object storage", "Resizable virtual compute instances", "DNS management", "Email delivery"], 1, "EC2 provides resizable virtual servers."),
        ("Which AWS service lets you run code without provisioning servers?",
         ["Lambda", "EC2", "S3", "VPC"], 0, "Lambda runs code in response to events without managing servers."),
        ("What does IAM manage in AWS?",
         ["Databases", "Users, groups, roles, and permissions", "Container orchestration", "DNS routing"], 1, "IAM handles identity and access management."),
        ("Which service is AWS's managed relational database offering?",
         ["DynamoDB", "RDS", "Redshift", "S3"], 1, "RDS provides managed relational databases."),
    ],
    "CI/CD": [
        ("What is the primary goal of a CI/CD pipeline?",
         ["Manual code review only", "Automating build, test, and deployment steps", "Replacing version control", "Encrypting source code"], 1, "CI/CD automates integration and delivery."),
        ("What does 'CI' stand for in CI/CD?",
         ["Code Isolation", "Continuous Integration", "Container Instance", "Cloud Infrastructure"], 1, "CI = Continuous Integration."),
        ("Which of these is a common CI/CD tool?",
         ["GitHub Actions", "Photoshop", "Excel", "Figma"], 0, "GitHub Actions is a widely used CI/CD platform."),
        ("What is a 'build artifact'?",
         ["A bug report", "The output produced by a build process (e.g. a binary or image)", "A test case", "A commit message"], 1, "Artifacts are the packaged output of a build."),
        ("Why are automated tests important in a CI/CD pipeline?",
         ["They replace the need for deployment", "They catch regressions before code reaches production", "They slow down releases intentionally", "They are optional for small teams"], 1, "Automated tests catch issues early, before release."),
    ],
    "SQL": [
        ("Which SQL clause filters rows before aggregation?",
         ["HAVING", "WHERE", "GROUP BY", "ORDER BY"], 1, "WHERE filters rows before any grouping/aggregation."),
        ("What does a JOIN do in SQL?",
         ["Deletes rows", "Combines rows from two or more tables based on a related column", "Creates a new database", "Indexes a column"], 1, "JOIN merges rows across tables via a related key."),
        ("Which statement is used to add a new row to a table?",
         ["UPDATE", "INSERT", "ALTER", "SELECT"], 1, "INSERT adds new rows."),
        ("What does a PRIMARY KEY enforce?",
         ["Duplicate values are allowed", "Uniqueness and non-null identification of each row", "Automatic backups", "Faster network access"], 1, "A primary key uniquely and non-null identifies rows."),
        ("Which clause is used to sort query results?",
         ["GROUP BY", "ORDER BY", "WHERE", "HAVING"], 1, "ORDER BY sorts the result set."),
    ],
}

DEMO_EMAIL = "demo.student@careerlens.ai"
DEMO_PASSWORD = "DemoPass123!"

# Demo student's starting skill levels (creates meaningful, realistic gaps vs DevOps Engineer)
DEMO_SKILLS = {
    "Python": 72, "AWS": 60, "Git": 70, "Linux": 40, "Docker": 30,
    "CI/CD": 20, "Kubernetes": 10, "Terraform": 5, "Networking": 45,
    "Bash Scripting": 35, "Monitoring & Logging": 15, "SQL": 55,
    "REST APIs": 50, "System Design": 30,
}


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Skill).count() == 0:
            # --- Skills ---
            skill_objs: dict[str, models.Skill] = {}
            for name, category in SKILLS.items():
                skill = models.Skill(
                    name=name, category=category,
                    description=f"{name} is a core competency in the {category} category.",
                    difficulty=DIFFICULTY_OVERRIDES.get(name, "Intermediate"),
                )
                db.add(skill)
                skill_objs[name] = skill
            db.flush()
            print(f"Seeded {len(skill_objs)} skills.")

            # --- Dependencies ---
            dep_count = 0
            for prereq_name, unlocks in DEPENDENCIES.items():
                prereq = skill_objs.get(prereq_name)
                if not prereq:
                    continue
                for unlocked_name in unlocks:
                    unlocked = skill_objs.get(unlocked_name)
                    if not unlocked:
                        continue
                    db.add(models.SkillDependency(skill_id=unlocked.id, prerequisite_skill_id=prereq.id))
                    dep_count += 1
            print(f"Seeded {dep_count} skill dependencies.")
        else:
            print("Skills already seeded.")
            skill_objs = {s.name: s for s in db.query(models.Skill).all()}

        # --- Careers ---
        career_objs: dict[str, models.Career] = {}
        if db.query(models.Career).count() == 0:
            for name, data in CAREERS.items():
                career = models.Career(name=name, description=data["description"], responsibilities=data["responsibilities"])
                db.add(career)
                career_objs[name] = career
            db.flush()

            career_skill_count = 0
            for career_name, data in CAREERS.items():
                career = career_objs[career_name]
                for skill_name, (level, importance) in data["skills"].items():
                    skill = skill_objs.get(skill_name)
                    if not skill:
                        continue
                    db.add(models.CareerSkill(career_id=career.id, skill_id=skill.id,
                                            required_level=level, importance=importance, is_required=True))
                    career_skill_count += 1
            print(f"Seeded {len(career_objs)} careers and {career_skill_count} career-skill mappings.")
        else:
            print("Careers already seeded.")
            career_objs = {c.name: c for c in db.query(models.Career).all()}

        # --- Learning resources ---
        for skill_name, title, rtype, hours, url in RESOURCES:
            skill = skill_objs.get(skill_name)
            if not skill:
                continue
            db.add(models.LearningResource(
                skill_id=skill.id, title=title, type=rtype, difficulty="Intermediate",
                estimated_hours=hours, url=url, description=f"Curated resource for {skill_name}.", is_demo=False,
            ))
        print(f"Seeded {len(RESOURCES)} learning resources.")

        # --- Assessments ---
        assessment_count, question_count = 0, 0
        for skill_name, questions in ASSESSMENTS.items():
            skill = skill_objs.get(skill_name)
            if not skill:
                continue
            assessment = models.Assessment(
                skill_id=skill.id, title=f"{skill_name} Fundamentals Assessment",
                description=f"A {len(questions)}-question check of your {skill_name} fundamentals.",
                type="MCQ",
            )
            db.add(assessment)
            db.flush()
            for prompt, options, correct_idx, explanation in questions:
                db.add(models.AssessmentQuestion(
                    assessment_id=assessment.id, prompt=prompt, options=options,
                    correct_index=correct_idx, explanation=explanation,
                ))
                question_count += 1
            assessment_count += 1
        print(f"Seeded {assessment_count} assessments with {question_count} questions.")

        db.commit()

        # --- Demo student ---
        demo_user = models.User(
            full_name="Aditi Sharma", email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD),
            college="National Institute of Technology", degree="B.Tech", department="Computer Science",
            graduation_year=2026, onboarding_complete=True,
        )
        db.add(demo_user)
        db.flush()

        devops_career = career_objs["DevOps Engineer"]
        profile = models.StudentProfile(
            user_id=demo_user.id, target_career_id=devops_career.id, weekly_hours="5-10",
            preferred_learning_style="Mixed", career_interests="DevOps Engineer,Cloud Engineer",
            github_username="octocat",
        )
        db.add(profile)

        for skill_name, level in DEMO_SKILLS.items():
            skill = skill_objs.get(skill_name)
            if not skill:
                continue
            status = "self_reported"
            has_resume = level >= 40
            has_project = level >= 55
            if level >= 70:
                status = "verified"
            elif level >= 40:
                status = "evidence_found"
            progress = models.StudentProgress(
                user_id=demo_user.id, skill_id=skill.id, level=level, status=status,
                has_resume_evidence=has_resume, has_project_evidence=has_project,
            )
            db.add(progress)

        demo_evidence = models.Evidence(
            user_id=demo_user.id, type="resume", title="Resume: Aditi_Sharma_Resume.pdf",
            description="Seed demo resume evidence.", source_filename="Aditi_Sharma_Resume.pdf",
        )
        db.add(demo_evidence)

        db.commit()

        # Historical readiness snapshots so the analytics trend chart has data
        base_time = datetime.utcnow() - timedelta(days=20)
        for i, val in enumerate([42.0, 48.5, 55.0, 61.5]):
            snap = models.ReadinessSnapshot(
                user_id=demo_user.id, career_id=devops_career.id, overall_readiness=val,
                technical_skills=val + 5, project_evidence=val - 8, assessment_performance=val - 3,
                skill_coverage=val + 2, verification=val - 15,
            )
            db.add(snap)
            snap.created_at = base_time + timedelta(days=i * 5)
        db.commit()

        print(f"Seeded demo student: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print("Seeding complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
