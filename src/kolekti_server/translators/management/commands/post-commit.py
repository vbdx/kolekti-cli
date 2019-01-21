import os
import pysvn
import subprocess
import datetime

from django.core.management.base import BaseCommand, CommandError
from translators.models import TranslatorRelease

import logging
logger = logging.getLogger('kolekti.'+__name__)

class Command(BaseCommand):
        help = 'auto updates translators source trees after commit'

        def add_arguments(self, parser):
            parser.add_argument('repo', type=str)
            parser.add_argument('revision', type=int)

        def get_changed(self, revision, repo):
            cmd = subprocess.Popen(['/usr/bin/svnlook', 'changed', '-r', str(revision), repo], stdout = subprocess.PIPE)
            for line in cmd.stdout.readlines():
                yield line
                
        def get_author(self, revision, repo):
            cmd = subprocess.Popen(['/usr/bin/svnlook', 'author', '-r', str(revision), repo], stdout = subprocess.PIPE)
            author = cmd.stdout.read()
            return author.strip()
                
        def handle(self, *args, **options):
            logger.debug('handle')
            try:
                from django.conf import settings
                self.stdout.write(str(datetime.datetime.now()))
                revision = options['revision']
                repo = options['repo']
                project = repo.split('/')[-1]
                user = self.get_author(revision, repo)
                self.stdout.write("author : [%s]"%user)
                
                try:
                    acllist = TranslatorRelease.objects.exclude(user__username = user).filter(project__directory = project)
                except TranslatorRelease.DoesNotExist:
                    raise CommandError('No update for "%d" ' % revision)
                seen = set()
                client = pysvn.Client()

                for mf in self.get_changed(revision, repo):
                    mf = mf[4:]
                    chunks = mf.split('/')
                    if len(chunks)>1 and chunks[0] == "releases":
                        if not chunks[1] in seen:
                            seen.add(chunks[1])
                            updates = acllist.filter(release_name = chunks[1])
                            for update in updates:
                                path = os.path.join(settings.KOLEKTI_BASE, update.user.username, update.project.directory, 'releases', update.release_name)
                                client.update(path)
                                self.stdout.write(path+" updated")
                    
                self.stdout.write(self.style.SUCCESS('update succesfully completed'))
            except:
                logger.exception('update command failed')
