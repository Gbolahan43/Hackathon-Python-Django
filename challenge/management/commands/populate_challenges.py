import json
import os
from django.core.management.base import BaseCommand
from challenge.models import Challenge


class Command(BaseCommand):
    help = (
        "Reads challenge data from 'challenge/challenge.json' and populates the "
        "Challenge table in the database. Uses get_or_create to prevent duplicates "
        "and handles JSON errors gracefully."
    )

    def handle(self, *args, **options):
        file_path = os.path.join('challenge', 'challenge.json')

        if not os.path.isfile(file_path):
            self.stderr.write(self.style.ERROR(f"JSON file not found: {file_path}"))
            return

        try:
            with open(file_path, 'r') as json_file:
                challenges_data = json.load(json_file)
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f"Error decoding JSON: {e}"))
            return

        created_count = 0
        skipped_count = 0
        required_fields = ["name"]

        for index, item in enumerate(challenges_data, start=1):
            # Validate required fields
            if not all(item.get(field) for field in required_fields):
                self.stderr.write(self.style.WARNING(
                    f"Skipping item {index}: Missing required fields."
                ))
                skipped_count += 1
                continue

            # Prepare default fields
            defaults = {
                "description": item.get("description", ""),
                "docker_image": item.get("docker_image", ""),
                "docker_port": item.get("docker_port", 0),
                "start_port": item.get("start_port", 0),
                "end_port": item.get("end_port", 0),
                "flag": item.get("flag", ""),
                "point": item.get("point", 0),
            }

            # Create or get the challenge
            challenge, created = Challenge.objects.get_or_create(
                name=item["name"],
                defaults=defaults
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Challenge '{challenge.name}' created."))
                created_count += 1
            else:
                self.stdout.write(f"ℹ Challenge '{challenge.name}' already exists.")
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created: {created_count}, Skipped: {skipped_count}"
        ))
