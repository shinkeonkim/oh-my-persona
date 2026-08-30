import random

import lorem
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from file_manager.models.thumbnail import Thumbnail
from meme.models.image_meme import ImageMeme
from meme.models.text_meme import TextMeme


class Command(BaseCommand):
    help = "Creates dummy memes for development and testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "-n",
            "--number",
            type=int,
            default=10,
            help="Total number of memes to create",
        )
        parser.add_argument(
            "--published",
            action="store_true",
            default=False,
            help="Create memes with published_at set to now",
        )
        parser.add_argument(
            "--image",
            type=int,
            default=None,
            help="Number of image memes to create (takes precedence over total)",
        )
        parser.add_argument(
            "--text",
            type=int,
            default=None,
            help="Number of text memes to create (takes precedence over total)",
        )

    def handle(self, *args, **options):
        total_memes = options.get("number")
        image_memes_count = options.get("image")
        text_memes_count = options.get("text")
        published = options.get("published")

        if image_memes_count is not None or text_memes_count is not None:
            image_memes_count = image_memes_count or 0
            text_memes_count = text_memes_count or 0
        else:
            # Split the total between image and text memes
            image_memes_count = total_memes // 2
            text_memes_count = total_memes - image_memes_count

        User = get_user_model()

        # Create the specified number of image memes
        self.stdout.write(f"Creating {image_memes_count} image memes...")

        IMG_URLS = [
            "https://img1.daumcdn.net/thumb/R1280x0.fjpg/?fname=http://t1.daumcdn.net/brunch/service/user/eHO2/image/eCEWfW0-lvcF_58Mk5QMYHWF7xo.heic",
            "https://media.istockphoto.com/id/865449012/ko/%EC%82%AC%EC%A7%84/%EA%B0%80-%EC%B6%94%EC%83%81%ED%99%94%EC%9E%85%EB%8B%88%EB%8B%A4-%EC%84%B8%EB%A1%9C%EB%A1%9C-%EA%B8%B4-%EB%B0%B0%EB%84%88%EC%9E%85%EB%8B%88%EB%8B%A4.jpg?s=1024x1024&w=is&k=20&c=nPIn1-cOc44tuRNaPUr3twdIR0sq_DUrFV7n6cUFFFo=",
            "https://academy.ilwoo.org/data/file/reference/3531300541_J1gHPmC6_479f762b4825515abc781b3a616929d8949ea2c5.jpg",
        ]

        for i in range(image_memes_count):
            # Create a thumbnail for the image meme
            thumbnail = Thumbnail.objects.create(
                name=f"Dummy Thumbnail {lorem.sentence()[:10]}",
                web_url=random.choice(IMG_URLS),
            )

            # Create the image meme
            ImageMeme.objects.create(
                title=f"Dummy Image Meme {lorem.sentence()[:10]}",
                description=lorem.paragraph()[:100],
                creator=User.objects.first(),
                thumbnail=thumbnail,
                published_at=(
                    timezone.now()
                    if published or random.choice([True, False])
                    else None
                ),
            )

        # Create the specified number of text memes
        self.stdout.write(f"Creating {text_memes_count} text memes...")
        for i in range(text_memes_count):
            # Create the text meme
            TextMeme.objects.create(
                title=f"Dummy Text Meme {lorem.sentence()[:10]}",
                description=lorem.paragraph()[:100],
                creator=User.objects.first(),
                published_at=(
                    timezone.now()
                    if published or random.choice([True, False])
                    else None
                ),
            )

        created_memes = image_memes_count + text_memes_count
        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_memes} dummy memes!")
        )
        self.stdout.write(f"- Image memes: {image_memes_count}")
        self.stdout.write(f"- Text memes: {text_memes_count}")
