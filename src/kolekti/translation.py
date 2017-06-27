# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import os
import json
from zipfile import ZipFile

import mimetypes
mimetypes.init()

from lxml import etree as ET
import logging
logger = logging.getLogger(__name__)

from django.utils.text import get_valid_filename

from publish_utils import PublisherMixin, PublisherExtensions, ReleasePublisherExtensions
from .common import kolektiTests, XSLExtensions, LOCAL_ENCODING, KolektiValidationError
from kolekti import plugins
from .synchro import SynchroManager

logger = logging.getLogger(__name__)

class TranslationImporter(kolektiTests):

    html = "{http://www.w3.org/1999/xhtml}"

    def __init__(self, *args, **kwargs):
        super(TranslationImporter, self).__init__(*args, **kwargs)
    
    def __get_path(self, path, release, lang):
        pathparts = path.split('/')
        try:
            return path.split('sources/%s/'%lang)[1]
        except IndexError:
            raise KolektiValidationError('wrong path in zip file')
        
    def __checkfile(self, filepath, filec, importfiletype, release, lang):
        logger.debug('checkfile %s %s',filepath, importfiletype)
        projectfile = filepath
        if '/' in filepath:
            projectfile = self.__get_path(filepath, release, lang)
        if importfiletype in ("text/html", "text/xml", "application/xml"):
            try:
                xml = ET.fromstring(filec)
            except:
                raise KolektiValidationError('xml parse error')
            logger.debug(xml.tag)
            # test if assembly
            if xml.tag == self.html + 'html':
                self.test_xml(xml,"assembly")
                
                projectfile = "/releases/" + release + '/sources/' + lang +'/assembly/' + release +'_asm.html'
                xhead = xml.xpath('/h:html/h:head', namespaces = self.namespaces)[0]
                xbody = xml.xpath('/h:html/h:body', namespaces = self.namespaces)[0]
                xbody.set('lang', lang)
                xbody.set('{http://www.w3.org/XML/1998/namespace}lang', lang)
                try:
                    xmetalang = xml.xpath('/h:html/h:html/h:meta[@name="LANG"][@scheme="condition"]',
                                              namespaces = self.namespaces)[0]
                    xmetalang.set('content',lang)
                except IndexError:
                    ET.SubElement(xhead, '{http://www.w3.org/1999/xhtml}meta', {"scheme":"condition","name":"LANG","content":lang})
                self.makedirs(self.dirname(projectfile))
                self.xwrite(xml, projectfile, pretty_print=False, sync = False)
                
            if xml.tag == 'variables':
                self.test_xml(xml,'variables')
                projectfile = "/releases/" + release + '/sources/' + lang + '/' + projectfile
                self.makedirs(self.dirname(projectfile))
                logger.debug(projectfile)
                self.write(filec, projectfile, sync = False)
                
        if importfiletype[:6] == "image":
            projectfile = "/releases/" + release + '/sources/' + lang + '/' + projectfile
            self.makedirs(self.dirname(projectfile))
            self.write(filec, projectfile, sync = False)
        logger.debug(projectfile)
        return projectfile

    
    def import_files(self, path, importfile, importfiletype, release, lang):
        logger.debug("%s/%s %s", path, importfile, importfiletype)
        files = []
        
        if importfiletype == "application/zip":
            z = ZipFile(os.path.join(path, importfile))
            for ifilename in z.namelist():
                logger.debug(ifilename)
                ifilec = z.read(ifilename)
                filetype = mimetypes.guess_type(ifilename)[0]
                projectfile = self.__checkfile(ifilename, ifilec, filetype, release, lang)
                files.append(projectfile)
                #self.write(ifilec, projectfile, "wb", sync = False)
        else:
            with open(os.path.join(path, importfile)) as f:
                ifilec = f.read() 
            projectfile = self.__checkfile(importfile, ifilec, importfiletype, release, lang)
            files.append(projectfile)
            #self.write(ifilec, projectfile, "wb", sync = False)
        return files


    def commit(self, files):
        pass

    def rollback(self, files):
        pass


class AssemblyImporter(object):
    namespaces = {'h':'http://www.w3.org/1999/xhtml'}
    def __init__(self, path, username):
        self._path = path
        self._username = username 

        
    def _get_source_lang(self, project, release):
        release_dir = os.path.join(self._path, self._username, project, 'releases', release)
        syncmgr = SynchroManager(release_dir, self._username)
        for l in os.listdir(os.path.join(self._path, self._username, project, 'releases', release, 'sources')):
            if l == 'share':
                continue
            try:
                assembly_file = "sources/%(lang)s/assembly/%(release)s_asm.html"%{
                    'lang': l,
                    'release': release
                    }
                state = syncmgr.propget("release_state",assembly_file)
                if state=="sourcelang":
                    return l
            except:
                logger.exception('could not get lang state')
                continue

    def _check_attribute(self, elta, attr):
        attr = attr.replace('{http://www.w3.org/XML/1998/namespace}','')
        if attr == "content" and elta.xpath('local-name()="meta" and @name="LANG" and @scheme ="condition"'):
            return False
        if attr == "lang" and elta.xpath('local-name()="body"'):
            return False
        if attr == "xml:lang" and elta.xpath('local-name()="body"'):
            return False
        return True
        
    def _compare_attributes(self, elta, eltb):
        for attr,val in elta.attrib.iteritems():
            if self._check_attribute(elta, attr):
                if eltb.get(attr) != val:
                    raise KolektiValidationError('structure does not match [attributes] [%s]'%attr)
                

            
    def _iter_structures(self, elta, eltb):
        taga = elta.xpath('local-name()')
        tagb = eltb.xpath('local-name()')
        if taga != tagb:
            raise KolektiValidationError('structure does not match')

        self._compare_attributes(elta, eltb)
        
        if taga == "div":
            if elta.get('class') =='topic':
                return 
        for subelta, subeltb in zip(elta, eltb):
            self._iter_structures(subelta, subeltb)
        
    def check_structure(self, project, assembly, release) :
        srclang = self._get_source_lang(project, release)
        logger.debug(srclang)
        src_assembly_file = os.path.join(self._path, self._username, project, 'releases', release, "sources", srclang, "assembly", release+"_asm.html")
        src_assembly = ET.parse(src_assembly_file)
        try :
            src_assembly = src_assembly.getroot()
        except AttributeError:
            pass
        try :
            assembly = assembly.getroot()
        except AttributeError:
            pass
        self._iter_structures(src_assembly, assembly)



    def check_variables(self, project, assembly, release) :
        pass
    
    def fix_topic_sources(self, project, assembly, release) :
        pass
    
    def fix_links(self, project, assembly, release) :
        pass
    
    def guess_project(self, assembly):
        try:
            project = assembly.xpath('/h:html/h:head/h:meta[@name="kolekti.project"]/@content', namespaces=self.namespaces)[0]
        except:
            logger.exception('project meta not found')
            raise KolektiValidationError('could not detect project')

        if not os.path.exists(os.path.join(self._path, self._username, project)):
            raise KolektiValidationError('project directory does not exists')
        
        return project
    
    def guess_release(self, assembly, project):
        # get assembly dir
        try:
            release = assembly.xpath('/h:html/h:head/h:meta[@name="kolekti.releasedir"]/@content', namespaces=self.namespaces)[0]
        except:
            logger.exception('release name not found')
            raise KolektiValidationError('could not detect release name')

        if not os.path.exists(os.path.join(self._path, self._username, project, 'releases', release)):
            raise KolektiValidationError('release directory does not exists')            
        return release
    
    def import_assembly(self, assembly_src):
        # xml parse
        try:
            assembly = ET.fromstring(assembly_src)
        except:
            logger.exception('Assembly parse error')
            raise KolektiValidationError('xml parse error')

        # check lang
        try:
            lang = assembly.xpath('/h:html/h:body/@lang|/h:html/h:body/@xml:lang', namespaces=self.namespaces)[0]
        except:
            logger.exception('language not found')
            raise KolektiValidationError('could not detect language')
        
        project = self.guess_project(assembly)
        release = self.guess_release(assembly, project)
        if not os.path.exists(os.path.join(self._path, self._username, project, 'releases', release , 'sources', lang)):
            raise KolektiValidationError('language directory does not exists')
        

        release_dir = os.path.join(self._path, self._username, project, 'releases', release)
        assembly_dir = os.path.join(release_dir, 'sources', lang, 'assembly')
        assembly_file = '/'.join(['sources', lang, 'assembly', release + '_asm.html'])
        syncmgr = SynchroManager(release_dir, self._username)
        
        try:
            state = syncmgr.propget("release_state", assembly_file)
        except:
            logger.exception('import release state')
            raise KolektiValidationError('could not get release state')

        if not (state == 'translation' or state == 'validation'):
                raise KolektiValidationError('release state does not allow update of translation')

        self.check_structure(project, assembly, release)
        self.check_variables(project, assembly, release)            
        self.fix_topic_sources(project, assembly, release)
        self.fix_links(project, assembly, release)

        with open(os.path.join(self._path, self._username, project, 'releases', release , 'sources', lang, 'assembly', release+"_asm.html"), 'w') as f:
            f.write(ET.tostring(assembly, encoding='utf-8'))
        return {'project':project, 'release': release, 'lang':lang}
        
# command line
    
def cmd_compare(args):
    """ compare two assembly, runs in a relase directory
    args : (.lang) language of the assembly to compare to sourcelang
    """
    projectdir = os.path.dirname(os.path.dirname(os.getcwd()))
    release = os.path.basename(os.getcwd())
    importer = TranslationImporter(projectdir)
    assembly = importer.parse('releases/%(release)s/sources/%(lang)s/assembly/%(release)s_asm.html'% {
        'release':release,
        'lang':args.lang
        })
    importer.check_structure(assembly, release)

def cmd_import(args):
    """ import a assembly in a project
    args : object with assembly and project attributes
    """
    ti = TranslationImporter(args.project)
    with open(args.assembly) as f:
        assembly = f.read()
    ti.import_assembly(assembly)
    
def main():
    import argparse
    from django.conf import settings

    
    argparser = argparse.ArgumentParser()
    subparsers = argparser.add_subparsers(title='commands')
    parser_compare = subparsers.add_parser('compare', help="compare assembly structure to source lang")
    parser_compare.add_argument('lang', action="store")
    defaults = {'cmd':'compare'}
    parser_compare.set_defaults(**defaults)

    parser_import = subparsers.add_parser('import', help="import assembly in project")
    parser_import.add_argument('assembly', action="store")
    parser_import.add_argument('project', action="store")
    defaults = {'cmd':'import'}
    parser_import.set_defaults(**defaults)
    
    args = argparser.parse_args()
    
    if args.cmd == 'compare':
        cmd_compare(args)

    if args.cmd == 'import':
        cmd_import(args)
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
