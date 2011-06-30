from commands import getoutput

SUPPORTED_PLATFORMS = ['pivotal',
                       ]

def feature():
    platform = getoutput('git config --get bushy.platform')
    platform = platform.strip()

    if platform not in SUPPORTED_PLATFORMS:
        raise NotImplementedError('The platform %s is not supported, please update your configuration with one of the following platforms: %s' % (platform, ', '.join(SUPPORTED_PLATFORMS)))
    
    api = __import__('bushy._%s' % platform, fromlist=['Feature'])
    
    command = api.Feature()
    return command()

def bug():
    platform = getoutput('git config --get bushy.platform')
    platform = platform.strip()

    if platform not in SUPPORTED_PLATFORMS:
        raise NotImplementedError('The platform %s is not supported, please update your configuration with one of the following platforms: %s' % (platform, ', '.join(SUPPORTED_PLATFORMS)))
    
    api = __import__('bushy._%s' % platform, fromlist=['Bug'])

    command = api.Bug()
    return command()

def finish():
    platform = getoutput('git config --get bushy.platform')
    platform = platform.strip()

    if platform not in SUPPORTED_PLATFORMS:
        raise NotImplementedError('The platform %s is not supported, please update your configuration with one of the following platforms: %s' % (platform, ', '.join(SUPPORTED_PLATFORMS)))
    
    api = __import__('bushy._%s' % platform, fromlist=['Finish'])

    command = api.Finish()
    return command()

