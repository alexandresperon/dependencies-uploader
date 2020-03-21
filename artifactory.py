from utils import last_attached_file
from requests.auth import HTTPBasicAuth
import os.path as path
import requests

art_types = ['ear', 'war', 'pom', 'jar', 'classes', 'source', 'docs']

def to_path(string):
    return string.replace('.', path.sep)

def to_url(string):
    return string.replace(path.sep, '/')

def artifactory_postform(minfo, repo_url, repo_id, auth, artifact, art_file):
    artifact_name = artifact.rsplit(path.sep, 1)[1]
    repo_path = to_url(path.join('artifactory', repo_id, to_path(minfo['g']), minfo['a'], minfo['v'], artifact_name))
    url = "%s/%s" % (repo_url, repo_path)
    headers = {'Content-type': 'application/octet-stream'}
    with open(art_file, 'rb') as fh:
        req = requests.put(url, data=fh.read(), auth=auth, headers=headers)
    if req.status_code > 299:
        print "Error communicating with Artifactory!",
        print "code=" + str(req.status_code) + ", msg=" + req.content
    else:
        print "Successfully uploaded: " + artifact_name

def artifactory_upload(maven_info, repo_url, repo_id, credentials=None, force=False):
    def encode_file(basename):
        return path.join(maven_info['path'], basename)

    auth = None
    if credentials is not None:
        auth = HTTPBasicAuth(credentials[0], credentials[1])

    for art_type in art_types:
        if art_type in maven_info:
            art_file = encode_file(maven_info[art_type])
            artifactory_postform(maven_info, repo_url, auth=auth, repo_id=repo_id, artifact=maven_info[art_type], art_file=art_file)