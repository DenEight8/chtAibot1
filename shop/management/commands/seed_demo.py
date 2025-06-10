from pathlib import Path
from django.core.files import File
from django.core.management.base import BaseCommand
from shop.models import Category, Product


class Command(BaseCommand):
    help = "Заповнює демо-категорію й товари"

    def handle(self, *args, **opts):
        cat, _ = Category.objects.get_or_create(name="Demo", slug="demo")
        media_dir = Path("media/products")
        for img in media_dir.glob("*.jpg"):
            slug = img.stem
            p, created = Product.objects.get_or_create(
                category=cat, slug=slug,
                defaults=dict(name=slug.replace("_", " ").title(),
                              price=999.99, description="Demo item")
            )
            if created or not p.image:
                p.image.save(img.name, File(img.open("rb")), save=True)
        self.stdout.write(self.style.SUCCESS("Demo products seeded"))
