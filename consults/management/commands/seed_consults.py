from django.core.management.base import BaseCommand

from consults.models import ConsultationArticle, Doctor


class Command(BaseCommand):
    help = "Seed doctors and consultation articles"

    def handle(self, *args, **options):
        doctors = [
            {
                "name": "Др. Ажар Нурбекова",
                "specialty": "Педиатр-невролог",
                "category": "neuro",
                "rating": 4.9,
                "image": "https://img.freepik.com/free-photo/doctor-with-co-workers-at-the-back_1098-1268.jpg",
                "color": "#6366F1",
                "min_age": 0,
                "max_age": 72,
                "online": True,
                "order": 1,
            },
            {
                "name": "Др. Мади Насипкалиев",
                "specialty": "Детский психолог",
                "category": "psych",
                "rating": 5.0,
                "image": "https://img.freepik.com/free-photo/portrait-of-male-doctor-with-stethoscope-smiling_23-2148827755.jpg",
                "color": "#10B981",
                "min_age": 24,
                "max_age": 180,
                "online": True,
                "order": 2,
            },
            {
                "name": "Др. Шугыла Адилова",
                "specialty": "Логопед-дефектолог",
                "category": "speech",
                "rating": 4.8,
                "image": "https://img.freepik.com/free-photo/beautiful-young-female-doctor-looking-at-camera_23-2148480537.jpg",
                "color": "#F59E0B",
                "min_age": 18,
                "max_age": 72,
                "online": False,
                "order": 3,
            },
            {
                "name": "Др. Даулет Калкаман",
                "specialty": "Детский ортопед",
                "category": "ortho",
                "rating": 4.7,
                "image": "https://img.freepik.com/free-photo/doctor-offering-medical-assistance-to-elderly-patient_23-2148827744.jpg",
                "color": "#EC4899",
                "min_age": 6,
                "max_age": 144,
                "online": True,
                "order": 4,
            },
            {
                "name": "Др. Алтынай Даулеткалиев",
                "specialty": "Педиатр высшей категории",
                "category": "pediatric",
                "rating": 4.9,
                "image": "https://img.freepik.com/free-photo/female-doctor-hospital-with-stethoscope_23-2148827772.jpg",
                "color": "#3B82F6",
                "min_age": 0,
                "max_age": 180,
                "online": True,
                "order": 5,
            },
        ]

        articles = [
            {
                "title": "Как подготовить ребенка к консультации?",
                "icon": "book-outline",
                "color": "#6366F1",
                "content": "Перед консультацией соберите жалобы, результаты анализов и список вопросов.",
                "order": 1,
            },
            {
                "title": "Режим дня и здоровье системы",
                "icon": "alarm-outline",
                "color": "#10B981",
                "content": "Стабильный режим сна и бодрствования помогает развитию ребенка.",
                "order": 2,
            },
        ]

        for doctor in doctors:
            Doctor.objects.update_or_create(
                name=doctor["name"],
                defaults=doctor,
            )

        for article in articles:
            ConsultationArticle.objects.update_or_create(
                title=article["title"],
                defaults=article,
            )

        self.stdout.write(self.style.SUCCESS("Consult data seeded"))