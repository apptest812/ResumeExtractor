from ..models import Resume, Experience, Education, JobDescription
from django.db import transaction

class DB():

    def __init__(self):
        pass

    def add_resume_json_to_db(self, json_object, file, user):
        """Add resume JSON to database"""

        if not json_object:
            raise ValueError("JSON not Found")

        with transaction.atomic():  # Ensure atomicity
            # Create and populate Resume
            resume = Resume(
                id=file.id,
                name=json_object.get("name"),
                phone=json_object.get("phone"),
                email=json_object.get("email"),
                more_contact_details=json_object.get("more_contact_details"),
                nationalities=json_object.get("nationalities"),
                position=json_object.get("position"),
                skills=", ".join(json_object.get("skills", [])),
                file=file.file,
                json=file.json,
                uploaded_at=file.uploaded_at,
                user=user
            )

            # Save Resume first to get its primary key
            resume.save()

            # Create and add Experiences
            experiences = []
            for exp in json_object.get("experiences", []):
                experience = Experience(
                    company=exp["company"],
                    title=exp["title"],
                    start_date=exp["start_date"],
                    end_date=exp.get("end_date"),
                    responsibilities=exp["responsibilities"],
                    resume=resume
                )
                experiences.append(experience)
            
            # Save experiences in bulk
            Experience.objects.bulk_create(experiences)  

            # Create and add Educations
            educations = []
            for edu in json_object.get("educations", []):
                education = Education(
                    degree=edu["degree"],
                    institution=edu["institution"],
                    graduation_year=edu["graduation_year"],
                    resume=resume
                )
                educations.append(education)
            
            # Save educations in bulk
            Education.objects.bulk_create(educations)  

            # Delete the file
            file.delete()

        return resume

    def add_job_description_json_to_db(self, json_object, file, user):
        """Add job description JSON to database"""
        if not json_object:
            raise ValueError("JSON not Found")

        with transaction.atomic():  # Ensure atomicity
            # Create and populate Resume
            job = JobDescription(
                id=file.id,
                title=json_object.get("title"),
                position=json_object.get("position"),
                company=json_object.get("company"),
                description=json_object.get("description"),
                phone=json_object.get("phone"),
                email=json_object.get("email"),
                more_contact_details=json_object.get("more_contact_details"),
                main_technologies=", ".join(json_object.get("main_technologies", [])),
                required_skills=", ".join(json_object.get("required_skills", [])),
                responsibilities=", ".join(json_object.get("responsibilities", [])),
                required_qualification=json_object.get("required_qualification"),
                preferred_qualification=json_object.get("preferred_qualification"),
                min_experience_in_months=json_object.get("min_experience_in_months"),
                max_experience_in_months=json_object.get("max_experience_in_months"),
                salary=json_object.get("salary"),
                address=json_object.get("address"),
                city=json_object.get("city"),
                state=json_object.get("state"),
                country=json_object.get("country"),
                postal_code=json_object.get("postal_code"),
                is_applicable_for_freshers=json_object.get("is_applicable_for_freshers"),
                total_paid_leaves=json_object.get("total_paid_leaves"),
                weekly_working_days=json_object.get("weekly_working_days"),
                other_benefits=json_object.get("other_benefits"),
                file=file.file,
                uploaded_at=file.uploaded_at,
                user=user
            )

            # Save Resume first to get its primary key
            job.save()

            # Delete the file
            file.delete()

        return job
