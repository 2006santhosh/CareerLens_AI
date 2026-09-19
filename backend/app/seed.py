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
        # --- existing 10 questions ---
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
        # --- new questions to reach 15 ---
        ("What is a Docker image?",
         ["A running process", "A read-only template used to create containers", "A network namespace", "A persistent disk volume"],
         1, "Images are read-only templates; containers are running instances of images."),
        ("Which command removes a stopped container?",
         ["docker stop", "docker rm", "docker rmi", "docker prune"],
         1, "`docker rm` removes stopped containers; `docker rmi` removes images."),
        ("What does the `docker pull` command do?",
         ["Pushes a local image to a registry", "Downloads an image from a registry to the local machine",
          "Runs a container from an image", "Lists available images"],
         1, "`docker pull` fetches an image from a registry such as Docker Hub."),
        ("How do you pass an environment variable to a container at runtime?",
         ["docker run --env VAR=value", "docker run --set VAR=value", "docker run --arg VAR=value", "docker run --config VAR=value"],
         0, "The -e / --env flag sets environment variables inside the running container."),
        ("What is the difference between CMD and ENTRYPOINT in a Dockerfile?",
         ["They are identical",
          "ENTRYPOINT sets the executable; CMD provides default arguments that can be overridden",
          "CMD sets the executable; ENTRYPOINT provides the image tag",
          "ENTRYPOINT is only for base images"],
         1, "ENTRYPOINT defines the main process; CMD supplies overridable default arguments."),
    ],
    "Linux": [
        # --- existing 8 questions ---
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
        # --- new questions to reach 15 ---
        ("Which command shows the last 20 lines of a file in real-time?",
         ["head -20", "tail -f", "cat -n", "less -20"],
         1, "`tail -f` follows the file and streams new lines in real-time."),
        ("What does the `crontab -e` command do?",
         ["Deletes all scheduled jobs", "Opens the cron table editor to schedule recurring tasks",
          "Runs all cron jobs immediately", "Lists currently running services"],
         1, "`crontab -e` opens the user's cron table for editing scheduled jobs."),
        ("Which command searches for a file by name recursively?",
         ["locate -r", "find / -name filename", "search filename", "ls -R | grep filename"],
         1, "`find / -name` recursively searches the filesystem for a file by name."),
        ("What does `top` display?",
         ["A list of installed packages", "Real-time CPU, memory, and process information",
          "Network interface statistics", "Open file handles"],
         1, "`top` shows a live, dynamic view of system resource usage."),
        ("What is a symbolic link in Linux?",
         ["A copy of a file", "A pointer (shortcut) to another file or directory",
          "A compressed archive", "A mounted filesystem"],
         1, "A symbolic link (symlink) is a file that points to another file or directory path."),
        ("Which command shows the manual page for a command?",
         ["help", "man", "info -v", "cmd --manual"],
         1, "`man <command>` displays the manual page for that command."),
        ("What does the pipe operator `|` do?",
         ["Appends output to a file", "Sends the output of one command as input to another",
          "Runs two commands in parallel", "Redirects stderr"],
         1, "The pipe `|` chains commands by feeding stdout of one into stdin of the next."),
    ],
    "Python": [
        # --- existing 6 questions ---
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
        # --- new questions to reach 15 ---
        ("What does the `with` statement ensure in Python file handling?",
         ["The file is opened read-only", "The file is properly closed after the block exits, even if an exception occurs",
          "The file is locked for exclusive access", "The file is written asynchronously"],
         1, "`with` uses context managers to guarantee resource cleanup."),
        ("What is the difference between a list and a tuple?",
         ["Lists are immutable; tuples are mutable", "Tuples are immutable; lists are mutable",
          "They are identical", "Tuples can only hold integers"],
         1, "Lists are mutable (changeable); tuples are immutable (fixed after creation)."),
        ("What does the `*args` syntax in a function signature do?",
         ["Passes a dictionary of arguments", "Collects any number of positional arguments into a tuple",
          "Unpacks a list", "Declares optional keyword arguments"],
         1, "`*args` collects extra positional arguments as a tuple."),
        ("Which built-in function returns the length of a sequence?",
         ["size()", "count()", "len()", "length()"],
         2, "`len()` returns the number of items in a sequence."),
        ("What does `enumerate()` do?",
         ["Sorts an iterable", "Returns pairs of (index, value) for each item in an iterable",
          "Removes duplicates from a list", "Converts a string to a list of characters"],
         1, "`enumerate()` yields (index, item) pairs, useful in for-loops."),
        ("How do you handle exceptions in Python?",
         ["using `catch` / `handle`", "using `try` / `except`", "using `if` / `elif`", "using `rescue` / `retry`"],
         1, "Python uses `try` / `except` blocks to catch and handle exceptions."),
        ("What is a Python decorator?",
         ["A comment style for documentation", "A function that wraps another function to modify its behaviour",
          "A type annotation", "A way to define class attributes"],
         1, "Decorators wrap functions to add or modify behaviour without changing the original code."),
        ("What does `__init__` do in a Python class?",
         ["Deletes the object", "Initialises instance attributes when an object is created",
          "Defines class-level constants", "Imports the class module"],
         1, "`__init__` is the constructor that initialises a new instance's attributes."),
        ("What is the output of `bool([])` in Python?",
         ["True", "False", "None", "Error"],
         1, "An empty list is falsy; `bool([])` returns `False`."),
    ],
    "AWS": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What is an AWS VPC?",
         ["A virtual private server", "A logically isolated section of the AWS cloud where you launch resources",
          "A virtual file system", "A caching layer"],
         1, "A VPC lets you define a private, isolated network within AWS."),
        ("What does Amazon CloudFront provide?",
         ["Relational database hosting", "A global content delivery network (CDN)",
          "Serverless function execution", "Container orchestration"],
         1, "CloudFront is AWS's CDN, caching content at edge locations worldwide."),
        ("What is the purpose of AWS Auto Scaling?",
         ["Automatically replicating databases", "Automatically adjusting compute capacity based on demand",
          "Compressing S3 objects", "Encrypting EBS volumes"],
         1, "Auto Scaling adds or removes instances to match workload demand."),
        ("Which AWS service is a managed NoSQL database?",
         ["Aurora", "DynamoDB", "ElastiCache", "Neptune"],
         1, "DynamoDB is AWS's fully managed, serverless NoSQL database."),
        ("What is AWS Route 53 used for?",
         ["Load balancing EC2 instances", "DNS and domain name management",
          "CDN caching", "Object storage"],
         1, "Route 53 is AWS's scalable DNS and domain name registration service."),
        ("What is the difference between S3 Standard and S3 Glacier?",
         ["Glacier is faster but more expensive",
          "Standard offers frequent access; Glacier is low-cost archival storage",
          "They are identical", "Standard is only for images"],
         1, "Glacier is designed for infrequently accessed data and long-term archival."),
        ("What does an Elastic Load Balancer (ELB) do?",
         ["Scales databases horizontally", "Distributes incoming traffic across multiple targets",
          "Compresses outbound traffic", "Manages SSL certificates"],
         1, "ELB distributes traffic across multiple compute targets for availability."),
        ("Which AWS service provides managed container orchestration?",
         ["ECS / EKS", "EC2", "S3", "Lambda"],
         0, "ECS (Elastic Container Service) and EKS (Elastic Kubernetes Service) manage containers."),
        ("What is an AWS Security Group?",
         ["A group of IAM users", "A virtual firewall that controls inbound and outbound traffic to resources",
          "A billing grouping mechanism", "A monitoring dashboard"],
         1, "Security groups act as stateful virtual firewalls for EC2 instances and other resources."),
        ("What does CloudWatch monitor?",
         ["Source code repositories", "AWS resources and applications — metrics, logs, alarms",
          "DNS resolution", "Database schemas"],
         1, "CloudWatch collects metrics and logs, and triggers alarms for AWS resources."),
    ],
    "CI/CD": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What does 'CD' stand for in CI/CD?",
         ["Code Delivery", "Continuous Deployment or Continuous Delivery", "Container Daemon", "Cloud Distribution"],
         1, "CD stands for Continuous Delivery (automated release-ready) or Continuous Deployment (auto-deploy)."),
        ("What is a pipeline stage?",
         ["A database transaction", "A distinct phase in a CI/CD pipeline such as build, test, or deploy",
          "A version control branch", "A monitoring alert"],
         1, "Stages partition a pipeline into logical phases executed in sequence."),
        ("What triggers a CI pipeline to run?",
         ["A scheduled database backup", "A code push or pull request to the repository",
          "A manual server restart", "A DNS update"],
         1, "CI pipelines typically trigger on git push or pull request events."),
        ("What is the purpose of environment variables in a CI/CD pipeline?",
         ["To define the programming language", "To securely inject secrets and configuration without hardcoding them",
          "To specify the build server's IP", "To list test files"],
         1, "Environment variables keep secrets and config out of source code."),
        ("What does a 'deployment rollback' mean in CD?",
         ["Pushing a new feature to production", "Reverting to a previous stable version when a deployment fails",
          "Deleting the deployment pipeline", "Running tests on a branch"],
         1, "A rollback restores the previous good deployment when the new one fails."),
        ("Which strategy deploys a new version alongside the old one and shifts traffic gradually?",
         ["Big bang deployment", "Blue/green or canary deployment", "Hotfix deployment", "Rolling wipe"],
         1, "Blue/green and canary deployments shift traffic gradually to reduce risk."),
        ("What is a 'pipeline as code' approach?",
         ["Writing pipeline config in a GUI", "Defining CI/CD pipeline steps in a version-controlled file (e.g. YAML)",
          "Storing build logs in a database", "Running pipelines manually via CLI only"],
         1, "Pipeline-as-code stores pipeline definitions in source control alongside the application."),
        ("What is the main benefit of parallelising pipeline jobs?",
         ["Reduces code complexity", "Shortens overall pipeline execution time",
          "Increases security", "Reduces artifact size"],
         1, "Running jobs in parallel reduces total wall-clock time of the pipeline."),
        ("What does a linting step in CI check?",
         ["Server resource usage", "Code style, syntax errors, and common mistakes",
          "Database migrations", "Container image sizes"],
         1, "Linting enforces code style rules and catches syntax or logic errors early."),
        ("What is the purpose of caching dependencies in a CI pipeline?",
         ["To persist test results", "To avoid re-downloading packages on every run and speed up builds",
          "To encrypt build artifacts", "To deploy faster to production"],
         1, "Caching node_modules, pip packages, etc. dramatically reduces build times."),
    ],
    "SQL": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What is the difference between INNER JOIN and LEFT JOIN?",
         ["They are identical",
          "INNER JOIN returns only matching rows; LEFT JOIN returns all left-table rows with NULLs for unmatched right-table rows",
          "LEFT JOIN is faster", "INNER JOIN returns all rows from both tables"],
         1, "INNER JOIN: matched rows only. LEFT JOIN: all left rows, NULLs where no match."),
        ("What does the HAVING clause do?",
         ["Filters individual rows", "Filters groups after aggregation (used with GROUP BY)",
          "Sorts aggregated results", "Joins two tables"],
         1, "HAVING filters aggregated results, like WHERE does for individual rows."),
        ("What is a foreign key?",
         ["A unique column in a table", "A column that references the primary key of another table to enforce referential integrity",
          "An encrypted column", "A column with a default value"],
         1, "A foreign key links rows across tables and ensures referenced records exist."),
        ("What does a SQL index do?",
         ["Sorts data alphabetically", "Speeds up data retrieval by creating a fast lookup structure",
          "Prevents duplicate rows", "Encrypts a column"],
         1, "Indexes let the database engine find rows faster without scanning the whole table."),
        ("What is a subquery?",
         ["A stored procedure", "A query nested inside another query",
          "A database view", "A join alias"],
         1, "A subquery is a SELECT statement embedded within another SQL statement."),
        ("Which aggregate function returns the number of rows?",
         ["SUM()", "AVG()", "COUNT()", "MAX()"],
         2, "COUNT() returns the number of rows matching the query condition."),
        ("What does the DISTINCT keyword do?",
         ["Sorts results", "Removes duplicate values from the result set",
          "Creates a unique index", "Aliases a column name"],
         1, "DISTINCT filters out duplicate rows from the query result."),
        ("What is a SQL transaction?",
         ["A database backup", "A sequence of operations treated as a single unit that either all succeed or all fail",
          "A scheduled query", "A view definition"],
         1, "Transactions ensure ACID properties: all operations commit or all roll back."),
        ("What does the COALESCE function return?",
         ["The maximum value", "The first non-NULL value from its list of arguments",
          "The count of NULL values", "A concatenated string"],
         1, "COALESCE returns the first non-NULL argument — useful for handling NULLs."),
        ("What is a database view?",
         ["A physical table copy", "A virtual table defined by a stored SELECT query",
          "A cached query result", "A backup snapshot"],
         1, "A view is a named query stored in the database, queryable like a table."),
    ],
    "Git": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What does `git stash` do?",
         ["Permanently deletes uncommitted changes", "Temporarily shelves uncommitted changes so you can work on something else",
          "Commits changes to a new branch", "Pushes changes to the remote"],
         1, "`git stash` saves dirty working directory state and reverts to HEAD."),
        ("What is `git cherry-pick` used for?",
         ["Undoing the last commit", "Applying a specific commit from one branch onto another",
          "Listing all commits", "Merging two branches"],
         1, "Cherry-pick applies a specific commit to the current branch without merging."),
        ("What does `git log --oneline` show?",
         ["Only uncommitted files", "A compact one-line-per-commit summary of the commit history",
          "Remote branch status", "Staged changes"],
         1, "`--oneline` shows abbreviated hashes and commit messages one per line."),
        ("How do you undo the last commit but keep the changes staged?",
         ["git reset --hard HEAD~1", "git reset --soft HEAD~1", "git revert HEAD", "git checkout HEAD~1"],
         1, "`--soft` moves HEAD back but keeps changes in the staging area."),
        ("What is a pull request (PR)?",
         ["A request to download the repository", "A proposal to merge changes from one branch into another, enabling code review",
          "A command to fetch remote changes", "A git config setting"],
         1, "Pull requests are the collaboration mechanism for code review and merging."),
        ("What does `git fetch` do compared to `git pull`?",
         ["They are identical",
          "fetch downloads remote changes without merging; pull downloads and merges",
          "pull only downloads; fetch also merges",
          "fetch deletes remote branches"],
         1, "`git fetch` retrieves but does not merge; `git pull` = fetch + merge."),
        ("What is `.gitignore` used for?",
         ["Listing collaborators", "Specifying files and patterns that Git should not track",
          "Storing commit messages", "Configuring the remote URL"],
         1, ".gitignore tells Git which files (e.g. build outputs, secrets) to ignore."),
        ("What does a merge conflict indicate?",
         ["A broken network connection", "Two branches made conflicting changes to the same part of a file",
          "An invalid commit message", "A missing remote branch"],
         1, "Merge conflicts occur when two branches edit the same lines differently."),
        ("What does `git tag` create?",
         ["A new branch", "A named reference to a specific commit, often used to mark releases",
          "A remote alias", "A commit message template"],
         1, "Tags are immutable pointers to commits, commonly used for versioned releases."),
        ("What is a 'git blame' command used for?",
         ["Reverting bad commits", "Showing which commit and author last modified each line of a file",
          "Listing untracked files", "Viewing the reflog"],
         1, "`git blame` annotates each line with the commit and author that last changed it."),
    ],
    "JavaScript": [
        # --- existing 6 questions ---
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
        # --- new questions to reach 15 ---
        ("What does `Array.prototype.filter()` return?",
         ["The first matching element", "A new array containing only elements that pass a test",
          "A count of matching elements", "A modified original array"],
         1, "`filter` returns a new array of elements for which the callback returns true."),
        ("What is closure in JavaScript?",
         ["A way to end a function early", "A function that retains access to its outer scope's variables even after the outer function returns",
          "An IIFE pattern", "A module import syntax"],
         1, "Closures allow inner functions to access outer scope variables after the outer function has returned."),
        ("What is event bubbling?",
         ["A network error pattern", "An event propagating from the target element up through its ancestors",
          "A CSS animation technique", "A Promise rejection pattern"],
         1, "Events bubble up the DOM tree from the target to the root by default."),
        ("What does the spread operator `...` do?",
         ["Creates a generator", "Expands an iterable into individual elements",
          "Declares a rest parameter", "Imports a module"],
         1, "The spread operator unpacks arrays or objects into individual elements."),
        ("What is the difference between `null` and `undefined`?",
         ["They are identical",
          "null is an intentional absence of value; undefined means a variable has been declared but not assigned",
          "undefined is set by the programmer; null is set by the engine",
          "null is a number type"],
         1, "null = intentional empty value; undefined = not yet assigned."),
        ("What does `Array.prototype.reduce()` do?",
         ["Removes the last element", "Accumulates array elements into a single output value",
          "Sorts the array", "Flattens nested arrays"],
         1, "`reduce` applies a function cumulatively across array elements to produce one value."),
        ("What is the purpose of `localStorage` in the browser?",
         ["Server-side session management", "Persisting key-value data in the browser with no expiry",
          "Caching network requests", "Managing cookies"],
         1, "`localStorage` stores data in the browser with no expiration time."),
        ("What does `Object.keys()` return?",
         ["An array of an object's values", "An array of an object's own enumerable property names",
          "A count of properties", "A JSON string"],
         1, "`Object.keys()` returns an array of the object's own enumerable string keys."),
        ("What is the event loop in JavaScript?",
         ["A CSS animation loop", "The mechanism that allows JavaScript to perform non-blocking I/O by offloading operations and processing callbacks in a queue",
          "A for-loop optimisation", "A DOM traversal method"],
         1, "The event loop processes the callback queue when the call stack is empty, enabling async JS."),
    ],
    "Machine Learning": [
        # --- existing 6 questions ---
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
        # --- new questions to reach 15 ---
        ("What is underfitting?",
         ["The model is too complex", "The model is too simple to capture patterns in the data",
          "The model trains too slowly", "The model has too many features"],
         1, "Underfitting means the model lacks the capacity to learn the underlying patterns."),
        ("What is the bias-variance tradeoff?",
         ["A tradeoff between CPU and RAM", "Balancing model simplicity (bias) against sensitivity to training data (variance) to minimise total error",
          "A tradeoff between accuracy and speed", "A method for choosing learning rate"],
         1, "High bias = underfitting; high variance = overfitting; the tradeoff seeks a balance."),
        ("What is gradient descent?",
         ["A method for cleaning data", "An optimisation algorithm that iteratively moves toward the minimum of a loss function",
          "A clustering technique", "A dimensionality reduction method"],
         1, "Gradient descent updates parameters in the direction that reduces the loss function."),
        ("What is the purpose of a training/validation/test split?",
         ["To increase dataset size", "Training fits the model; validation tunes hyperparameters; test gives an unbiased final evaluation",
          "To speed up training", "To remove outliers"],
         1, "The three-way split prevents data leakage and provides an honest evaluation."),
        ("What is feature scaling and why is it important?",
         ["Removing irrelevant features", "Normalising feature ranges so gradient-based algorithms converge faster",
          "Adding polynomial features", "Encoding categorical variables"],
         1, "Scaling (e.g. min-max, standardisation) ensures no feature dominates due to magnitude."),
        ("What type of problem is predicting house prices?",
         ["Classification", "Regression", "Clustering", "Reinforcement learning"],
         1, "Predicting a continuous numeric output is a regression problem."),
        ("What is Principal Component Analysis (PCA) used for?",
         ["Classification", "Dimensionality reduction by projecting data onto principal components",
          "Model ensembling", "Hyperparameter tuning"],
         1, "PCA reduces dimensionality while retaining maximum variance in the data."),
        ("What is regularisation in machine learning?",
         ["Normalising input features", "Adding a penalty term to the loss function to reduce overfitting",
          "Augmenting the dataset", "Scaling model outputs"],
         1, "L1 (Lasso) and L2 (Ridge) regularisation penalise large weights to reduce overfitting."),
        ("What does K-Means clustering do?",
         ["Classifies labelled data", "Groups unlabelled data into K clusters by minimising intra-cluster distance",
          "Predicts a target value", "Reduces feature dimensions"],
         1, "K-Means partitions data into K clusters, assigning each point to its nearest centroid."),
    ],
    "System Design": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What is a load balancer?",
         ["A database optimiser", "A component that distributes incoming requests across multiple servers",
          "A caching layer", "A message broker"],
         1, "Load balancers spread traffic to improve availability and throughput."),
        ("What is caching and why is it used in system design?",
         ["Compressing data for storage", "Storing frequently accessed data in fast memory to reduce latency and database load",
          "Replicating data across regions", "Encrypting data in transit"],
         1, "Caching (e.g. Redis, Memcached) reduces expensive repeated computation or DB queries."),
        ("What is eventual consistency?",
         ["All nodes return the same data immediately after a write",
          "Given enough time without updates, all nodes will converge to the same value",
          "Data is always written to all nodes before confirming",
          "Only the primary node is consistent"],
         1, "Eventual consistency trades immediate consistency for availability and partition tolerance."),
        ("What is a microservices architecture?",
         ["A single large application", "An architecture where the application is composed of small, independently deployable services",
          "A type of database schema", "A load balancing strategy"],
         1, "Microservices break an application into small services that communicate over APIs."),
        ("What is rate limiting?",
         ["Capping database connections", "Restricting the number of requests a client can make in a time window",
          "Compressing API responses", "Scaling servers automatically"],
         1, "Rate limiting protects services from abuse and overload."),
        ("What does API Gateway do in a microservices system?",
         ["Stores API documentation", "Acts as a single entry point for clients, routing requests to appropriate services",
          "Manages database migrations", "Encrypts inter-service traffic"],
         1, "An API gateway handles routing, auth, rate-limiting, and aggregation at the edge."),
        ("What is a database read replica?",
         ["A backup snapshot", "A copy of the primary database that handles read traffic to reduce load",
          "A sharded database node", "A distributed cache"],
         1, "Read replicas offload SELECT queries from the primary, improving read scalability."),
        ("What is the two-phase commit protocol?",
         ["A UI rendering strategy", "A distributed transaction protocol ensuring all nodes either commit or abort",
          "A replication technique", "A consensus algorithm"],
         1, "2PC coordinates distributed transactions so all participants agree to commit or roll back."),
        ("What is a circuit breaker pattern?",
         ["A load balancing algorithm", "A pattern that stops calling a failing service and returns a fallback to prevent cascading failures",
          "A database replication strategy", "A caching invalidation technique"],
         1, "Circuit breakers detect failures and prevent repeated calls to degraded services."),
        ("What is back-pressure in a distributed system?",
         ["Network compression", "A flow-control mechanism where a downstream service signals it is overwhelmed so upstream slows down",
          "A database index rebuild", "An SSL handshake delay"],
         1, "Back-pressure prevents buffer overflow by propagating overload signals upstream."),
    ],
    "React": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What does the `key` prop do in a list of React elements?",
         ["Applies CSS styling", "Helps React identify which items have changed, added, or removed",
          "Sorts the list", "Binds an event handler"],
         1, "Keys help React's reconciler efficiently update lists by tracking identity."),
        ("What is prop drilling?",
         ["Removing unused props", "Passing props through many layers of components to reach a deeply nested child",
          "Destructuring props", "Validating prop types"],
         1, "Prop drilling becomes painful with deep trees; Context API solves it."),
        ("What does `React.memo` do?",
         ["Memoises the entire component tree", "Prevents a functional component from re-rendering if its props haven't changed",
          "Caches API responses", "Creates a memo list"],
         1, "`React.memo` is a higher-order component that skips re-renders when props are unchanged."),
        ("What is the Context API used for?",
         ["Making API calls", "Sharing state across the component tree without prop drilling",
          "Styling components", "Routing between pages"],
         1, "Context provides a way to pass values to any component without explicitly threading props."),
        ("What is `useReducer` used for?",
         ["Fetching data", "Managing complex state transitions with a reducer function",
          "Caching computed values", "Running side effects"],
         1, "`useReducer` is preferable over `useState` when state logic is complex."),
        ("What does `useMemo` optimise?",
         ["Network requests", "Expensive computations by caching the result until dependencies change",
          "Component mounting", "Event listeners"],
         1, "`useMemo` caches a computed value, recomputing only when dependencies change."),
        ("What is React Router used for?",
         ["State management", "Client-side navigation between pages in a React application",
          "API data fetching", "Component styling"],
         1, "React Router maps URL paths to components for client-side navigation."),
        ("What is the difference between controlled and uncontrolled components?",
         ["Controlled components use Redux; uncontrolled use Context",
          "Controlled components have their form state managed by React; uncontrolled rely on the DOM",
          "Uncontrolled components are class-based",
          "They are the same"],
         1, "Controlled: React state drives the input value. Uncontrolled: the DOM holds the state."),
        ("What is code splitting in React?",
         ["Splitting CSS into modules", "Lazily loading parts of the application bundle to improve initial load time",
          "Dividing a component into subcomponents", "Separating business logic from UI"],
         1, "Code splitting with React.lazy / Suspense loads chunks only when needed."),
        ("What does the `useCallback` hook do?",
         ["Runs a callback on mount", "Memoises a function reference so it is not recreated on every render",
          "Cancels an async operation", "Creates a context consumer"],
         1, "`useCallback` returns a stable function reference, preventing unnecessary child re-renders."),
    ],
    "TypeScript": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What is a TypeScript generic?",
         ["A default export", "A type placeholder that makes functions or classes work with multiple types",
          "A runtime type check", "A decorator factory"],
         1, "Generics (e.g. `Array<T>`) allow reusable, type-safe code for different types."),
        ("What does the `unknown` type mean?",
         ["The variable is always undefined", "A type-safe alternative to `any` that requires a type check before use",
          "An unresolved import", "A generic constraint"],
         1, "`unknown` is safer than `any` because you must narrow the type before using it."),
        ("What is a type assertion in TypeScript?",
         ["Automatic type inference", "Telling the TypeScript compiler to treat a value as a specific type",
          "A runtime type guard", "A decorator"],
         1, "Type assertions (e.g. `as string`) override the inferred type — use carefully."),
        ("What is an enum in TypeScript?",
         ["A runtime error type", "A set of named constants representing a fixed set of values",
          "A mapped type", "An optional property"],
         1, "Enums define a set of named constants, making intent clear and code readable."),
        ("What does the `Partial<T>` utility type do?",
         ["Makes all properties required", "Makes all properties of T optional",
          "Makes all properties readonly", "Picks a subset of properties"],
         1, "`Partial<T>` constructs a type with all properties of T set to optional."),
        ("What is a type guard?",
         ["A type alias for null", "A runtime check that narrows a variable's type within a code block",
          "A readonly modifier", "A generic constraint"],
         1, "Type guards (e.g. typeof, instanceof, custom predicates) narrow types at runtime."),
        ("What is the `never` type used for?",
         ["Variables that have no value yet", "Values that never occur, such as the return type of a function that always throws",
          "Empty arrays", "Optional function parameters"],
         1, "`never` represents values that should never exist, used in exhaustive checks and throws."),
        ("What does `Record<K, V>` represent?",
         ["An array of key-value pairs", "An object type with keys of type K and values of type V",
          "A read-only map", "A tuple type"],
         1, "`Record<K, V>` creates an object type mapping keys K to values V."),
        ("What is declaration merging in TypeScript?",
         ["Combining two JS files", "TypeScript's ability to merge multiple declarations of the same name into one definition",
          "Importing a module twice", "Extending a class at runtime"],
         1, "Declaration merging lets you extend existing interfaces and namespaces."),
        ("What is the purpose of `tsconfig.json`?",
         ["Storing API keys", "Configuring TypeScript compiler options for a project",
          "Defining CSS variables", "Listing npm dependencies"],
         1, "`tsconfig.json` controls compiler flags such as target ES version, strict mode, and output paths."),
    ],
    "Cybersecurity": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What is SQL injection?",
         ["A type of DDoS attack", "An attack that inserts malicious SQL into input fields to manipulate a database",
          "A network sniffing technique", "A brute-force attack on passwords"],
         1, "SQL injection exploits unparameterised queries to manipulate or dump database data."),
        ("What is a firewall?",
         ["An antivirus program", "A network security system that monitors and controls incoming/outgoing traffic based on rules",
          "A password manager", "A VPN endpoint"],
         1, "Firewalls filter network traffic according to predefined security rules."),
        ("What does SSL/TLS provide?",
         ["User authentication only", "Encrypted communication and server identity verification between client and server",
          "Network routing", "Two-factor authentication"],
         1, "SSL/TLS encrypts data in transit and authenticates the server via certificates."),
        ("What is a DDoS attack?",
         ["A single hacker overwhelming a target", "A distributed attack using many systems to flood a target and deny service to legitimate users",
          "A social engineering attack", "A code injection technique"],
         1, "DDoS (Distributed Denial of Service) uses botnets to overwhelm a target's resources."),
        ("What is a zero-day vulnerability?",
         ["A vulnerability patched on the same day it is discovered", "A vulnerability unknown to the vendor with no available patch",
          "A bug in zero-trust architecture", "A misconfigured server"],
         1, "Zero-days are exploited before the vendor is aware and can issue a fix."),
        ("What is the purpose of penetration testing?",
         ["Deploying software updates", "Simulating attacks to find and fix vulnerabilities before real attackers exploit them",
          "Monitoring network traffic", "Encrypting user data"],
         1, "Pen testing proactively discovers vulnerabilities through authorised, simulated attacks."),
        ("What is encryption at rest?",
         ["Encrypting data while it is being transmitted", "Encrypting stored data on disk so it is unreadable without the key",
          "Hashing passwords before storage", "Compressing database backups"],
         1, "Encryption at rest protects stored data from physical media theft."),
        ("What does a Security Operations Centre (SOC) do?",
         ["Develops software", "Continuously monitors, detects, and responds to security incidents",
          "Manages cloud costs", "Performs code reviews"],
         1, "A SOC team monitors systems 24/7 and responds to security events."),
        ("What is social engineering in cybersecurity?",
         ["Building social networks", "Manipulating people into divulging confidential information or performing actions",
          "Profiling network traffic", "Scanning for open ports"],
         1, "Social engineering exploits human psychology rather than technical vulnerabilities."),
        ("What is a hash function used for in security?",
         ["Encrypting data symmetrically", "Producing a fixed-size fingerprint of data to verify integrity without reversibility",
          "Generating session tokens", "Compressing files"],
         1, "Hash functions (e.g. SHA-256) are one-way; they verify data integrity without storing the original."),
    ],
    "Data Analysis": [
        # --- existing 5 questions ---
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
        # --- new questions to reach 15 ---
        ("What is a histogram?",
         ["A bar chart comparing categories", "A chart showing the distribution of a numeric variable by grouping values into bins",
          "A line chart over time", "A scatter plot matrix"],
         1, "Histograms show frequency distributions of continuous numeric data."),
        ("What does the term 'null values' mean in a dataset?",
         ["Values that equal zero", "Missing or unknown entries in the dataset",
          "Negative numbers", "Duplicate records"],
         1, "Null/NaN values represent missing data that must be handled before modelling."),
        ("What is a scatter plot used for?",
         ["Showing data over time", "Visualising the relationship between two numeric variables",
          "Comparing categories", "Displaying proportions"],
         1, "Scatter plots reveal correlations, clusters, and outliers between two variables."),
        ("What does the standard deviation measure?",
         ["The average value", "The average distance of data points from the mean",
          "The range of the dataset", "The most frequent value"],
         1, "Standard deviation quantifies how spread out values are around the mean."),
        ("What is a pivot table?",
         ["A database index", "A table that summarises data by grouping and aggregating across dimensions",
          "A type of chart", "A SQL JOIN"],
         1, "Pivot tables restructure and summarise data for cross-dimensional analysis."),
        ("What is the purpose of data normalisation?",
         ["Removing duplicate rows", "Scaling features to a common range so no single feature dominates",
          "Encoding categorical variables", "Splitting the dataset"],
         1, "Normalisation (e.g. 0-1 scaling) prevents features with large ranges from skewing analysis."),
        ("What is an outlier?",
         ["A missing value", "A data point significantly different from the rest of the dataset",
          "A duplicate record", "A categorical variable"],
         1, "Outliers can skew statistics and models; they should be investigated and handled."),
        ("What does a heatmap visualise?",
         ["Time series trends", "Magnitude of values across a two-dimensional matrix using colour intensity",
          "Distribution of a single variable", "Hierarchical clustering results"],
         1, "Heatmaps use colour to represent values, commonly used to show correlation matrices."),
        ("What is the interquartile range (IQR)?",
         ["The full range of the data", "The difference between the 75th and 25th percentile",
          "The standard deviation", "The mean absolute error"],
         1, "IQR measures statistical spread of the middle 50% of data, robust to outliers."),
        ("What is A/B testing?",
         ["Comparing two datasets for identical values", "A controlled experiment comparing two versions to determine which performs better",
          "A type of regression", "A feature selection method"],
         1, "A/B tests randomly assign users to variants and measure outcomes to guide decisions."),
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


def _patch_assessment_questions(db, skill_objs: dict):
    """Top-up existing assessments to 15 questions by adding missing questions.
    Keyed by prompt text — never inserts a duplicate.
    """
    added = 0
    for skill_name, all_questions in ASSESSMENTS.items():
        skill = skill_objs.get(skill_name)
        if not skill:
            continue
        assessment = db.query(models.Assessment).filter(
            models.Assessment.skill_id == skill.id
        ).first()
        if not assessment:
            continue
        existing_prompts = {
            q.prompt for q in db.query(models.AssessmentQuestion)
            .filter(models.AssessmentQuestion.assessment_id == assessment.id).all()
        }
        for prompt, options, correct_idx, explanation in all_questions:
            if prompt in existing_prompts:
                continue  # already present
            db.add(models.AssessmentQuestion(
                assessment_id=assessment.id, prompt=prompt, options=options,
                correct_index=correct_idx, explanation=explanation,
            ))
            existing_prompts.add(prompt)
            added += 1
    print(f"Patch: added {added} new questions to existing assessments.")


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
        _patch_assessment_questions(db, skill_objs)
        db.commit()
        print("Dataset patch complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    patch()
