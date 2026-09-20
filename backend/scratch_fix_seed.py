import re

def rewrite_seed():
    with open('app/seed.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_seed = """def seed():
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
        res_added = 0
        for skill_name, title, rtype, hours, url in RESOURCES:
            skill = skill_objs.get(skill_name)
            if not skill:
                continue
            exists = db.query(models.LearningResource).filter_by(url=url).first()
            if not exists:
                db.add(models.LearningResource(
                    skill_id=skill.id, title=title, type=rtype, difficulty="Intermediate",
                    estimated_hours=hours, url=url, description=f"Curated resource for {skill_name}.", is_demo=False,
                ))
                res_added += 1
        print(f"Seeded {res_added} learning resources.")

        # --- Assessments ---
        assessment_count, question_count = 0, 0
        for skill_name, questions in ASSESSMENTS.items():
            skill = skill_objs.get(skill_name)
            if not skill:
                continue
            assessment_title = f"{skill_name} Fundamentals Assessment"
            assessment = db.query(models.Assessment).filter_by(skill_id=skill.id, title=assessment_title).first()
            if not assessment:
                assessment = models.Assessment(
                    skill_id=skill.id, title=assessment_title,
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

        # --- Practical Assessments ---
        docker_skill = skill_objs.get("Docker")
        if docker_skill:
            practical = db.query(models.PracticalAssessment).filter_by(skill_id=docker_skill.id).first()
            if not practical:
                practical = models.PracticalAssessment(
                    skill_id=docker_skill.id,
                    title="Dockerize a Web App",
                    description="Containerize a provided Flask application. You must write a Dockerfile that sets a base image, copies files, exposes the correct port, and defines a startup command.",
                    validation_type="docker_containerize",
                )
                db.add(practical)
                print("Seeded Practical Assessment for Docker.")

        db.commit()

        # --- Demo student ---
        demo_user = db.query(models.User).filter_by(email=DEMO_EMAIL).first()
        if not demo_user:
            demo_user = models.User(
                full_name="Aditi Sharma", email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD),
                college="National Institute of Technology", degree="B.Tech", department="Computer Science",
                graduation_year=2026, onboarding_complete=True,
            )
            db.add(demo_user)
            db.flush()
            print("Created demo user.")
        else:
            print("Demo user already exists, reusing.")

        devops_career = career_objs["DevOps Engineer"]
        profile = db.query(models.StudentProfile).filter_by(user_id=demo_user.id).first()
        if not profile:
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
            progress = db.query(models.StudentProgress).filter_by(user_id=demo_user.id, skill_id=skill.id).first()
            if not progress:
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

        demo_evidence = db.query(models.Evidence).filter_by(user_id=demo_user.id, title="Resume: Aditi_Sharma_Resume.pdf").first()
        if not demo_evidence:
            demo_evidence = models.Evidence(
                user_id=demo_user.id, type="resume", title="Resume: Aditi_Sharma_Resume.pdf",
                description="Seed demo resume evidence.", source_filename="Aditi_Sharma_Resume.pdf",
            )
            db.add(demo_evidence)

        db.commit()

        # Historical readiness snapshots so the analytics trend chart has data
        existing_snaps = db.query(models.ReadinessSnapshot).filter_by(user_id=demo_user.id).count()
        if existing_snaps == 0:
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
        db.close()"""

    # Use regex to replace the def seed(): ... def _patch_skills
    # We want to match from "def seed():" up to just before "# ---" followed by "def _patch_skills"
    
    start_str = "def seed():"
    end_str = "# ---------------------------------------------------------------------------\n# Additive patch"
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    
    if start_idx != -1 and end_idx != -1:
        new_content = content[:start_idx] + new_seed + "\n\n\n" + content[end_idx:]
        with open('app/seed.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Replaced seed() successfully.")
    else:
        print("Could not find start or end index")

rewrite_seed()
