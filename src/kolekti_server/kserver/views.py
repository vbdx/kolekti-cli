# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import re
import os
from copy import copy
import shutil
import json
import random
from datetime import datetime
import time
from lxml import etree as ET
import base64
from PIL import Image
import urllib, urllib2
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import logging
logger = logging.getLogger('kolekti.'+__name__)
       
from kserver_saas.models import Project, UserProfile, UserProject
from forms import UploadFileForm, SearchForm

from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views.generic import View,TemplateView, ListView
from django.views.generic.base import TemplateResponseMixin
from django.views.static import serve 
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from django.template.loader import get_template
from django.template import Context
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# kolekti imports
from kolekti.common import kolektiBase
from kolekti.publish_utils import PublisherExtensions
from kolekti import publish
from kolekti.searchindex import Searcher
from kolekti.exceptions import ExcSyncNoSync
from kolekti.variables import OdsToXML, XMLToOds
from kolekti.import_sheets import Importer, Templater

fileicons= {
    "application/zip":"fa-file-archive-o",
    'application/x-tar':"fa-file-archive-o",
    "audio/mpeg":"fa-file-audio-o",
    "audio/ogg":"fa-file-audio-o",
    "application/xml":"fa-file-code-o",
    "application/vnd.ms-excel":"fa-file-excel-o",
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':"fa-file-excel-o",
    'application/vnd.oasis.opendocument.spreadsheet':"fa-file-excel-o",
    'image/png':"fa-file-image-o",
    'image/gif':"fa-file-image-o",
    'image/jpeg':"fa-file-image-o",
    'image/tiff':"fa-file-image-o",
    "application/pdf":"fa-file-pdf-o",
    'application/vnd.oasis.opendocument.presentation':"fa-file-powerpoint-o",
    'application/vnd.ms-powerpoint':"fa-file-powerpoint-o",
    'application/vnd.openxmlformats-officedocument.presentationml.presentation':"fa-file-powerpoint-o",
    'text/html':"fa-file-text-o",
    'text/plain':"fa-file-text-o",
    'video/mpeg':"fa-file-video-o",
    'application/vnd.oasis.opendocument.text':"fa-file-word-o",
    'application/msword':"fa-file-word-o",
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document':"fa-file-word-o",
    "application/octet-stream":"fa-file-o",
    "text/directory":"fa-folder-o",
    }



    
class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        if settings.KOLEKTI_MULTIUSER:
            return login_required(view)
        else:
            return view

class kolektiMixin(LoginRequiredMixin, TemplateResponseMixin, kolektiBase):
#    def __init__(self, *args, **kwargs):
#        self.user_settings = Settings.objects.get()
#        projectpath = os.path.join(settings.KOLEKTI_BASE, self.user_settings.active_project)
#        super(kolektiMixin, self).__init__(projectpath,*args,**kwargs)

    def config(self):
        return self._config

    def dispatch(self, *args, **kwargs):
        if self.request.kolekti_userproject is not None:
            self.set_project(self.request.kolekti_projectpath)
        # try:
        #     self.kolekti_userproject = self.request.user.userprofile.activeproject
        #     if self.kolekti_userproject is not None:
        #         self.kolekti_projectpath = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, self.kolekti_userproject.project.directory)
        
        #         self.set_project(self.kolekti_projectpath)
        # except:
        #     self.kolekti_userproject = None
        #     logger.warning('user %s has no user profile', str(self.request.user))
            
        return super(kolektiMixin, self).dispatch(*args, **kwargs)

    def process_svn_url(self, url):
        localpath = "file://%s/"%(settings.KOLEKTI_SVN_ROOT,)
        remotepath = "http://%s/svn/"%(settings.HOSTNAME,)
#        return localpath
        return url.replace(localpath, remotepath)
    
    def projects(self):
        projects = []
#        logger.debug(self.request.user.username)
        if settings.KOLEKTI_MULTIUSER:
            userprojects = UserProject.objects.filter(user = self.request.user)
        else:
            userprojects = UserProject.objects.all()
        for up in userprojects:
            project={
                'userproject':up,
                'name':up.project.name,
                'id':up.project.pk,
            }
            try:
                project_path = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, up.project.directory)
                project_settings = ET.parse(os.path.join(project_path, 'kolekti', 'settings.xml')).getroot()
                if project_settings.xpath('string(/settings/@version)') != '0.7':
                    continue
                project.update({'languages':[l.text for l in project_settings.xpath('/settings/languages/lang')],
                                'defaultlang':project_settings.xpath('string(/settings/@sourcelang)')})
            except:
                continue


            try:
                from kolekti.synchro import SynchroManager
                synchro = SynchroManager(project_path)
                projecturl = synchro.geturl()
                project.update({"status":"svn","url":self.process_svn_url(projecturl)})
            except ExcSyncNoSync:
                project.update({"status":"local"})
            projects.append(project)
            
        return sorted(projects, key=lambda p: p.get('name').lower())


    def project_langs(self):
        try:
            return ([l.text for l in self._project_settings.xpath('/settings/languages/lang')],
                    [l.text for l in self._project_settings.xpath('/settings/releases/lang')],
                    self._project_settings.xpath('string(/settings/@sourcelang)'))
        except IOError:
            return ['en'],['en','fr','de'],'en'
        except AttributeError:
            return ['en'],['en','fr','de'],'en'
    
    def get_context_data(self, data={}, **kwargs):
        context= {
            'active_project':self.request.kolekti_userproject,
            'projects':self.projects(),
        }
        
        if self.request.kolekti_userproject is not None:
            up = self.request.kolekti_userproject
            languages, release_languages, default_srclang = self.project_langs()
            project_path = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, up.project.directory)
            try:
                from kolekti.synchro import SynchroManager
                synchro = SynchroManager(project_path)
                projecturl = synchro.geturl()
                context.update({"svn_url":self.process_svn_url(projecturl)})
            except ExcSyncNoSync:
                context.update({"svn_url":"local"})

            context.update({
                'kolekti':self._config,
                'srclangs' : languages,
                'releaselangs' : release_languages,
                'default_srclang':default_srclang,
                'active_project_name' : self.request.kolekti_userproject.project.name,
                'active_project_directory' : self.request.kolekti_userproject.project.directory,                                      
                'active_project_admin' : self.request.kolekti_userproject.is_admin,                           
                'active_srclang' : self.request.kolekti_userproject.srclang,
#                'syncnum' : self._syncnumber,
                'kolektiversion' : self._kolektiversion,
            })
        context.update(data)
        return context

    def get_toc_edit(self, path):
        xtoc = self.parse(path)
        tocmeta = {}
        toctitle = xtoc.xpath('string(/html:html/html:head/html:meta[@name="DC.title"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        tocauthor = xtoc.xpath('string(/html:html/html:head/html:meta[@name="DC.author"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        if len(toctitle) == 0:
            toctitle = xtoc.xpath('string(/html:html/html:head/html:title)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        for meta in xtoc.xpath('/html:html/html:head/html:meta', namespaces={'html':'http://www.w3.org/1999/xhtml'}):
            if meta.get('name',False):
                tocmeta.update({meta.get('name').replace('.','_'):meta.get('content')})
        tocjob = xtoc.xpath('string(/html:html/html:head/html:meta[@name="kolekti.job"]/@content)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('django_toc_edit', extclass=PublisherExtensions, lang=self.request.kolekti_userproject.srclang)
        try:
            etoc = xsl(xtoc)
        except:
            import traceback
            print traceback.format_exc()
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return toctitle, tocauthor, tocmeta, str(etoc)

    def localname(self,e):
        return re.sub('\{[^\}]+\}','',e.tag)
    
    def get_topic_edit(self, path):
        return self.read(path.replace('{LANG}',self.request.kolekti_userproject.srclang))
#        xtopic = self.parse(path.replace('{LANG}',self.user_settings.active_srclang))
#        head = xtopic.xpath('/html:html/html:head', namespaces={'html':'http://www.w3.org/1999/xhtml'})[0]
#        ET.SubElement(head, 'script', {"src":"/static/jquery.js"})
#        ET.SubElement(head, 'script', {"src":"/static/ckeditor/ckeditor.js"})
#        ET.SubElement(head, 'script', {"src":"/static/js/kolekti-topicedit.js"})
#        ET.SubElement(head, 'script', {"src":"/settings.js"})
#        print xtopic
#        return ET.tostring(xtopic, xml_declaration=True, encoding="utf-8")
        
        # topictitle = xtopic.xpath('string(/html:html/html:head/html:title)', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        # topicmeta = xtopic.xpath('/html:html/html:head/html:meta[@name]', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        # topicmetalist = [{'tag':self.localname(m),'name':m.get('name',None),'content':m.get('content',None)} for m in topicmeta]
        # topicmeta = xtopic.xpath('/html:html/html:head/html:title', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        # topicmetalist += [{'tag':self.localname(m),'title':m.text} for m in topicmeta]
        # topicmeta = xtopic.xpath('/html:html/html:head/html:link', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        # topicmetalist += [{'tag':self.localname(m),'rel':m.get('rel',None),'type':m.get('type',None),'href':m.get('href',None)} for m in topicmeta]
        # topicbody = xtopic.xpath('/html:html/html:body/*', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        # xsl = self.get_xsl('django_topic_edit')
        # #print [str(xsl(t)) for t in topicbody]
        # topiccontent = ''.join([str(xsl(t)) for t in topicbody])
        # return topictitle, topicmetalist, topiccontent

    def get_assembly_edit(self, path, release_path=""):
        xassembly = self.parse(path.replace('{LANG}',self.request.kolekti_userproject.publang))
        body = xassembly.xpath('/html:html/html:body/*', namespaces={'html':'http://www.w3.org/1999/xhtml'})
        xsl = self.get_xsl('django_assembly_edit')
        content = ''.join([str(xsl(t, path="'%s'"%release_path)) for t in body])
        return content
    
    def get_tocs(self):
        return self.itertocs

    def get_jobs(self):
        res = []
        for job in self.iterjobs:
            xj = self.parse(job['path'])
            profiles = []
            scripts  = []
            
            for p in xj.xpath('/job/profiles/profile'):
                label = p.find('label').text
                enabled = p.get('enabled')
                profiles.append((label, enabled))
                
            for s in xj.xpath('/job/scripts/script'):
                try:
                    label = s.find('label').text
                except:
                    continue
                enabled = s.get('enabled')
                scripts.append((label, enabled))
                
            job.update({'profiles': profiles,
                        'scripts':scripts,
                        })
            res.append(job)
        return sorted(res, key = lambda j: j['name'])

    def get_job_edit(self,path):
        xjob = self.parse(path)
        xjob.getroot().append(copy(self._project_settings))
        xjob.getroot().find('settings').append(copy(self.get_scripts_defs()))
        try:
            xscripts = self.parse('/kolekti/pubscripts.xml').getroot()
            for pubscript in xscripts.xpath('/scripts/pubscript'):
                pubscript.set('type',"multi")
            xjob.getroot().find('settings').append(copy(xscripts))
        except:
            logger.exception('unable to get local script definitions')

        xsl = self.get_xsl('django_job_edit', extclass=PublisherExtensions, lang=self.request.kolekti_userproject.srclang)
        try:
            ejob = xsl(xjob, path="'%s'"%path, jobname="'%s'"%self.basename(path))
        except:
            self.log_xsl(xsl.error_log)
            raise Exception, xsl.error_log
        return str(ejob)

    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)

    def project_activate(self,userproject):
        # get userdir
        if settings.KOLEKTI_MULTIUSER:
            self.request.user.userprofile.activeproject = userproject
            self.request.user.userprofile.save()
            self.request.kolekti_projectpath = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, userproject.project.directory)
        else:
            userprofile = UserProfile.objects.get()
            userprofile.activeproject = userproject
            userprofile.save()
            self.request.kolekti_projectpath = os.path.join(settings.KOLEKTI_BASE, userproject.project.directory)        
        self.request.kolekti_userproject = userproject
        self.set_project(self.request.kolekti_projectpath)
        try:
            languages, rlang, defaultlang = self.project_langs()
            if not self.request.kolekti_userproject.srclang in languages:
                self.request.kolekti_userproject.srclang = defaultlang
                self.request.kolekti_userproject.save()
        except:
            self.request.kolekti_userproject.srclang='en'
            self.request.kolekti_userproject.save()

        

    def language_activate(self,language):
        # get userdir
        self.request.kolekti_userproject.srclang = language
        self.request.kolekti_userproject.save()


    def format_iterator(self, sourceiter):
        template = get_template('publication-iterator.html')
        nbchunck = 0
        for chunck in sourceiter:
            nbchunck += 1
            chunck.update({'id':nbchunck})
            yield template.render(chunck)
        

    def set_extension(self, path, default):
        if os.path.splitext(path)[1] == "":
            path = path + default
        return path
    
class HomeView(kolektiMixin, View):
    template_name = "home.html"

    def get(self, request):
        context = self.get_context_data()
        if context.get('active_project') is None:
            try:
                request.user.groups.get(name=u'translator')
                return HttpResponseRedirect(reverse('translators_home')) 
            except ObjectDoesNotExist:
                return HttpResponseRedirect(reverse('projects')) 
        else:
            return self.render_to_response(context)


class ProjectsView(kolektiMixin, View):
    template_name = "projects.html"
    def get(self, request, require_svn_auth=False, project_folder="", project_url="", error = None):
        
        context = self.get_context_data({
                    "require_svn_auth":require_svn_auth,
                    "projectfolder":project_folder,
                    "projecturl":project_url,
                    "error":error,
                    })
        if self.request.kolekti_userproject is not None:
            context.update({
                    "projectfolder":self.request.kolekti_userproject.project.directory,
                    })
        if hasattr(self,'_project_starters'):
            context.update({'project_starters':self._project_starters(request.user)})
        return self.render_to_response(context)

    def post(self, request):
        project_folder = request.POST.get('projectfolder')
        project_url = request.POST.get('projecturl')
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        from kolekti.synchro import SVNProjectManager
        sync = SVNProjectManager(settings.KOLEKTI_BASE,username,password)

        if project_url=="":
        # create local project
            #sync.export_project(project_folder)
            try:
                self.create_project(project_folder, settings.KOLEKTI_BASE)
                self.project_activate(project_folder)
            except:
                logger.exception('unable to create new project')
                return self.get(request,project_folder=project_folder, error="Erreur à la création du projet")
        else:
            try:
                sync.checkout_project(project_folder, project_url)
            except ExcSyncNoSync:
                logger.exception('unable to checkout project')
                return self.get(request, require_svn_auth=True, project_folder=project_folder, project_url=project_url, error="Erreur à la récupération du projet")
            
        project = Project(
            name = project_folder,
            description = "Kolekti project %s"%project_folder,
            directory = project_folder,
            owner = User.objects.get(),
            template = None,
            )
        project.save()
                              
        up = UserProject(
            user = User.objects.get(),
            project = project,
            is_saas = False,
            is_admin = True,
            )
        up.save()
        
        return self.get(request)
        
            
class ProjectsConfigView(kolektiMixin, View):
    template_name = "projects-config.html"
    def get(self, request):
        settings = self.parse('/kolekti/settings.xml')
        
        context = self.get_context_data({
            "active_project" :self.request.kolekti_userproject.project.name,
            "srclangs" :[l.text for l in settings.xpath('/settings/languages/lang')],
            "releaselangs" :[l.text for l in settings.xpath('/settings/releases/lang')],
            "default_srclang":settings.xpath('string(/settings/@sourcelang)'),
            "active_srclang":self.request.kolekti_userproject.srclang
            })
            
        return self.render_to_response(context)

    def post(self, request):
        try:
            settings = self.parse('/kolekti/settings.xml').getroot()
            srclangs = request.POST.getlist('sources[]',[])
            rellangs = request.POST.getlist('releases[]',[])
            settings.set('sourcelang', request.POST.get('default_source','en'))
            xlangs = settings.find('languages')
            if xlangs is None:
                xlangs = ET.SubElement(settings, 'languages')
            else:
                for l in xlangs:
                    xlangs.remove(l)
            for l in srclangs:
                xl = ET.SubElement(xlangs,'lang')
                xl.text = l
    
            xlangs = settings.find('releases')
            if xlangs is None:
                xlangs = ET.SubElement(settings, 'releases')
            else:
                for l in xlangs:
                    xlangs.remove(l)
            for l in set(rellangs).union(set(srclangs)):
                xl = ET.SubElement(xlangs,'lang')
                xl.text = l
    
            self.xwrite(settings,'/kolekti/settings.xml')
            return HttpResponse(json.dumps('ok'),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=404)
                    
class ProjectsActivateView(ProjectsView):
    def get(self, request):
        project = request.GET.get('project')
        redirect =request.GET.get('redirect',reverse('home'))

        if settings.KOLEKTI_MULTIUSER:
            userproject = UserProject.objects.get(user = self.request.user, project__name = project)
        else:
            userproject = UserProject.objects.get(project__name = project)        
        self.project_activate(userproject)
        return HttpResponseRedirect(redirect)
            



class ProjectsLanguageView(ProjectsView):
    def get(self, request):
        project = request.GET.get('lang')
        self.language_activate(project)
        return super(ProjectsLanguageView, self).get(request)

        
class PublicationsListJsonView(kolektiMixin, View):
    def get(self, request):
        context = {
            "publications": [p for p in self.get_publications()]
        }
        return HttpResponse(json.dumps(context),content_type="application/json")

class PublicationsZipView(kolektiMixin, View):
    def get(self,request):
        path = request.GET.get('path')
        zipname = path.split('/')[-1]
        try:
            response = HttpResponse(self.zip_publication(path),content_type="application/zip")
            response['Content-Disposition'] = 'attachment; filename=%s.zip'%zipname
            return response
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=404)

class ReleasesPublicationsListJsonView(kolektiMixin, View):
    def get(self, request):
        context = {
            "publications": [p for p in self.get_releases_publications()]
        }
        return HttpResponse(json.dumps(context),content_type="application/json")


class TocsListView(kolektiMixin, View):
    template_name = 'tocs/list.html'
    

class TocView(kolektiMixin, View):
    template_name = "tocs/detail.html"

    def get(self, request):
        context = self.get_context_data()
        tocpath = request.GET.get('toc')
        tocfile = tocpath.split('/')[-1]
        tocdisplay = os.path.splitext(tocfile)[0]
        toctitle, tocauthor, tocmeta, toccontent = self.get_toc_edit(tocpath)
        
        context.update({'tocfile':tocfile,
                        'tocdisplay':tocdisplay,
                        'toctitle':toctitle,
                        'tocauthor':tocauthor,
                        'toccontent':toccontent,
                        'tocpath':tocpath,
                        'tocmeta':tocmeta})
#        context.update({'criteria':self.get_criteria()})
        context.update({'jobs':self.get_jobs()})

        return self.render_to_response(context)
    
    def post(self, request):
        try:
            xtoc=self.parse_string(request.body)
            tocpath = xtoc.get('data-kolekti-path')
            xtoc_save = self.get_xsl('django_toc_save')
            xtoc = xtoc_save(xtoc)
            self.write(str(xtoc), tocpath)
            return HttpResponse('ok')
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)


class TocCreateView(kolektiMixin, View):
    template_name = "home.html"
    def post(self, request):
        try:
            tocpath = request.POST.get('tocpath')
            tocpath = self.set_extension(tocpath, ".html")
            toc = self.parse_html_string("""<?xml version="1.0"?>
<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml">
  <head><title>toc</title></head>
  <body></body>
</html>""")
            self.xwrite(toc, tocpath)
        except:
            import  traceback
            print traceback.format_exc()
        return HttpResponse(json.dumps(self.path_exists(tocpath)),content_type="application/json")


class ReleaseListView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"

class ReleaseAllStatesView(kolektiMixin, TemplateView):
    def get(self, request):
        path, assembly_name = request.GET.get('release').rsplit('/',1)
        languages, release_languages, default_srclang = self.project_langs()
        states = []
        for lang in release_languages:
            asfilename = "/".join(['/releases',assembly_name,"sources",lang,"assembly",assembly_name+'_asm.html'])
            try:
                state = self.syncMgr.propget("release_state",asfilename)
            except:
                state = None
            if state is None:
                if self.exists(asfilename):
                    states.append((lang, "local"))

            if state == "source_lang":
                states.insert(0,(lang, state))
            else:
                states.append((lang, state))
        return HttpResponse(json.dumps(states),content_type="application/json")

    
class ReleaseStateView(kolektiMixin, TemplateView):
    def get(self, request):
        path, assembly_name = request.GET.get('release').rsplit('/',1)
        lang = request.GET.get('lang', self.request.kolekti_userproject.srclang)
        if self.syncMgr is None:
            state = "unknown"
        else:
            state = self.syncMgr.propget("release_state","/".join(['/releases',assembly_name,"sources",lang,"assembly",assembly_name+'_asm.html']))
        return HttpResponse(state)

    def post(self,request):
        try:
            path, assembly_name = request.POST.get('release').rsplit('/',1)
            state = request.POST.get('state')
            lang = request.POST.get('lang')
            assembly = "/".join(['/releases',assembly_name,"sources",lang,"assembly",assembly_name+'_asm.html'])
            self.syncMgr.propset("release_state",state, assembly)
            return HttpResponse(state)
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
                    
class ReleaseFocusView(kolektiMixin, TemplateView):

    def post(self,request):
        try:
            release = request.POST.get('release')
            path, assembly_name = release.rsplit('/',1)
            state = request.POST.get('state')
            lang = request.POST.get('lang')
            try:
                rf = ReleaseFocus.objects.get(release = release, assembly = assembly_name, lang = lang)
            except ReleaseFocus.DoesNotExist:
                rf = ReleaseFocus(release = release, assembly = assembly_name, lang = lang)
            rf.state = (state == "true")
            rf.save()
            return HttpResponse(json.dumps({"status":"OK"}), content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
                    
class ReleaseCopyView(kolektiMixin, TemplateView):
    template_name = "releases/list.html"
    def post(self,request):
        try:
            release = request.POST.get('release')
            path, assembly_name = release.rsplit('/',1) 
            srclang = request.POST.get('release_copy_from_lang')
            dstlang = request.POST.get('release_lang')

            #            return StreamingHttpResponse(
            for copiedfiles in self.copy_release(path, assembly_name, srclang, dstlang):
                pass
            assembly = "/".join(['/releases',assembly_name,"sources",dstlang,"assembly",assembly_name+'_asm.html'])
            self.syncMgr.propset("release_state",'edition', assembly)
            self.syncMgr.propset("release_srclang", srclang, assembly)
            # self.syncMgr.commit(path,"Revision Copy %s to %s"%(srclang, dstlang))


        except:
            import traceback
            print traceback.format_exc()
    #    return HttpResponse("ok")
        return HttpResponseRedirect('/releases/detail/?release=%s&lang=%s'%(path,dstlang))
    
class ReleaseDeleteView(kolektiMixin, View):
    def post(self,request):
        try:
            release = request.POST.get('release')
            lang = request.POST.get('lang')
            self.delete_resource('%s/sources/%s'%(release, lang))
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        except:
            logger.exception("Could not delete release")
            return HttpResponse(status=500)
            
class ReleaseAssemblyView(kolektiMixin, TemplateView):
    def get(self, request):
        try:
            release_path = request.GET.get('release')
            assembly_name = release_path.rsplit('/',1)[1]
            lang = request.GET.get('lang', self.request.kolekti_userproject.srclang)
            assembly_path = '/'.join([release_path,"sources",lang,"assembly",assembly_name+"_asm.html"])
            content = self.get_assembly_edit(assembly_path, release_path=release_path),
        except:
            import traceback
            print traceback.format_exc()
        return HttpResponse(content)
    

class ReleasePublicationsView(kolektiMixin, TemplateView):
    template_name = "releases/publications.html"
    
    def __release_publications(self, lang, release_path):
        publications = []
        try:
            mf = json.loads(self.read(release_path + "/manifest.json"))
            for event in mf:
                if event.get('event','') == "release_publication":
                    for event2 in event.get('content'):
                        if event2.get('event','') == "lang" and event2.get('label','') == lang:
                            publications.extend(event2.get('content'))
        except:
            import traceback
            print traceback.format_exc()
        return publications

    def get(self, request):
        release_path = request.GET.get('release')
        lang = request.GET.get('lang', self.request.kolekti_userproject.srclang)
        context = self.get_context_data({
            'publications':self.__release_publications(lang, release_path)
        })
        return self.render_to_response(context)
                
class ReleaseDetailsView(kolektiMixin, TemplateView):
    template_name = "releases/detail.html"

    def __has_valid_actions(self,  release_path):
        assembly = release_path.rsplit('/',1)[1]
        xjob = self.parse(release_path + '/kolekti/publication-parameters/'+ assembly +'_asm.xml')
        print xjob.xpath('/job/scripts/script[@enabled="1"]/validation/script')
        return len(xjob.xpath('/job/scripts/script[@enabled="1"]/validation/script')) > 0

    
    def get_context_data(self, context):
        context = super(ReleaseDetailsView, self).get_context_data(context)
        states = []
        focus = []
        release_path = context.get('release_path')
        assembly_name = context.get('assembly_name')
        assembly_lang = context.get('lang')
        langstate = None
        for lang in context.get('releaselangs',[]):
            tr_assembly_path = release_path+"/sources/"+lang+"/assembly/"+assembly_name+'_asm.html'
            if self.path_exists(tr_assembly_path):
                if (self.syncMgr is not None):
                    states.append(self.syncMgr.propget('release_state',tr_assembly_path))
                else:
                    states.append("local")
            else:
                states.append("unknown")
            if lang == assembly_lang:
                langstate = states[-1]
            try:
                focus.append(ReleaseFocus.objects.get(release = release_path, assembly = assembly_name, lang = lang).state)
            except:
                focus.append(False)
        context.update({'langstate':langstate,'langstates':zip(context.get('releaselangs',[]),states,focus)})
        return context
    
    def get(self, request):
        release_path = request.GET.get('release')
        lang = request.GET.get('lang', self.request.kolekti_userproject.srclang)
        assembly_name = self.basename(release_path)
        assembly_path = '/'.join([release_path,"sources",lang,"assembly",assembly_name+"_asm.html"])
        assembly_meta = {}
        try:
            xassembly = self.parse(assembly_path)
            for meta in xassembly.xpath("/h:html/h:head/h:meta",namespaces = {"h":"http://www.w3.org/1999/xhtml"}):
                if meta.get('name') is not None:
                    assembly_meta.update({meta.get('name').replace('.','_'):meta.get('content')})
        except IOError:
            pass
        logger.debug(assembly_path)
        try:
            srclang = self.syncMgr.propget('release_srclang', assembly_path)
        except:
            srclang = self.request.kolekti_userproject.srclang
        if srclang is None:
            srclang = self.project_langs()[2]
        parameters = self.parse('/'.join([release_path,"kolekti","publication-parameters",assembly_name+"_asm.xml"]))
        profiles = []
        for profile in parameters.xpath('/job/profiles/profile[@enabled="1"]'):
            profiles.append({
                'label':profile.find('label').text,
                'criteria':self._get_criteria_dict(profile)
                })
        scripts = []
        for script in parameters.xpath('/job/scripts/script[@enabled="1"]'):
            scripts.append(script.find('label').text)
            #print self.get_assembly_edit(assembly_path)
        context = self.get_context_data({
            'releasesinfo':self.release_details(release_path, lang),
            'releaseparams':{'profiles':profiles, 'scripts':scripts},
            'success':True,
            'release_path':release_path,
            'assembly_name':assembly_name,
            'assembly_meta':assembly_meta,
            'lang':lang,
            'srclang':srclang,
            'validactions':self.__has_valid_actions(release_path)
        })
        logger.debug(context)
        logger.debug(context.get('srclang','not defined'))
        return self.render_to_response(context)
    
    def post(self, request):
        release_path = request.GET.get('release')
        assembly_name = release_path.rsplit('/',1)[1]

        lang=request.GET.get('lang',self.request.kolekti_userproject.srclang)
        assembly_path = '/'.join([release_path,'sources',lang,'assembly',assembly_name+'_asm.html'])
        payload = request.FILES.get('upload_file').read()
        xassembly = self.parse_string(payload)
        
        xsl = self.get_xsl('django_assembly_save')
        xassembly = xsl(xassembly, prefixrelease='"%s"'%release_path)
        self.update_assembly_lang(xassembly, lang)
        self.xwrite(xassembly, assembly_path)
        try:
            srclang = self.syncMgr.propget('release_srclang', assembly_path)
        except:
            srclang = self.request.kolekti_userproject.srclang
        context = self.get_context_data({
            'releasesinfo':self.release_details(release_path, lang),
            'success':True,
            'release_path':release_path,
            'assembly_name':assembly_name,
            'lang':lang,
            'srclang':srclang,
        })
        return self.render_to_response(context)


class ReleasePublishView(kolektiMixin, TemplateView):
    def post (self, request):
        release_path = request.POST.get('release')
        assembly_name = release_path.rsplit('/',1)[1]
        langs = request.POST.getlist('langs[]',[])
        context={}
        try:
            p = publish.ReleasePublisher(release_path, self.request.kolekti_projectpath, langs=langs)
            return StreamingHttpResponse(self.format_iterator(p.publish_assembly(assembly_name + "_asm")), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)

class ReleaseValidateView(kolektiMixin, TemplateView):
    def post (self, request):
        release_path = request.POST.get('release')
        langs = request.POST.getlist('langs[]',[])
        context={}

#        jobpath = release + '/kolekti/publication-parameters/' + assembly + '.xml'
#        print jobpath
#        xjob = self.parse(jobpath)
        try:
            p = publish.ReleasePublisher(release_path, self.request.kolekti_projectpath, langs=langs)
            return StreamingHttpResponse(self.format_iterator(p.validate_release()), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)

class TopicsListView(kolektiMixin, TemplateView):
    template_name = "topics/list.html"

class TopicTemplateListView(kolektiMixin, TemplateView):
    template_name = "topics/templates.html"

class ImagesListView(kolektiMixin, TemplateView):
    template_name = "illustrations/list.html"
    def get(self, request):
        context = self.get_context_data({
            'root':request.GET.get('path','')
            })
        return self.render_to_response(context)


class ImagesUploadView(kolektiMixin, TemplateView):
    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            path = request.POST['path']
            self.write_chunks(uploaded_file.chunks, path +'/'+ uploaded_file.name, mode = "wb") 
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        else:
            return HttpResponse(status=500)

class ImagesDetailsView(kolektiMixin, TemplateView):
    template_name = "illustrations/details.html"
    def get(self, request):
        path = request.GET.get('path')
        name = path.rsplit('/',1)[1]
        ospath = self.getOsPath(path)
        try:
            im = Image.open(ospath)
            context = self.get_context_data({
                'fileweight':"%.2f"%(float(os.path.getsize(ospath)) / 1024),
                'name':name,
                'path':path,
                'format':im.format,
                'mode':im.mode,
                'size':im.size,
                'info':im.info,
                })
        except:
            import traceback
            print traceback.format_exc()
            context = self.get_context_data({
                'name':name,
                'path':path,
                })
        return self.render_to_response(context)


class VariablesListView(kolektiMixin, TemplateView):
    template_name = "variables/list.html"


class VariablesMixin(kolektiMixin, TemplateView):

    def getval(self, val):
        try:
            return val.find('content').text
        except AttributeError:
            return ""
        
    def variable_details(self, path, include_values = None):
        name=path.rsplit('/',1)[1]
        xmlvar = self.parse(path)
        crits = [c.text[1:] for c in xmlvar.xpath('/variables/critlist/crit')]
        variables = xmlvar.xpath('/variables/variable/@code')
        values = xmlvar.xpath('/variables/variable[1]/value')
        conditions = [{
            'label':", ".join(["=".join((c.get('name'),c.get('value')))  for c in v.findall('crit')]) ,
            'expr':dict([(c.get('name'),c.get('value')) for c in v.findall('crit')])
            } for v in values]
            
        vardata = {
            "crits" : crits,
            "variables" : variables,
            "conditions" : conditions,
            "criteria" : self._get_criteria_def_dict(include_lang = True),
            }
        if include_values:
            vardata.update({"values": [[self.getval(v) for v in var.xpath('value') ] for var in xmlvar.xpath('/variables/variable')]})
            
        context = self.get_context_data({
            'name':name,
            'path':path,
            'vardata' : json.dumps(vardata),
            })
        context.update(vardata)
        return context

    def post(self, request):
        try:
            payload = json.loads(request.body)
            varpath = payload.get('path')
            xvar = self.parse(varpath)
            for var, mvar in zip(xvar.xpath('/variables/variable'), payload.get('data')):
                for (val, mval) in zip(var.xpath('value/content'), mvar):
                    val.text = mval
            self.xwrite(xvar, varpath)
            return HttpResponse('ok')
        except:
            logger.exception('Could not save variable')
            return HttpResponse(status=500)
    
class VariablesDetailsView(VariablesMixin):
    template_name = "variables/details.html"
    def get(self, request):
        path = request.GET.get('path')
        try:
            return self.render_to_response(self.variable_details(path))
        except:
            logger.exception('unable to process variable file')
            raise
        
    def post(self, request):
        try:
            action = request.POST.get('action')
            path = request.POST.get('path')
            xvar = self.parse(path)
            if action == "newvar":
                varname = request.POST.get('varname')
                varvalue = request.POST.get('varvalue')
                try:
                    firstvar = xvar.xpath('/variables/variable[1]')
                    newvar = ET.SubElement(xvar.xpath('/variables')[0],'variable', {"code":varname})
                    if len(firstvar):
                        for value in firstvar[0]:
                            newval = ET.SubElement(newvar, 'value')
                            for crit in value.xpath('crit'):
                                ET.SubElement(newval, 'crit',{
                                    "name":crit.get("name"),                            
                                    "value":crit.get("value")
                                    })
                            xcontent = ET.SubElement(newval,'content')
                            xcontent.text = request.POST.get('varvalue','')

                    else:
                        newval = ET.SubElement(newvar, 'value')
                        
                        xcontent = ET.SubElement(newval,'content')
                        xcontent.text = request.POST.get('varvalue','')
                except:
                    logger.exception('could not add variable')
                    
            if action == "delvar":
                index = int(request.POST.get('index'))
                delvar = xvar.xpath('/variables/variable[%d]'%index)[0]
                delvar.getparent().remove(delvar)
                
            if action == "renamevar":
                index = int(request.POST.get('index'))
                newname = request.POST.get('varname')
                var = xvar.xpath('/variables/variable[%d]'%index)[0]
                var.set('code', newname)
            
            if action == "newcond":
                crits = [c.text[1:] for c in xvar.xpath('/variables/critlist/crit')]
                for var in xvar.xpath('/variables/variable'):
                    if len(var.xpath('value/crit')):
                        xvalue = ET.SubElement(var,'value')
                        xcontent = ET.SubElement(xvalue,'content')
                        xcontent.text = request.POST.get('varvalue','')
                    else:
                        xvalue = var.find('value')
                    for entry in crits:
                        ET.SubElement(xvalue,'crit',{'name':entry, 'value':request.POST.get(entry)})

            if action == "editcond":
                index = int(request.POST.get('condindex'))
                for var in xvar.xpath('/variables/variable'):
                    for crit in var.xpath('value[%d]/crit'%index):
                        critcode = crit.get('name')
                        crit.set('value',request.POST.get(critcode))
                    
            if action == "delcond":
                index = int(request.POST.get('index'))
                if len(xvar.xpath('/variables/variable[1]/value')) == 1:
                    for xcond in xvar.xpath('/variables/variable/value/crit'):
                        xcond.getparent().remove(xcond)
                else:
                    for xcond in xvar.xpath('/variables/variable/value[%d]'%index):
                        xcond.getparent().remove(xcond)
                    
            if action == "newcrit":
                try:
                    critlist = xvar.xpath('/variables/critlist')[0]
                except IndexError:
                    critlist = ET.SubElement(xvar.xpath('/variables')[0],'critlist')
                critdecl = ET.SubElement(critlist, 'crit')
                critdecl.text = ":" + request.POST.get("crit")
                for xcond in xvar.xpath('/variables/variable/value'):
                    ET.SubElement(xcond, 'crit',{
                        "name":request.POST.get("crit"),                            
                        "value":request.POST.get("val")
                        })
                    
                
        except:
            logger.exception('var action failed')
            
        self.xwrite(xvar, path)
        return HttpResponseRedirect('?path='+path)
#        return self.render_to_response(self.variable_details(path))
        
class VariablesEditvarView(VariablesMixin):
    template_name = "variables/editvar.html"
    def get(self, request):
        path = request.GET.get('path')
        index = int(request.GET.get('index',1)) - 1
        name=path.rsplit('/',1)[1]
        context =  self.variable_details(path, True)
        context.update({
            "method":"line",
            "current":index,
            })
        return self.render_to_response(context)
    

class VariablesEditcolView(VariablesMixin):
    template_name = "variables/editvar.html"
    def get(self, request):
        path = request.GET.get('path')
        index = int(request.GET.get('index', 1)) - 1
        name=path.rsplit('/',1)[1]
        context =  self.variable_details(path, True)
        context.update({
            "method":"col",
            "current":index,
            })
        return self.render_to_response(context)
    
    
class VariablesUploadView(kolektiMixin, TemplateView):
    def post(self, request):
        logger.debug("ods post")
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logger.debug( "form valid")
            uploaded_file = request.FILES[u'upload_file']
            path = request.POST['path']
            converter = OdsToXML(self.request.kolekti_projectpath)
            converter.convert(uploaded_file, path)
            # self.write_chunks(uploaded_file.chunks,path +'/'+ uploaded_file.name) 
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        else:
            return HttpResponse(status=500)

class VariablesCreateView(kolektiMixin, TemplateView):
    def post(self, request):
        try:
            path = request.POST.get('path')
            path = self.set_extension(path, ".xml")
            varx = self.parse_string('<variables><critlist></critlist></variables>')
            self.xwrite(varx, path)
            return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)

class VariablesODSView(kolektiMixin, View):
    def get(self, request):
        path = request.GET.get('path')
        filename = path.rsplit('/',1)[1].replace('.xml','.ods')
        odsfile = StringIO()
        converter = XMLToOds(self.request.kolekti_projectpath)
        converter.convert(odsfile, path)
        response = HttpResponse(odsfile.getvalue(),
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        odsfile.close()
        return response


    
class ImportView(kolektiMixin, TemplateView):
    template_name = "import.html"
    def get(self, request):
        lang = self.request.kolekti_userproject.srclang
        tpls = self.get_directory(root = "/sources/"+lang+"/templates")
        tnames = [t['name'] for t in tpls]
        
        context = self.get_context_data({'templates':tnames})
        return self.render_to_response(context)

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():

            uploaded_file = request.FILES[u'upload_file']
            filename = str(uploaded_file)

            importer = Importer(self.request.kolekti_projectpath, lang=self.request.kolekti_userproject.srclang)
            if(os.path.splitext(filename)[1] == '.ods'):
                events =  importer.importOds(uploaded_file)
            elif(os.path.splitext(filename)[1] == '.xlsx'):
                events =  importer.importXlsx(uploaded_file)
            else:
                import traceback
                events = [{
                'event':'error',
                'msg':"Erreur lors de l'import : type de fichier non supporté %s"%filename,
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
                }]
        else:
            import traceback
            events = [{
                'event':'error',
                'msg':"Erreur lors de l'import : pas de tableur",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }]
        context = self.get_context_data({'events':events})
        return self.render_to_response(context)
            
class ImportTemplateView(kolektiMixin, TemplateView):
    def get(self, request):
        template = request.GET.get('template')
        filename = "import_template.ods"
        odsfile = StringIO()
        tplter = Templater(self.request.kolekti_projectpath)
        tplter.generate("/sources/"+self.request.kolekti_userproject.srclang+"/templates/"+template, odsfile)
        response = HttpResponse(odsfile.getvalue(),                            
                                content_type="application/vnd.oasis.opendocument.spreadsheet")
        response['Content-Disposition']='attachement; filename="%s"'%filename
        odsfile.close()
        return response

    
class SettingsJsView(kolektiMixin, TemplateView):
    def get(self, request):
        project_path = os.path.join(settings.KOLEKTI_BASE, request.user.username,request.kolekti_userproject.project.directory)
        try:
            from kolekti.synchro import SynchroManager
            synchro = SynchroManager(project_path)
            project_svn_url = synchro.geturl()
        except:
            project_svn_url = "N/A"
        settings_js="""
        var kolekti = {
        "lang":"%s",
        "project":"%s",
        "project_svn_url":"%s"
        }
        """%(
            self.request.kolekti_userproject.srclang,
            self.request.kolekti_userproject.project.name,
            self.process_svn_url(project_svn_url))
        return HttpResponse(settings_js,content_type="text/javascript")
    
class SettingsJsonView(kolektiMixin, TemplateView):
    template_name = "settings/list.html"
    def get(self, request):
        context = {
            'kolekti':self._config,
            'kolektiversion' : self._kolektiversion
            }
        if request.kolekti_userproject is not None:
            languages, release_languages, default_srclang = self.project_langs()
            context.update({
                'srclangs' : languages,
                'releaselangs' : release_languages,
                'default_srclang':default_srclang,
                'active_project_name' : self.request.kolekti_userproject.project.name,
                'active_srclang' : self.request.kolekti_userproject.srclang,
            })

        return HttpResponse(json.dumps(context),content_type="application/json")
        

class SettingsView(kolektiMixin, TemplateView):
    template_name = "settings/list.html"

    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)



class PublicationTemplatesView(kolektiMixin, TemplateView):
    template_name = "publication-templates/list.html"




    
class JobCreateView(kolektiMixin, View):
    def post(self, request):        
        try:
            path = request.POST.get('path')
            path = self.set_extension(path, ".xml")
            job = self.parse_string('<job><criteria/><profiles/><scripts/></job>')
            self.xwrite(job, path)
            return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
        

class JobEditView(kolektiMixin, TemplateView):
    template_name = "settings/job.html"

    def get(self, request):
        context = self.get_context_data()
#        context.update({'jobs':self.get_jobs()})
        context.update({'job':self.get_job_edit(request.GET.get('path'))})
        context.update({'path':request.GET.get('path')})
        context.update({'name':self.basename(request.GET.get('path'))})
        return self.render_to_response(context)

    def post(self, request):
        try:
            xjob = self.parse_string(request.body)
            jobpath = request.GET.get('path')
            self.xwrite(xjob, jobpath)
            return HttpResponse('ok')
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)


class CriteriaView(kolektiMixin, View):
    def get(self, request):
        return HttpResponse(self.read('/kolekti/settings.xml'),content_type="text/xml")

class CriteriaCssView(kolektiMixin, TemplateView):
    template_name = "settings/criteria-css.html"
    def get(self, request):
        try:
            settings = self.parse('/kolekti/settings.xml')
            xsl = self.get_xsl('django_criteria_css')
            #print xsl(settings)
            return HttpResponse(str(xsl(settings)), "text/css")
        except:
            import traceback
            print traceback.format_exc()
            
class CriteriaJsonView(kolektiMixin, TemplateView):
    template_name = "settings/criteria-css.html"
    def get(self, request):
        try:
            criterias = self._get_criteria_def_dict()
            return HttpResponse(json.dumps(criterias),content_type="application/json")
        except:
            import traceback
            print traceback.format_exc()
    
                
class CriteriaEditView(kolektiMixin, TemplateView):
    template_name = "settings/criteria.html"

    def get(self, request):
        context = self.get_context_data()
        settings = self.parse('/kolekti/settings.xml')
        criteria = []
        for xcriterion in settings.xpath('/settings/criteria/criterion'):
            criteria.append(
                {'code':xcriterion.get('code'),
                'type':xcriterion.get('type'),
                'values':[str(v.text) for v in xcriterion.findall("value")]
                })
        context.update({'criteria':criteria})
        return self.render_to_response(context)
    def post(self, request):
        try:
            settings = self.parse('/kolekti/settings.xml')
            xcriteria = self.parse_string(request.body)
            xsettingscriteria=settings.xpath('/settings/criteria')[0]
            for xcriterion in xsettingscriteria:
                xsettingscriteria.remove(xcriterion)
                
            for xcriterion in xcriteria.xpath('/criteria/criterion'):
                xsettingscriteria.append(xcriterion)
            self.xwrite(settings, '/kolekti/settings.xml')
            return HttpResponse('ok')
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)
   
class BrowserExistsView(kolektiMixin, View):
    def get(self,request):
        path = request.GET.get('path','/')
        return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")
        
class BrowserMkdirView(kolektiMixin, View):
    def post(self,request):
        path = request.POST.get('path','/')
        self.makedirs(path, sync=True)
        return HttpResponse("",content_type="text/plain")
#        return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")

class BrowserMoveView(kolektiMixin, View):
    def post(self,request):
        src = request.POST.get('from','/')
        dest = request.POST.get('to','/')
        self.move_resource(src, dest)
        return HttpResponse(json.dumps(self.path_exists(dest)),content_type="text/plain")
        #return HttpResponse(,content_type="application/json")

class BrowserCopyView(kolektiMixin, View):
    def post(self,request):
        src = request.POST.get('from','/')
        dest = request.POST.get('to','/')
        self.copy_resource(src, dest)
        return HttpResponse("",content_type="text/plain")
        #return HttpResponse(json.dumps(self.path_exists(path)),content_type="application/json")


class BrowserDeleteView(kolektiMixin, View):
    def post(self,request):
        path = request.POST.get('path','/')
        try:
            self.delete_resource(path)
        except:
            import traceback
            print traceback.format_exc()

        return HttpResponse("",content_type="text/plain")

class BrowserView(kolektiMixin, View):
    template_name = "browser/main.html"
    def __browserfilter(self, entry):
        for exc in settings.RE_BROWSER_IGNORE:
            if re.search(exc, entry.get('name','')):
                return False
        return True

    def release_filter(self, entry):
        if entry.get('type','') == 'text/directory':
            pass
        return entry
            
    def get(self,request):
        try:
            context = self.get_context_data()
            path = request.GET.get('path','/')
            mode = request.GET.get('mode','select')

            files = filter(self.__browserfilter, self.get_directory(path))
        
            for f in files:
                f.update({'icon':fileicons.get(f.get('type'),"fa-file-o")})
                        
            pathsteps = []
            startpath = ""
            for step in path.split("/")[1:]:
                startpath = startpath + "/" + step
                pathsteps.append({'label':step, 'path': startpath})

            context.update({'files':files})
            context.update({'pathsteps':pathsteps})
            context.update({'mode':mode})
            context.update({'path':path})
            context.update({'project':self.request.kolekti_userproject.project.directory})
            context.update({'id':'browser_%i'%random.randint(1, 10000)})
            return self.render_to_response(context)
        except:
            import traceback
            print traceback.format_exc()

class BrowserReleasesView(BrowserView):
    template_name = "browser/releases.html"
    def get_directory(self, path):
        projectdir = self.request.kolekti_userproject.project.directory
#        logger.debug('get releases %s',projectdir)
        if self.syncMgr is not None :
            svn_url = self.syncMgr.geturl()
            if svn_url[:7] == 'file://':
                svn_url = 'https://' + settings.HOSTNAME + '/svn/' + projectdir
        try:
            releases = {}
            res = []
            for assembly, date in self.get_release_assemblies(path):
                item = {'name':assembly,
                        'project':projectdir,
                        'type':"text/xml",
                        'date':date}
                res.append(item)
                try:
                    found = False
                    mf = json.loads(self.read('/'.join([path, assembly, 'release_info.json'])))
                    releasename = mf.get('releasename')
                    releaseindex = mf.get('releaseindex')
                    
                    r = {'name':releaseindex, 'type':"text/xml", 'date':date}
                    try:
                        releases[releasename]['indexes'].append(r)
                    except KeyError:
                        releases[releasename] = {
                            'name':releasename,
                            'type':"text/xml",                                   
                            'date':None,
                            'indexes':[r]}
                        found = True
                except:
                    releases[assembly]=item
                    # logger.exception('release list error')
            # logger.debug(releases)
            return releases.values()
#            return res
        except:
            logger.exception('release list error')
            import traceback
            print traceback.format_exc()
            return super(BrowserReleasesView, self).get_directory(path)
                      
            
class BrowserCKView(kolektiMixin, View):
    template_name = "browser/browser.html"
    def __browserfilter(self, entry):
        for exc in settings.RE_BROWSER_IGNORE:
            if re.search(exc, entry.get('name','')):
                return False
        return True
                         
    def get(self,request):
        context={}
        path = request.GET.get('path','/')
        mode = request.GET.get('mode','select')
        client_filter_name = request.GET.get('filter',None)
        client_filter = None
        if client_filter_name is not None:
            client_filter = getattr(self, client_filter_name)
            
        files = filter(self.__browserfilter, self.get_directory(path,client_filter))

        for f in files:
            f.update({'icon':fileicons.get(f.get('type'),"fa-file-o")})
        pathsteps = []
        startpath = ""
        for step in path.split("/")[1:]:
            startpath = startpath + "/" + step
            pathsteps.append({'label':step, 'path': startpath})
        context.update({'files':files})
        context.update({'pathsteps':pathsteps})
        context.update({'mode':mode})
        context.update({'path':path})
        context.update({'editor':request.GET.get('CKEditor','_')})
        context.update({'funcnum':request.GET.get('CKEditorFuncNum','_')})
        
        context.update({'id':'browser_%i'%random.randint(1, 10000)})
        return self.render_to_response(context)

class BrowserCKUploadView(kolektiMixin, View):
    template_name = "browser/main.html"

class BrowserUploadView(kolektiMixin, TemplateView):
    def post(self, request):
        try:
            path = request.POST['path']
            name = request.POST['name']
            payload = request.POST['file']
            data = base64.decodestring(payload)
            self.write(data, path + "/" + name, mode="wb")
            return HttpResponse(json.dumps("ok"),content_type="text/javascript")
        except:
            import traceback
            print traceback.format_exc()
            return HttpResponse(status=500)


    
class PublicationView(kolektiMixin, View):
    template_name = "publication.html"
    def __init__(self, *args, **kwargs):
        super(PublicationView, self).__init__(*args, **kwargs)
#        self.loggerstream = StringIO()
#        import logging
#        self.loghandler = logging.StreamHandler(stream = self.loggerstream)
#        self.loghandler.setLevel(logging.WARNING)
        # set a format which is simpler for console use
#        formatter = logging.Formatter('%(levelname)-8s ; %(message)s\n')
        # tell the handler to use this format
#        self.loghandler.setFormatter(formatter)
#        # add the handler to the root logger
#        rl = logging.getLogger('')
#        rl.addHandler(self.loghandler)

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(PublicationView, cls).as_view(**initkwargs)
        return condition(etag_func=None)(view)

class DraftView(PublicationView):
    def post(self,request):
        tocpath = request.POST.get('toc')
        jobpath = request.POST.get('job')
        pubdir  = request.POST.get('pubdir')
        pubtitle= request.POST.get('pubtitle')
        profiles = request.POST.getlist('profiles[]',[])
        scripts = request.POST.getlist('scripts[]',[])
        context={}
        xjob = self.parse(jobpath)
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
                else:
                    jprofile.set('enabled',"1")
            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.find('label').text in scripts:
                    jscript.getparent().remove(jscript)
                else:
                    jscript.set('enabled',"1")

            xjob.getroot().set('pubdir',pubdir)

            p = publish.DraftPublisher(self.request.kolekti_projectpath, lang=self.request.kolekti_userproject.srclang)
            return StreamingHttpResponse(self.format_iterator(p.publish_draft(tocpath, xjob, pubtitle)), content_type="text/html")

        except:
            import traceback
#            self.loghandler.flush()
#            print self.loggerstream
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})

            return self.render_to_response(context)
        
class ReleaseView(PublicationView):
    def post(self,request):
        tocpath = request.POST.get('toc')
        jobpath = request.POST.get('job')
        release_name  = request.POST.get('release_name')
        release_index  = request.POST.get('release_index')
        release_prev_index  = request.POST.get('release_prev_index')
        pubdir  = "%s_%s"%(release_name, release_index)
                
#        pubtitle= request.POST.get('pubtitle')

        
        profiles = request.POST.getlist('profiles[]',[])

        # print profiles
        scripts = request.POST.getlist('scripts[]',[])
        context={}
        xjob = self.parse(jobpath)
        
        try:
            for jprofile in xjob.xpath('/job/profiles/profile'):
#                logger.debug(ET.tostring(jprofile))
                if not jprofile.find('label').text in profiles:
                    jprofile.getparent().remove(jprofile)
                else:
                    jprofile.set('enabled',"1")

            for jscript in xjob.xpath('/job/scripts/script'):
                if not jscript.find('label').text in scripts:
                    jscript.getparent().remove(jscript)
                else:
                    jscript.set('enabled',"1")

            xjob.getroot().set('pubdir',pubdir)
            xjob.getroot().set('releasename',release_name)
            xjob.getroot().set('releaseindex',release_index)
            if not (release_prev_index is None):
                xjob.getroot().set('releaseprevindex',release_prev_index)
                        
            return StreamingHttpResponse(self.format_iterator(self.release_iter(self.request.kolekti_projectpath, tocpath, xjob)))
#            r = publish.Releaser(projectpath, lang=self.request.kolekti_userproject.srclang)
#            pp = r.make_release(tocpath, xjob)
            

#            release_dir = pp[0]['assembly_dir']
            
#            p = publish.ReleasePublisher(projectpath, langs=[self.request.kolekti_userproject.srclang])
#            return StreamingHttpResponse(self.format_iterator(p.publish_assembly(release_dir, pp[0]['pubname'])), content_type="text/html")

        except:
            import traceback
            print traceback.format_exc()
#            self.loghandler.flush()
            context.update({'success':False})
#            context.update({'logger':self.loggerstream.getvalue()})        
            context.update({'stacktrace':traceback.format_exc()})
            
            return self.render_to_response(context)

    def release_iter(self, projectpath, tocpath, xjob):
        lang=self.request.kolekti_userproject.srclang
        r = publish.Releaser(projectpath, lang = lang)
        pp = r.make_release(tocpath, xjob)
        release_dir = pp[0]['assembly_dir'][:-1]
        yield {
            'event':'release',
            'ref':release_dir,
            'releasedir':pp[0]['releasedir'],
            'time':pp[0]['datetime'],
            'lang':lang,
        }
        
        if self.syncMgr is not None :
            self.syncMgr.propset("release_state","sourcelang","/".join([release_dir,"sources",lang,"assembly",pp[0]['releasedir']+'_asm.html']))
        p = publish.ReleasePublisher(release_dir, projectpath, langs=[self.request.kolekti_userproject.srclang])
        for e in p.publish_assembly(pp[0]['pubname']):
            yield e
        
            
class TopicEditorView(kolektiMixin, View):
    template_name = "topics/edit-ckeditor.html"
    def get(self, request):
        topicpath = request.GET.get('topic')
        topic = self.get_topic_edit(topicpath)
        context = self.get_context_data({"body":topic,
                                         "title": self.basename(topicpath),
#                                         "meta":topicmeta
                                         })
        return self.render_to_response(context)

    def post(self,request):
        try:
            path = request.GET['topic']
            topic = request.body
            xtopic = self.parse_string(topic)

            self.write(topic, path)
            return HttpResponse(json.dumps({'status':'ok'}), content_type="application/json")

        except:
            logger.exception('invalid topic structure')
            import traceback
            msg = traceback.format_exc().split('\n')[-2]
            return HttpResponse(json.dumps({'status':'error', 'msg':msg}), content_type="application/json")

class TopicMetaJsonView(kolektiMixin, View):
    def get(self, request):
        path=request.GET['topic']
        xtopic = self.parse(path.replace('{LANG}',self.request.kolekti_userproject.srclang))
        metaelts = xtopic.xpath('/h:html/h:head/h:meta[@name][@content]',namespaces={'h':'http://www.w3.org/1999/xhtml'})
        meta = [{'name':m.get('name'),'content':m.get('content')} for m in metaelts]
        return HttpResponse(json.dumps(meta), content_type="application/json")
    
class TopicCreateView(kolektiMixin, View):
    template_name = "home.html"
    def post(self, request):
        try:
            modelpath = '/sources/'+ self.request.kolekti_userproject.srclang + "/templates/" + request.POST.get('model')
            topicpath = request.POST.get('topicpath')
            topicpath = self.set_extension(topicpath, ".html")
            topic = self.parse(modelpath)
            self.xwrite(topic, topicpath)
        except:
            import  traceback
            print traceback.format_exc()
        return HttpResponse(json.dumps(topicpath), content_type="application/json")

class TopicTemplatesView(kolektiMixin, View):
    def get(self, request):
        lang = request.GET.get('lang')
        tpls = self.get_directory(root = "/sources/"+lang+"/templates")
        tnames = [t['name'] for t in tpls]
        return HttpResponse(json.dumps(tnames),content_type="application/json")

class TocUsecasesView(kolektiMixin, View):
    def get(self, request):
        pathes = request.GET.getlist('pathes[]',[])
        context={}
        for toc in self.itertocs:
            xtoc=self.parse(toc)
            for path in pathes:
                if len(xtoc.xpath('//html:a[@href="%s"]'%path,namespaces={'html':'http://www.w3.org/1999/xhtml'})):
                    try:
                        context[path].append(toc)
                    except:
                        context[path]=[toc]
        return HttpResponse(json.dumps(context),content_type="application/json")


class SearchFormView(kolektiMixin, TemplateView):
    template_name = "search/form.html"
    def get(self, request):
        context = self.get_context_data()
        form = SearchForm()
        context.update({'form':form})
        return self.render_to_response(context)
    
class SearchView(kolektiMixin, View):
    template_name = "search/results.html"
    def get(self, request, page=1):
        context = self.get_context_data()
        return self.render_to_response(context)
    
    def post(self, request, page=1):
        context = self.get_context_data()
        q = request.GET.get('query')
        s = Searcher(self.request.kolekti_projectpath)
        results = s.search(q, page)
        context.update({"results":results})
        context.update({"page":page})
        context.update({"query":q})
        return self.render_to_response(context)



class SyncView(kolektiMixin, View):
    template_name = "synchro/main.html"
    def get(self, request):
        context = self.get_context_data()
        try:
            from kolekti.synchro import SynchroManager
            sync = SynchroManager(self.request.kolekti_projectpath)
            context.update({
                    "history": sync.history(),
                    "changes": sync.statuses(),
                    })
        except ExcSyncNoSync:
            logger.exception("Synchro unavailable")
            context.update({'status':'nosync'})
        return self.render_to_response(context)

    def post(self, request):
        from kolekti.synchro import SynchroManager
        sync = SynchroManager(self.request.kolekti_projectpath, username = request.user.username)
        action = request.POST.get('action')
        commitmsg = request.POST.get('commitmsg',u"").encode('utf-8')
        if len(commitmsg) == 0:
            commitmsg = "unspecified"
        if action == "conflict":
            resolve = request.POST.get('resolve')
            files = request.POST.getlist('fileselect',[])
            if resolve == "local":
                sync.update(files)
                for file in files:
                    if self.exists(file+'.mine'):
                        self.copyFile(file+'.mine', file)
                    else:
                        raise Exception('impossible de trouver la version locale')
                    try:
                        sync.resolved(file)
                    except:
                        logger.exception('error while resolving conflict [use local]')
                        
                sync.commit(files, commitmsg)
            if resolve == "remote":
                try:
                    sync.revert(files)
                except:
                    logger.exception('impossible to revert')
                sync.update(files)

        elif action == "merge":
            resolve  = request.POST.get('resolve',None)
            files = request.POST.getlist('fileselect',[])
            if resolve =="merge":
                sync.update(files)
                sync.commit(files,commitmsg)
            if resolve == "remote":
                sync.revert(files)
                
        elif action == "update":
            sync.update_all()
            
        elif action == "commit":
            resolve = request.POST.get('resolve')
            files = request.POST.getlist('fileselect',[])
            if resolve == "commit":
                sync.update_all()
                sync.commit(files,commitmsg)
            else:
                sync.revert(files)
            
        return self.get(request)
                    
class SyncRevisionView(kolektiMixin, View):
    template_name = "synchro/revision.html"
    def get(self, request, rev):
        from kolekti.synchro import SynchroManager
        sync = SynchroManager(self.request.kolekti_projectpath)
        revsumm, revinfo, difftext = sync.revision_info(rev)
        context = self.get_context_data({
            "history": sync.history(),
            'revsumm':revsumm,
            'revinfo':revinfo,
            'difftext':difftext,
            })
        
        return self.render_to_response(context)




class SyncDiffView(kolektiMixin, View):
    template_name = "synchro/diff.html"
    def get(self, request):
        entry = request.GET.get("file")
        from kolekti.synchro import SynchroManager
        sync = SynchroManager(self.request.kolekti_projectpath)
        diff,  headdata, workdata = sync.diff(entry) 
        import difflib
        #htmldiff = hd.make_table(headdata.splitlines(), workdata.splitlines())
        context = self.get_context_data({
            'diff':difflib.ndiff(headdata.splitlines(), workdata.splitlines()),
            'headdata':headdata,
            'workdata':workdata,
#            'htmldiff':htmldiff,
            })
        
        return self.render_to_response(context)

class SyncStatusView(kolektiMixin, View):
    def get(self, request):
        try:
            from kolekti.synchro import SynchroManager
            sync = SynchroManager(self.request.kolekti_projectpath)
            states = dict(sync.rev_state())
            return HttpResponse(json.dumps(states),content_type="application/json")
        except:
            logger.exception("Unable to get project sync status")
            return HttpResponse(json.dumps({'revision':{'status':'E'}}),content_type="application/json")

class SyncRemoteStatusView(kolektiMixin, View):
    def get(self, request):
        try:
            return HttpResponse(json.dumps(self._syncnumber),content_type="application/json")
        except:
            logger.exception("Unable to get project remote sync status")
            return HttpResponse(json.dumps({'revision':{'number':'!'}}),content_type="application/json")
            
class SyncResStatusView(kolektiMixin, View):
    def get(self, request):
        try:
            path = request.GET.get("path")
            from kolekti.synchro import SynchroManager
            sync = SynchroManager(self.request.kolekti_projectpath)
            state = sync.statuses(path, recurse = False)
            return HttpResponse(json.dumps(state),content_type="application/json")
        except:
            logger.exception("Unable to get file sync status : %s"%path)
            return HttpResponse(json.dumps({'revision':{'status':'E'}}),content_type="application/json")

class SyncAddView(kolektiMixin, View):
    def post(self, request):
        try:
            from kolekti.synchro import SynchroManager
            sync = SynchroManager(self.request.kolekti_projectpath)
            path = request.POST.get('path')
            sync.add_resource(path)
            return HttpResponse(json.dumps('ok'),content_type="application/json")
        except:
            logger.exception("Unable to add file to synchro : %s"%path)
                        
class SyncRemoveView(kolektiMixin, View):
    def post(self, request):
        try:
            from kolekti.synchro import SynchroManager
            sync = SynchroManager(self.request.kolekti_projectpath)
            path = request.POST.get('path')
            sync.remove_resource(path)
            return HttpResponse(json.dumps('ok'),content_type="application/json")
        except:
            logger.exception("Unable to remove file to synchro : %s"%path)
                        
class projectStaticView(kolektiMixin, View):
    def get(self, request, path):
        return serve(request, path, self.request.kolekti_projectpath)

class ProjectHistoryView(kolektiMixin, View):
    def get(self, request):
        try:
            from kolekti.synchro import SynchroManager
            sync = SynchroManager(self.request.kolekti_projectpath)
            hist = sync.history()
            hisrecords = [{"timestamp":r.date,"date":r.date,"user":r.author,"message":r.message,"rev":r.revision.number} for r in hist] 
            return HttpResponse(json.dumps(hisrecords),content_type="application/json")
        except:
            logger.exception("Unable to get project history")


    
class WidgetView(kolektiMixin, View):
    def get(self, request):
        context = self.get_context_data()
        return self.render_to_response(context)    


class WidgetSearchView(WidgetView):
    template_name = "widgets/search.html"
    def get(self, request):
        context = self.get_context_data()
        form = SearchForm()
        context.update({'form':form})
        return self.render_to_response(context)

    def post(self, request, page=1):
        context = self.get_context_data()
        q = request.POST.get('query')

        projectspath = os.path.join(settings.KOLEKTI_BASE, request.user.username)
        project = self.request.kolekti_userproject.project.directory
        
        s = Searcher(projectspath, project)
        results = s.search(q, page)
        context.update({"results":results})
        context.update({"page":page})
        context.update({"query":q})
        return self.render_to_response(context)

    
class WidgetProjectHistoryView(WidgetView):
    template_name = "widgets/project-history.html"
    def get_context_data(self):
        try:
            from kolekti.synchro import SynchroManager
            sync = SynchroManager(self.request.kolekti_projectpath)
            return super(WidgetProjectHistoryView, self).get_context_data({
                'history':sync.history()
                })
        except:
            logger.exception("Unable to get project history")


class WidgetPublicationsListView(kolektiMixin, View):
    template_name = "widgets/publications.html"
    
    def get(self, request):
        context = {
            "publications": [p for p in sorted(self.get_publications(), key = lambda a: a['time'], reverse = True) ]
        }
        return self.render_to_response(context)

class WidgetReleasePublicationsListView(kolektiMixin, View):
    template_name = "widgets/publications.html"

    def get(self, request):
        context = {
            "publications": [p for p in sorted(self.get_releases_publications(), key = lambda a: a['time'], reverse = True) ]
        }
        return HttpResponse(json.dumps(context),content_type="application/json")
        return self.render_to_response(context)

          
