import json
import os
from django.core.management.base import BaseCommand, CommandError
from challenge.models import Challenge


class Command(BaseCommand):
    help = "Populates the database with test challenge data from a JSON file"

    def handle(self, *args, **options):
        filename = os.path.join("challenge", "challenge.json")

        if not os.path.exists(filename):
            raise CommandError(f"File not found: {filename}")

        with open(filename, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as e:
                raise CommandError(f"Invalid JSON format: {e}")

        created_count = 0
        failed_count = 0

        for index, challenge_data in enumerate(data, start=1):
            try:
                Challenge.objects.create(**challenge_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f" Challenge {index} created"))
            except Exception as e:
                failed_count += 1
                self.stderr.write(self.style.WARNING(
                    f" Failed to create challenge {index}: {e}"
                ))

        self.stdout.write(self.style.NOTICE(f"\nSummary:"))
        self.stdout.write(self.style.SUCCESS(f"Created: {created_count}"))
        self.stdout.write(self.style.WARNING(f"Failed: {failed_count}"))
