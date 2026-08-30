# from django_seed import Seed
from django.core.management.base import BaseCommand
from tag.factories import TagFactory


class Command(BaseCommand):
    help = "This command creates tags"

    def add_arguments(self, parser):
        parser.add_argument(
            "-n", default=10, type=int, help="How many tags do you want to create?"
        )

    def handle(self, *args, **options):
        number = options.get("n")
        TagFactory.create_batch(number)
        self.stdout.write(self.style.SUCCESS(f"{number} tags created!"))
