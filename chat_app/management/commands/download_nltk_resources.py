import nltk
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Download required NLTK resources'

    def handle(self, *args, **kwargs):
        resources = ['punkt', 'stopwords']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}' if resource == 'punkt' else f'corpora/{resource}')
                self.stdout.write(self.style.SUCCESS(f'NLTK resource "{resource}" already exists.'))
            except LookupError:
                self.stdout.write(f'Downloading NLTK resource: {resource}...')
                nltk.download(resource)
                self.stdout.write(self.style.SUCCESS(f'Successfully downloaded "{resource}".'))
