def last_attached_file(minfo):
    return "%s/%s/%s" % (minfo['g'].replace('.','/'), minfo['a'], minfo['v'])