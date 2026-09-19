"""
Seed script. Populates a curated (not exhaustive, but non-trivial) dataset:
~105 canonical skills, 15 careers with weighted skill requirements, a
prerequisite dependency graph, learning resources, MCQ assessments for the
core skill set, and one fully-populated demo student so a judge
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
    "Rust": "Programming", "Kotlin": "Programming", "Swift": "Programming",
    "Scala": "Programming", "C#": "Programming",

    # Web / Frontend
    "React": "Web Development", "HTML/CSS": "Web Development", "Vue.js": "Web Development",
    "Node.js": "Web Development", "REST APIs": "Web Development", "GraphQL": "Web Development",
    "Responsive Design": "Web Development", "Angular": "Web Development",
    "Webpack": "Web Development", "Accessibility (a11y)": "Web Development",
    "Next.js": "Web Development",

    # Backend frameworks
    "FastAPI": "Backend", "Django": "Backend", "Flask": "Backend",
    "Spring Boot": "Backend", "Express.js": "Backend", "ASP.NET Core": "Backend",
    "Laravel": "Backend",

    # Database
    "PostgreSQL": "Database", "MongoDB": "Database", "Redis": "Database",
    "MySQL": "Database", "Database Design": "Database", "Data Modeling": "Database",
    "Elasticsearch": "Database", "Cassandra": "Database",

    # Version control / collaboration
    "Git": "Tools & Collaboration", "GitHub": "Tools & Collaboration", "Agile/Scrum": "Tools & Collaboration",
    "Jira": "Tools & Collaboration", "Code Review": "Tools & Collaboration",

    # Cloud / DevOps
    "AWS": "Cloud", "Azure": "Cloud", "Google Cloud Platform": "Cloud",
    "Cloud Computing": "Cloud", "Docker": "DevOps", "Kubernetes": "DevOps",
    "CI/CD": "DevOps", "Terraform": "DevOps", "Linux": "DevOps",
    "Networking": "Networking", "Monitoring & Logging": "DevOps", "Ansible": "DevOps",
    "Helm": "DevOps", "GitOps": "DevOps", "Service Mesh": "DevOps",

    # Data / ML
    "Machine Learning": "Data & AI", "Deep Learning": "Data & AI", "Data Analysis": "Data & AI",
    "Data Visualization": "Data & AI", "Pandas": "Data & AI", "NumPy": "Data & AI",
    "TensorFlow": "Data & AI", "PyTorch": "Data & AI", "Natural Language Processing": "Data & AI",
    "Statistics": "Data & AI", "Big Data (Spark)": "Data & AI",
    "Feature Engineering": "Data & AI", "MLOps": "Data & AI",
    "Data Pipelines": "Data & AI", "dbt": "Data & AI",
    "Computer Vision": "Data & AI", "Reinforcement Learning": "Data & AI",
    "LLM & Prompt Engineering": "Data & AI",

    # Security
    "Cybersecurity": "Security", "Network Security": "Security", "Ethical Hacking": "Security",
    "Cryptography": "Security", "OWASP Top 10": "Security",
    "Security Compliance": "Security", "Penetration Testing": "Security",
    "Cloud Security": "Security",

    # Mobile
    "Android Development": "Mobile", "iOS Development": "Mobile", "Flutter": "Mobile",
    "React Native": "Mobile",

    # System design / architecture
    "System Design": "System Design", "Microservices": "System Design",
    "API Design": "System Design", "Object-Oriented Design": "System Design",
    "Event-Driven Architecture": "System Design", "Message Queues": "System Design",
    "Caching Strategies": "System Design",

    # Testing / QA
    "Unit Testing": "Quality & Testing", "Test Automation": "Quality & Testing", "Debugging": "Quality & Testing",
    "Performance Testing": "Quality & Testing", "End-to-End Testing": "Quality & Testing",

    # Soft / professional
    "Technical Communication": "Professional Skills", "Problem Solving": "Professional Skills",
    "Project Management": "Professional Skills", "Leadership": "Professional Skills",
    "Documentation": "Professional Skills",

    # Data structures / CS fundamentals
    "Data Structures": "CS Fundamentals", "Algorithms": "CS Fundamentals",
    "Operating Systems": "CS Fundamentals", "Computer Networks": "CS Fundamentals",
    "Compiler Design": "CS Fundamentals",
}

DIFFICULTY_OVERRIDES = {
    "Kubernetes": "Advanced", "Terraform": "Advanced", "Deep Learning": "Advanced",
    "Machine Learning": "Advanced", "System Design": "Advanced", "Microservices": "Advanced",
    "Cryptography": "Advanced", "Big Data (Spark)": "Advanced",
    "Reinforcement Learning": "Advanced", "Service Mesh": "Advanced",
    "Compiler Design": "Advanced", "Computer Vision": "Advanced",
    "LLM & Prompt Engineering": "Advanced", "MLOps": "Advanced",
    "Penetration Testing": "Advanced", "Cassandra": "Advanced",
    "Git": "Beginner", "HTML/CSS": "Beginner", "Linux": "Beginner", "Python": "Beginner",
    "Jira": "Beginner", "Documentation": "Beginner",
}

# prerequisite -> [skills it unlocks]
DEPENDENCIES = {
    "Linux": ["Docker", "Networking", "Bash Scripting"],
    "Networking": ["Cloud Computing", "AWS", "Network Security"],
    "Docker": ["Kubernetes", "CI/CD"],
    "Git": ["GitHub", "CI/CD", "GitOps"],
    "AWS": ["Terraform", "Cloud Computing", "Cloud Security"],
    "Cloud Computing": ["Kubernetes", "Terraform", "Cloud Security"],
    "Python": ["Django", "Flask", "FastAPI", "Data Analysis", "Machine Learning", "Pandas", "NumPy"],
    "JavaScript": ["React", "Node.js", "TypeScript", "Vue.js", "Angular"],
    "React": ["React Native", "Next.js"],
    "Node.js": ["Express.js"],
    "SQL": ["PostgreSQL", "MySQL", "Database Design", "Data Modeling", "dbt"],
    "Data Structures": ["Algorithms", "System Design"],
    "Algorithms": ["System Design"],
    "Statistics": ["Machine Learning", "Data Analysis"],
    "Machine Learning": ["Deep Learning", "Natural Language Processing", "Computer Vision",
                         "Reinforcement Learning", "Feature Engineering", "MLOps"],
    "Pandas": ["Data Analysis", "Data Visualization", "Feature Engineering"],
    "REST APIs": ["API Design", "Microservices", "GraphQL"],
    "Cybersecurity": ["Ethical Hacking", "Network Security", "OWASP Top 10", "Penetration Testing"],
    "CI/CD": ["Monitoring & Logging", "GitOps"],
    "Unit Testing": ["Test Automation", "End-to-End Testing"],
    "Kubernetes": ["Helm", "Service Mesh"],
    "Microservices": ["Event-Driven Architecture", "Message Queues", "Service Mesh"],
    "System Design": ["Caching Strategies", "Event-Driven Architecture"],
    "Deep Learning": ["Natural Language Processing", "Computer Vision", "Reinforcement Learning",
                      "LLM & Prompt Engineering"],
    "Data Analysis": ["Data Pipelines"],
    "Scala": ["Big Data (Spark)"],
    "Java": ["Spring Boot", "Kotlin"],
    "C#": ["ASP.NET Core"],

    "Kotlin": ["Android Development"],
    "Swift": ["iOS Development"],
    "HTML/CSS": ["Responsive Design", "Accessibility (a11y)"],
    "Ethical Hacking": ["Penetration Testing"],
    "Network Security": ["Cloud Security", "Security Compliance"],
    "OWASP Top 10": ["Cloud Security", "Security Compliance"],

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
    "Frontend Engineer": {
        "description": "Crafts high-quality, accessible, and performant user interfaces that delight users "
                        "across devices and browsers.",
        "responsibilities": "Build responsive UI components\nOptimize web performance\nEnsure accessibility standards\n"
                             "Collaborate with designers\nWrite end-to-end tests",
        "skills": {
            "JavaScript": (85, "High"), "TypeScript": (75, "High"), "React": (85, "High"),
            "HTML/CSS": (85, "High"), "Responsive Design": (75, "High"), "Vue.js": (55, "Low"),
            "Webpack": (60, "Medium"), "Accessibility (a11y)": (65, "Medium"),
            "Git": (75, "Medium"), "Unit Testing": (65, "Medium"), "End-to-End Testing": (55, "Medium"),
            "REST APIs": (65, "Medium"), "Next.js": (60, "Medium"),
        },
    },
    "Data Engineer": {
        "description": "Designs and builds the data infrastructure — pipelines, warehouses, and lakes — that "
                        "makes analytics and machine learning possible at scale.",
        "responsibilities": "Build and maintain data pipelines\nDesign data warehouses\nEnsure data quality\n"
                             "Orchestrate batch and streaming workflows\nCollaborate with data scientists",
        "skills": {
            "Python": (80, "High"), "SQL": (85, "High"), "Data Pipelines": (80, "High"),
            "Big Data (Spark)": (70, "High"), "PostgreSQL": (70, "High"),
            "Data Modeling": (75, "High"), "dbt": (60, "Medium"), "Cassandra": (45, "Low"),
            "AWS": (65, "Medium"), "Docker": (60, "Medium"), "Bash Scripting": (55, "Medium"),
            "Elasticsearch": (50, "Low"),
        },
    },
    "Site Reliability Engineer": {
        "description": "Applies software engineering to infrastructure problems to build scalable, reliable "
                        "systems — bridging development and operations.",
        "responsibilities": "Define and track SLOs/SLAs\nManage incident response\nAutomate toil elimination\n"
                             "Capacity planning\nBuild reliability tooling",
        "skills": {
            "Linux": (85, "High"), "Python": (75, "High"), "Kubernetes": (80, "High"),
            "Monitoring & Logging": (85, "High"), "CI/CD": (75, "High"), "Docker": (75, "High"),
            "AWS": (70, "Medium"), "Terraform": (65, "Medium"), "Networking": (70, "High"),
            "System Design": (70, "High"), "Bash Scripting": (65, "Medium"),
            "Helm": (60, "Medium"), "GitOps": (55, "Medium"),
        },
    },
    "AI/ML Research Engineer": {
        "description": "Bridges research and production by implementing, optimizing, and scaling "
                        "state-of-the-art machine learning models.",
        "responsibilities": "Implement research papers\nTrain large-scale models\nOptimize model inference\n"
                             "Build experiment tracking systems\nPublish findings",
        "skills": {
            "Python": (90, "High"), "Deep Learning": (85, "High"), "PyTorch": (80, "High"),
            "TensorFlow": (65, "Medium"), "Statistics": (80, "High"),
            "Natural Language Processing": (70, "High"), "Computer Vision": (65, "Medium"),
            "LLM & Prompt Engineering": (65, "Medium"), "MLOps": (60, "Medium"),
            "Data Analysis": (70, "Medium"), "Algorithms": (70, "High"),
            "Reinforcement Learning": (50, "Low"),
        },
    },
    "Blockchain Developer": {
        "description": "Designs and implements decentralized applications and smart contracts on "
                        "blockchain platforms.",
        "responsibilities": "Write and audit smart contracts\nBuild dApps\nIntegrate wallets and oracles\n"
                             "Ensure contract security\nContribute to protocol design",
        "skills": {
            "JavaScript": (75, "High"), "Python": (65, "Medium"), "Cryptography": (70, "High"),
            "Cybersecurity": (65, "High"), "REST APIs": (65, "Medium"),
            "Node.js": (60, "Medium"), "System Design": (65, "Medium"),
            "Object-Oriented Design": (60, "Medium"), "Algorithms": (65, "Medium"),
            "Git": (70, "Medium"),
        },
    },
    "Software Quality Engineer": {
        "description": "Ensures software quality through manual and automated testing, performance "
                        "testing, and continuous quality processes across the SDLC.",
        "responsibilities": "Write automated test suites\nPerform exploratory testing\nSet up QA pipelines\n"
                             "Conduct performance and load testing\nCollaborate with developers",
        "skills": {
            "Unit Testing": (80, "High"), "Test Automation": (85, "High"), "End-to-End Testing": (80, "High"),
            "Performance Testing": (70, "High"), "Debugging": (75, "High"),
            "Python": (65, "Medium"), "JavaScript": (55, "Medium"),
            "CI/CD": (65, "Medium"), "Git": (70, "Medium"),
            "REST APIs": (60, "Medium"), "Agile/Scrum": (65, "Medium"),
        },
    },
    "Solutions Architect": {
        "description": "Designs end-to-end technical solutions aligned with business goals, "
                        "guiding engineering teams and stakeholders through complex decisions.",
        "responsibilities": "Design scalable cloud architectures\nEvaluate technology trade-offs\n"
                             "Lead technical pre-sales\nCreate architecture diagrams\nMentor engineering teams",
        "skills": {
            "System Design": (90, "High"), "AWS": (85, "High"), "Microservices": (80, "High"),
            "Cloud Computing": (85, "High"), "Networking": (75, "High"),
            "API Design": (75, "High"), "Docker": (65, "Medium"), "Kubernetes": (65, "Medium"),
            "Technical Communication": (80, "High"), "Project Management": (70, "Medium"),
            "Security Compliance": (65, "Medium"), "Caching Strategies": (65, "Medium"),
            "Event-Driven Architecture": (65, "Medium"),
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
    # --- Expanded resources ---
    ("TypeScript", "TypeScript Official Handbook", "Documentation", 6, "https://www.typescriptlang.org/docs/handbook/intro.html"),
    ("Next.js", "Next.js Official Learn Course", "Tutorial", 6, "https://nextjs.org/learn"),
    ("Angular", "Angular Official Tour of Heroes", "Tutorial", 8, "https://angular.io/tutorial"),
    ("Vue.js", "Vue.js Official Guide", "Documentation", 6, "https://vuejs.org/guide/introduction.html"),
    ("GraphQL", "How to GraphQL", "Tutorial", 6, "https://www.howtographql.com/"),
    ("MongoDB", "MongoDB University (Free)", "Course", 8, "https://learn.mongodb.com/"),
    ("Redis", "Redis University", "Course", 5, "https://university.redis.com/"),
    ("Elasticsearch", "Elasticsearch Getting Started", "Documentation", 5, "https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started.html"),
    ("Deep Learning", "fast.ai Practical Deep Learning", "Course", 30, "https://course.fast.ai/"),
    ("PyTorch", "PyTorch Official Tutorials", "Documentation", 8, "https://pytorch.org/tutorials/"),
    ("TensorFlow", "TensorFlow Official Tutorials", "Documentation", 8, "https://www.tensorflow.org/tutorials"),
    ("Natural Language Processing", "Hugging Face NLP Course", "Course", 12, "https://huggingface.co/learn/nlp-course/chapter1/1"),
    ("LLM & Prompt Engineering", "Prompt Engineering Guide", "Documentation", 4, "https://www.promptingguide.ai/"),
    ("MLOps", "MLOps Zoomcamp (free)", "Course", 20, "https://github.com/DataTalksClub/mlops-zoomcamp"),
    ("Data Pipelines", "Apache Airflow Tutorial", "Documentation", 6, "https://airflow.apache.org/docs/apache-airflow/stable/tutorial/index.html"),
    ("Big Data (Spark)", "Apache Spark Official Docs", "Documentation", 10, "https://spark.apache.org/docs/latest/"),
    ("dbt", "dbt Official Learn", "Tutorial", 5, "https://learn.getdbt.com/"),
    ("Helm", "Helm Official Docs", "Documentation", 4, "https://helm.sh/docs/"),
    ("GitOps", "ArgoCD Getting Started", "Documentation", 5, "https://argo-cd.readthedocs.io/en/stable/getting_started/"),
    ("Cybersecurity", "TryHackMe — Pre-Security", "Course", 12, "https://tryhackme.com/path/outline/presecurity"),
    ("Ethical Hacking", "The Cyber Mentor — TCM Security", "Course", 20, "https://tcm-sec.com/"),
    ("OWASP Top 10", "OWASP Top Ten Project", "Documentation", 5, "https://owasp.org/www-project-top-ten/"),
    ("Cloud Security", "AWS Security Best Practices", "Documentation", 6, "https://aws.amazon.com/architecture/security-identity-compliance/"),
    ("Test Automation", "Selenium Official Docs", "Documentation", 6, "https://www.selenium.dev/documentation/"),
    ("Performance Testing", "k6 Load Testing Guide", "Documentation", 5, "https://k6.io/docs/"),
    ("Algorithms", "Visualgo — Algorithm Visualisations", "Tutorial", 8, "https://visualgo.net/en"),
    ("Data Structures", "Data Structures & Algorithms (CS50)", "Course", 10, "https://cs50.harvard.edu/x/"),
    ("Kotlin", "Kotlin Official Docs", "Documentation", 6, "https://kotlinlang.org/docs/home.html"),
    ("Swift", "Swift Official Docs", "Documentation", 6, "https://www.swift.org/documentation/"),
    ("Flutter", "Flutter Official Get Started", "Documentation", 8, "https://docs.flutter.dev/get-started/install"),
    ("Go", "A Tour of Go", "Tutorial", 5, "https://go.dev/tour/welcome/1"),
    ("Rust", "The Rust Book (free)", "Documentation", 10, "https://doc.rust-lang.org/book/"),
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
    "Git": [
        ("Which command creates a new branch and switches to it?",
         ["git branch new-branch", "git checkout -b new-branch", "git switch new-branch", "git new new-branch"],
         1, "`git checkout -b` creates and switches to a new branch."),
        ("What does `git merge` do?",
         ["Deletes a branch", "Combines the history of two branches", "Rebases commits", "Clones a repository"],
         1, "git merge integrates changes from another branch into the current branch."),
        ("What is a 'detached HEAD' state?",
         ["A corrupted repository", "HEAD pointing directly to a commit rather than a branch",
          "A branch with no commits", "A remote tracking branch"],
         1, "Detached HEAD means you checked out a specific commit, not a branch tip."),
        ("Which command stages all changed files?",
         ["git commit -a", "git add .", "git stash", "git push"],
         1, "`git add .` stages all changes in the working directory."),
        ("What does `git rebase` do?",
         ["Reverts the last commit", "Re-applies commits on top of another base commit",
          "Merges branches with a merge commit", "Pushes to a remote"],
         1, "Rebase replays commits on a new base, creating a linear history."),
    ],
    "JavaScript": [
        ("What does `===` check in JavaScript?",
         ["Value equality only", "Both value and type equality", "Reference equality only", "Logical equality"],
         1, "=== checks both value and type without coercion."),
        ("Which keyword declares a block-scoped variable?",
         ["var", "let", "function", "global"],
         1, "`let` is block-scoped; `var` is function-scoped."),
        ("What does `Array.prototype.map()` return?",
         ["The original array mutated", "A new array with each element transformed",
          "undefined", "A Promise"],
         1, "`map` returns a new array produced by calling the callback on each element."),
        ("What is a Promise in JavaScript?",
         ["A synchronous function", "An object representing the eventual completion or failure of an async operation",
          "A type of loop", "A class decorator"],
         1, "Promises represent async operations that may succeed or fail."),
        ("What does `async/await` do?",
         ["Blocks the event loop", "Allows writing asynchronous code in a synchronous style",
          "Creates web workers", "Disables error handling"],
         1, "async/await is syntactic sugar over Promises for cleaner async code."),
        ("What is the output of `typeof null`?",
         ["\"null\"", "\"undefined\"", "\"object\"", "\"boolean\""],
         2, "typeof null returns 'object' — a well-known historical quirk in JavaScript."),
    ],
    "Machine Learning": [
        ("What is overfitting in a machine learning model?",
         ["The model underfits the training data", "The model performs well on training data but poorly on unseen data",
          "The model trains too slowly", "The model uses too few parameters"],
         1, "Overfitting means the model memorizes training data and fails to generalize."),
        ("Which metric is typically used for binary classification?",
         ["Mean Squared Error", "ROC-AUC", "R-squared", "Mean Absolute Error"],
         1, "ROC-AUC measures the classifier's ability to discriminate between classes."),
        ("What does a confusion matrix show?",
         ["Model hyperparameters", "True/false positives and negatives across predicted vs actual classes",
          "Training loss over time", "Feature importance scores"],
         1, "A confusion matrix summarizes prediction results across all classes."),
        ("What is the purpose of cross-validation?",
         ["Speed up training", "Estimate model performance on unseen data by rotating train/test splits",
          "Reduce model complexity", "Increase dataset size"],
         1, "Cross-validation gives a reliable estimate of generalization performance."),
        ("What is a hyperparameter?",
         ["A learned model weight", "A configuration set before training (e.g. learning rate, depth)",
          "A type of neuron", "A normalisation layer"],
         1, "Hyperparameters are set before training and control the learning process."),
        ("Which algorithm is an ensemble of decision trees?",
         ["Linear Regression", "Support Vector Machine", "Random Forest", "K-Means"],
         2, "Random Forest combines many decision trees to reduce variance."),
    ],
    "System Design": [
        ("What does horizontal scaling mean?",
         ["Increasing a server's CPU and RAM", "Adding more servers to distribute load",
          "Optimising a single database query", "Using a faster network card"],
         1, "Horizontal scaling adds more machines; vertical scaling upgrades existing ones."),
        ("What is the primary purpose of a CDN?",
         ["Store application code", "Serve static assets from edge nodes closer to users",
          "Encrypt database connections", "Balance database writes"],
         1, "CDNs reduce latency by caching content near end users."),
        ("What does CAP theorem state?",
         ["A system can be fast, cheap, and reliable simultaneously",
          "A distributed system can guarantee at most two of: Consistency, Availability, Partition Tolerance",
          "All databases must use ACID transactions",
          "Caches always improve consistency"],
         1, "CAP theorem describes fundamental trade-offs in distributed systems."),
        ("What is sharding in databases?",
         ["Encrypting data at rest", "Splitting a dataset across multiple database nodes",
          "Creating read replicas", "Compressing table indexes"],
         1, "Sharding partitions data horizontally across multiple nodes."),
        ("What is the role of a message queue in a distributed system?",
         ["Store user sessions", "Decouple services and buffer asynchronous messages between producers and consumers",
          "Cache database query results", "Terminate TLS connections"],
         1, "Message queues enable async, decoupled communication between services."),
    ],
    "React": [
        ("What is a React component?",
         ["A CSS selector", "A reusable, self-contained piece of UI defined as a function or class",
          "A database record", "An HTTP route"],
         1, "React components are the building blocks of a React application's UI."),
        ("What does the `useState` hook do?",
         ["Fetches data from an API", "Adds local state to a functional component",
          "Creates a new component", "Handles routing"],
         1, "useState lets functional components hold and update local state."),
        ("What is the Virtual DOM?",
         ["A browser API for rendering", "A lightweight JavaScript representation of the real DOM",
          "A CSS preprocessor", "A database layer"],
         1, "React's Virtual DOM allows efficient diffing and minimal real DOM updates."),
        ("What does `useEffect` do?",
         ["Renders child components", "Runs a side effect after the component renders",
          "Defines a reducer", "Imports CSS modules"],
         1, "useEffect handles side effects like data fetching or subscriptions."),
        ("What does lifting state up mean?",
         ["Storing state in the browser localStorage", "Moving state to a common ancestor component so siblings can share it",
          "Moving state to a backend server", "Initialising state at application start"],
         1, "Lifting state lets sibling components share data through a common parent."),
    ],
    "TypeScript": [
        ("What does TypeScript add to JavaScript?",
         ["Runtime garbage collection", "Static type checking", "Built-in HTTP server", "CSS compilation"],
         1, "TypeScript adds a static type system on top of JavaScript."),
        ("What is an interface in TypeScript?",
         ["A runtime class", "A compile-time contract describing the shape of an object",
          "A function decorator", "A module system"],
         1, "Interfaces define the expected structure of objects at compile time."),
        ("What does the `any` type mean?",
         ["The variable can only be a number", "TypeScript infers the type automatically",
          "The type checker is disabled for that variable", "The variable is always undefined"],
         2, "`any` opts out of type checking — use sparingly."),
        ("What is a union type?",
         ["A type that can be one of several specific types (e.g. string | number)",
          "A type that merges two classes", "An array of mixed values", "A generic constraint"],
         0, "Union types allow a value to be one of several defined types."),
        ("What does `readonly` mean in TypeScript?",
         ["The property can only be read at runtime", "The property cannot be reassigned after initialisation",
          "The type is inferred", "The class is abstract"],
         1, "`readonly` prevents reassignment after the object is created."),
    ],
    "Cybersecurity": [
        ("What is a man-in-the-middle (MITM) attack?",
         ["Physically stealing a server", "An attacker secretly relays and possibly alters communication between two parties",
          "A SQL injection attack", "A brute-force login attempt"],
         1, "MITM attacks intercept communications between two parties without their knowledge."),
        ("What does CIA stand for in information security?",
         ["Central Intelligence Agency", "Confidentiality, Integrity, Availability",
          "Code Injection Attack", "Certificate Identity Authority"],
         1, "The CIA triad is the foundational model for information security."),
        ("What is phishing?",
         ["A network port scanner", "A social engineering attack that tricks users into revealing credentials",
          "A type of encryption", "A firewall bypass technique"],
         1, "Phishing uses deceptive messages to steal sensitive information."),
        ("What is the principle of least privilege?",
         ["Admins have unrestricted access", "Users and processes should have only the minimum permissions they need",
          "All traffic is encrypted", "Passwords are hashed with SHA-256"],
         1, "Least privilege limits damage from compromised accounts or bugs."),
        ("What does multi-factor authentication (MFA) provide?",
         ["Faster login", "An extra layer of security by requiring a second verification factor",
          "Automatic password reset", "SSO across applications"],
         1, "MFA requires something you know plus something you have or are."),
    ],
    "Data Analysis": [
        ("What is the purpose of exploratory data analysis (EDA)?",
         ["To deploy a model to production", "To understand data distributions, patterns, and anomalies before modelling",
          "To clean the database", "To write SQL queries"],
         1, "EDA helps you understand your dataset before applying models."),
        ("What does a box plot show?",
         ["A time series trend", "The median, quartiles, and outliers of a distribution",
          "Correlation between two variables", "Feature importance"],
         1, "Box plots summarise distribution via median, IQR, and outliers."),
        ("What is the difference between correlation and causation?",
         ["They are the same thing",
          "Correlation shows a statistical relationship; causation proves one variable causes another",
          "Causation is weaker than correlation", "Correlation requires a controlled experiment"],
         1, "Correlation does not imply causation — confounders can create spurious links."),
        ("Which measure is robust to outliers?",
         ["Mean", "Median", "Standard Deviation", "Variance"],
         1, "The median is not affected by extreme values the way mean is."),
        ("What is data wrangling?",
         ["Visualising data in charts", "Cleaning and transforming raw data into a usable format",
          "Training a model", "Deploying a dashboard"],
         1, "Data wrangling (munging) prepares raw data for analysis."),
    ],
}

# ---------------------------------------------------------------------------
# Skill aliases — for resume/skill extraction matching
# ---------------------------------------------------------------------------
ALIASES = [
    # (canonical_skill_name, alias_string)
    ("PostgreSQL", "Postgres"),
    ("PostgreSQL", "pg"),
    ("MongoDB", "Mongo"),
    ("JavaScript", "JS"),
    ("TypeScript", "TS"),
    ("Python", "py"),
    ("Kubernetes", "K8s"),
    ("Kubernetes", "k8s"),
    ("Docker", "containerization"),
    ("CI/CD", "Continuous Integration"),
    ("CI/CD", "Continuous Deployment"),
    ("CI/CD", "GitHub Actions"),
    ("CI/CD", "Jenkins"),
    ("CI/CD", "GitLab CI"),
    ("Machine Learning", "ML"),
    ("Deep Learning", "DL"),
    ("Natural Language Processing", "NLP"),
    ("Natural Language Processing", "text processing"),
    ("Computer Vision", "CV"),
    ("LLM & Prompt Engineering", "LLM"),
    ("LLM & Prompt Engineering", "prompt engineering"),
    ("LLM & Prompt Engineering", "GPT"),
    ("LLM & Prompt Engineering", "ChatGPT"),
    ("AWS", "Amazon Web Services"),
    ("Google Cloud Platform", "GCP"),
    ("Google Cloud Platform", "Google Cloud"),
    ("Azure", "Microsoft Azure"),
    ("Big Data (Spark)", "Apache Spark"),
    ("Big Data (Spark)", "Spark"),
    ("REST APIs", "RESTful APIs"),
    ("REST APIs", "REST"),
    ("GraphQL", "GQL"),
    ("React", "ReactJS"),
    ("React", "React.js"),
    ("Vue.js", "Vue"),
    ("Angular", "AngularJS"),
    ("Node.js", "NodeJS"),
    ("Express.js", "Express"),
    ("Next.js", "NextJS"),
    ("Flask", "Python Flask"),
    ("Django", "Python Django"),
    ("Spring Boot", "Spring"),
    ("Elasticsearch", "Elastic"),
    ("Elasticsearch", "ELK"),
    ("Monitoring & Logging", "Prometheus"),
    ("Monitoring & Logging", "Grafana"),
    ("Monitoring & Logging", "ELK Stack"),
    ("Test Automation", "Selenium"),
    ("Test Automation", "Playwright"),
    ("Test Automation", "Cypress"),
    ("Agile/Scrum", "Scrum"),
    ("Agile/Scrum", "Agile"),
    ("Git", "version control"),
    ("HTML/CSS", "HTML"),
    ("HTML/CSS", "CSS"),
    ("Data Visualization", "Tableau"),
    ("Data Visualization", "PowerBI"),
    ("Data Visualization", "matplotlib"),
    ("Data Visualization", "seaborn"),
    ("MLOps", "ML Ops"),
    ("Helm", "Helm charts"),
    ("GitOps", "ArgoCD"),
    ("GitOps", "Flux"),
    ("Service Mesh", "Istio"),
    ("Service Mesh", "Linkerd"),
    ("Message Queues", "Kafka"),
    ("Message Queues", "RabbitMQ"),
    ("Message Queues", "SQS"),
    ("Caching Strategies", "Redis caching"),
    ("Caching Strategies", "CDN"),
    ("dbt", "data build tool"),
    ("Data Pipelines", "ETL"),
    ("Data Pipelines", "ELT"),
    ("Data Pipelines", "Apache Airflow"),
    ("Performance Testing", "load testing"),
    ("Performance Testing", "k6"),
    ("End-to-End Testing", "E2E testing"),
    ("End-to-End Testing", "Cypress"),
    ("Security Compliance", "SOC 2"),
    ("Security Compliance", "ISO 27001"),
    ("Security Compliance", "GDPR"),
]

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


# ---------------------------------------------------------------------------
# Additive patch — inserts NEW skills / careers / aliases / assessments into
# an already-populated database without touching any existing records.
# Safe to run multiple times (all inserts are guarded by existence checks).
# ---------------------------------------------------------------------------

def _patch_skills(db, skill_objs: dict):
    """Insert new skills from SKILLS that are not already in the DB."""
    existing_names = {s.name for s in db.query(models.Skill).all()}
    added = 0
    for name, category in SKILLS.items():
        if name in existing_names:
            continue
        skill = models.Skill(
            name=name, category=category,
            description=f"{name} is a core competency in the {category} category.",
            difficulty=DIFFICULTY_OVERRIDES.get(name, "Intermediate"),
        )
        db.add(skill)
        skill_objs[name] = skill
        added += 1
    if added:
        db.flush()
    print(f"Patch: added {added} new skills.")
    return skill_objs


def _patch_dependencies(db, skill_objs: dict):
    """Insert new dependency edges that don't already exist."""
    from sqlalchemy import and_
    added = 0
    for prereq_name, unlocks in DEPENDENCIES.items():
        prereq = skill_objs.get(prereq_name)
        if not prereq:
            continue
        for unlocked_name in unlocks:
            unlocked = skill_objs.get(unlocked_name)
            if not unlocked:
                continue
            exists = db.query(models.SkillDependency).filter(
                and_(
                    models.SkillDependency.skill_id == unlocked.id,
                    models.SkillDependency.prerequisite_skill_id == prereq.id,
                )
            ).first()
            if not exists:
                db.add(models.SkillDependency(
                    skill_id=unlocked.id, prerequisite_skill_id=prereq.id
                ))
                added += 1
    print(f"Patch: added {added} new skill dependency edges.")


def _patch_aliases(db, skill_objs: dict):
    """Insert skill aliases that don't already exist."""
    existing_aliases = {a.alias for a in db.query(models.SkillAlias).all()}
    added = 0
    for skill_name, alias_str in ALIASES:
        skill = skill_objs.get(skill_name)
        if not skill:
            continue
        if alias_str in existing_aliases:
            continue
        db.add(models.SkillAlias(skill_id=skill.id, alias=alias_str))
        existing_aliases.add(alias_str)
        added += 1
    print(f"Patch: added {added} new skill aliases.")


def _patch_careers(db, skill_objs: dict):
    """Insert new careers and their career-skill mappings."""
    existing_career_names = {c.name for c in db.query(models.Career).all()}
    career_objs = {c.name: c for c in db.query(models.Career).all()}
    careers_added = 0
    mappings_added = 0
    for name, data in CAREERS.items():
        if name in existing_career_names:
            continue
        career = models.Career(
            name=name,
            description=data["description"],
            responsibilities=data["responsibilities"],
        )
        db.add(career)
        career_objs[name] = career
        careers_added += 1
    if careers_added:
        db.flush()
    # Now add career-skill mappings for newly-added careers only
    for name, data in CAREERS.items():
        career = career_objs.get(name)
        if not career:
            continue
        if name in existing_career_names:
            continue  # skip careers that already existed
        for skill_name, (level, importance) in data["skills"].items():
            skill = skill_objs.get(skill_name)
            if not skill:
                continue
            db.add(models.CareerSkill(
                career_id=career.id, skill_id=skill.id,
                required_level=level, importance=importance, is_required=True,
            ))
            mappings_added += 1
    print(f"Patch: added {careers_added} new careers and {mappings_added} career-skill mappings.")


def _patch_assessments(db, skill_objs: dict):
    """Insert assessments for skills that don't yet have one."""
    existing_assessed_skill_ids = {a.skill_id for a in db.query(models.Assessment).all()}
    added_assessments = 0
    added_questions = 0
    for skill_name, questions in ASSESSMENTS.items():
        skill = skill_objs.get(skill_name)
        if not skill:
            continue
        if skill.id in existing_assessed_skill_ids:
            continue  # already has an assessment
        assessment = models.Assessment(
            skill_id=skill.id,
            title=f"{skill_name} Fundamentals Assessment",
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
            added_questions += 1
        added_assessments += 1
    print(f"Patch: added {added_assessments} new assessments with {added_questions} questions.")


def patch():
    """Additive patch — safe to run against an already-populated database.
    Only inserts records that are not already present. Never deletes or modifies.
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        skill_objs = {s.name: s for s in db.query(models.Skill).all()}
        skill_objs = _patch_skills(db, skill_objs)
        # Reload to include newly added skills
        skill_objs = {s.name: s for s in db.query(models.Skill).all()}
        _patch_dependencies(db, skill_objs)
        _patch_aliases(db, skill_objs)
        _patch_careers(db, skill_objs)
        _patch_assessments(db, skill_objs)
        db.commit()
        print("Dataset patch complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    patch()
