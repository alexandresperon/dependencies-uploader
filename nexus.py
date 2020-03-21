from utils import last_attached_file
from requests.auth import HTTPBasicAuth
import os.path as path
import requests

def nexus_postform(minfo, repo_url, repo_id, auth, form_params, files):
    url = "%s/%s" % (repo_url, 'service/rest/v1/components?repository=' + repo_id)
    req = requests.post(url, files=files, auth=auth, data=form_params)
    if req.status_code > 299:
        print "Error communicating with Nexus!",
        print "code=" + str(req.status_code) + ", msg=" + req.content
    else:
        print "Successfully uploaded: " + last_attached_file(minfo)

def nexus_upload(maven_info, repo_url, repo_id, credentials=None, force=False):
    def encode_file(asset_number, basename):
        fullpath = path.join(maven_info['path'], basename)
        return ('maven2.asset' + str(asset_number), (basename, open(fullpath, 'rb')))

    files = []
    payload = { 'maven2.groupId':maven_info['g'], 'maven2.artifactId':maven_info['a'], 'maven2.version':maven_info['v'] }
    auth = None
    if credentials is not None:
        auth = HTTPBasicAuth(credentials[0], credentials[1])

    n = 1
    if 'pom' in maven_info:
        files.append(encode_file(n, maven_info['pom']))
        payload['maven2.asset' + str(n) + '.extension'] = 'pom'
        n = n + 1

    if 'jar' in maven_info:
        files.append(encode_file(n, maven_info['jar']))
        payload['maven2.asset' + str(n) + '.extension'] = 'jar'
        n = n + 1

    if 'ear' in maven_info:
        files.append(encode_file(n, maven_info['ear']))
        payload['maven2.asset' + str(n) + '.extension'] = 'ear'
        n = n + 1

    if 'war' in maven_info:
        files.append(encode_file(n, maven_info['war']))
        payload['maven2.asset' + str(n) + '.extension'] = 'war'
        n = n + 1

    if 'classes' in maven_info:
        files.append(encode_file(n, maven_info['classes']))
        payload['maven2.asset' + str(n) + '.classifier'] = 'classes'
        payload['maven2.asset' + str(n) + '.extension'] = 'jar'
        n = n + 1

    if 'source' in maven_info:
        files.append(encode_file(n, maven_info['source']))
        payload['maven2.asset' + str(n) + '.classifier'] = 'sources'
        payload['maven2.asset' + str(n) + '.extension'] = 'jar'
        n = n + 1

    if 'docs' in maven_info:
        files.append(encode_file(n, maven_info['docs']))
        payload['maven2.asset' + str(n) + '.classifier'] = 'javadoc'
        payload['maven2.asset' + str(n) + '.extension'] = 'jar'
        n = n + 1
    
    if n != 1:
        nexus_postform(maven_info, repo_url, auth=auth, repo_id=repo_id, form_params=payload, files=files)
    else:
        print "No files to upload"
