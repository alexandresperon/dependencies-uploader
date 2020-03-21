import os
import os.path as path
import sys
import argparse
from nexus import nexus_upload
from artifactory import artifactory_upload

def list_files(root, ffilter = lambda x: True, recurse = True):
    """ list all files matching a filter in a given dir with optional recursion. """
    for root, subdirs, files in os.walk(root):
        for f in filter(ffilter, files):
            yield path.join(root, f)[:-4]
        if recurse:
            for sdir in subdirs:
                for f in list_files(sdir, ffilter, recurse):
                    yield f

def is_valid(file):
    """ checks if the specific maven file is a valid one """
    if(os.path.getsize(file) < 2000):
        with open(file, 'r') as f:
            line = f.readline()
            if '#NOTE' in line:
                    return False
    return True

def m2_maven_info(root):
    """ walks an on-disk m2 repo yielding a dict of pom/gav/jar info. """
    for f in set(list_files(root, lambda x: x[-3:] in ["pom","ear","war","jar"] and x[-11:] not in ["javadoc.jar","sources.jar"])):
        rpath = path.dirname(f).replace(root, '')
        rpath_parts = filter(lambda x: x != '', rpath.split(os.sep))
        info = { 'path': path.dirname(f) }
        info['g'] = '.'.join(rpath_parts[:-2])
        info['a'] = rpath_parts[-2:-1][0]
        info['v'] = rpath_parts[-1:][0]

        # check pom
        pomfile = f + '.pom'
        if path.isfile(pomfile) and is_valid(pomfile):
            info['pom'] = pomfile
        # check for jar
        jarfile = f + '.jar'
        if path.isfile(jarfile) and is_valid(jarfile):
            info['jar'] = jarfile
        # check for ear
        earfile = f + '.ear'
        if path.isfile(earfile) and is_valid(earfile):
            info['ear'] = earfile
        # check for war
        warfile = f + '.war'
        if path.isfile(warfile) and is_valid(warfile):
            info['war'] = warfile
        # check for sources
        sourcejar = f + '-sources.jar'
        if path.isfile(sourcejar) and is_valid(sourcejar):
            info['source'] = sourcejar
        # check for javadoc
        docjar = f + '-javadoc.jar'
        if path.isfile(docjar) and is_valid(docjar):
            info['docs'] = docjar
        # check for classes
        classesjar = f + '-classes.jar'
        if path.isfile(classesjar) and is_valid(classesjar):
            info['classes'] = classesjar
        yield info

def gav(info):
    return (info['g'], info['a'], info['v'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Easily upload multiple artifacts to a remote server.')
    parser.add_argument('repodirs', type=str, nargs='+',
                        help='list of repodirs to scan')
    parser.add_argument('--repo-id', type=str, help='Repository ID to u/l to.', required=True)
    parser.add_argument('--auth',type=str, help='basicauth credentials in the form of username:password.')
    parser.add_argument('--include-artifact','-ia', type=str, metavar='REGEX', help='regex to apply to artifactId')
    parser.add_argument('--include-group', '-ig', type=str, metavar='REGEX', help='regex to apply to groupId')
    parser.add_argument('--force-upload', '-F', action='store_true', help='force u/l even if artifact exists.')
    parser.add_argument('--repo-url', type=str, required=True, 
                        help="Repo URL (e.g. http://localhost:8081)")

    args = parser.parse_args()
    
    import re
    igroup_pat = None
    iartifact_pat = None
    if args.include_group:
        igroup_pat = re.compile(args.include_group)
    if args.include_artifact:
        iartifact_pat = re.compile(args.include_artifact)

        
    for repo in args.repodirs:
        print "Uploading content from [%s] to %s repo on %s" % (repo, args.repo_id, args.repo_url)
        for info in m2_maven_info(repo):
            if igroup_pat and not igroup_pat.search(info['g']):
                continue

            if iartifact_pat and not iartifact_pat.search(info['a']):
                continue
            
            print "\nProcessing: %s" % (gav(info),)
            artifactory_upload(info, args.repo_url, args.repo_id, credentials=tuple(args.auth.split(':')), force=args.force_upload)