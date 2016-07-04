import json


def _conda_return(name, output):
    ret = {
        'name': name,
        'changes': {},
        'comment': '',
        'result': None
    }

    conda_res = json.loads(output)

    if 'success' in conda_res and conda_res['success']:
        ret['result'] = True
        if 'actions' in conda_res:
            ret['changes'].update({
                name: {
                    'old': conda_res['actions'].get('UNLINK', []),
                    'new': conda_res['actions'].get('LINK', [])
                }
            })
        elif 'message' in conda_res:
            ret['comment'] = conda_res['message']

        else:
            ret['comment'] = res

    elif 'error' in conda_res:
        ret['comment'] = conda_res['error']
        if conda_res['error_type'] == 'PackageNotInstalled':
            ret['result'] = True

        elif conda_res['error'].startswith('prefix already exists'):
            ret['result'] = True

        else:
            ret['result'] = False

    else:
        ret['comment'] = conda_res

    return ret


def _conda_install(packages, conda_dir, env='', channel='',
                   present=True, user=None):
    if env != '':
        env = '-n %s' % env

    if channel != '':
        channel = '-c %s' % channel

    cmd = 'install'
    if not present:
        cmd = 'uninstall'
    res = (__salt__['cmd.run']
           ('%(bin)s %(cmd)s %(env)s %(chan)s -q --json -y %(packages)s' %
            {'bin': '%s/bin/conda' % conda_dir,
             'packages': packages,
             'env': env,
             'cmd': cmd,
             'chan': channel
             }, runas=user))

    return _conda_return(packages, res)


def _pip_install(packages, conda_dir, env='',
                 present=True, user=None):

    if env != '':
        bin_ = '%s/envs/%s/bin/pip' % (conda_dir, env)
    else:
        bin_ = '%s/bin/pip'

    cmd = 'install'
    yes = ''
    if not present:
        cmd = 'uninstall'
        yes = '-y'

    res = (__salt__['cmd.run']
           ('%(bin)s %(cmd)s %(yes)s %(packages)s' %
            {'bin': bin_,
             'packages': packages,
             'cmd': cmd,
             'yes': yes
             }, runas=user))

    r = res.split('\n')
    c = -1
    while True:
        resp = r[c].strip()
        if not resp.startswith('The directory'):
            break
        c -= 1
    ret = {
        'name': packages,
        'changes': {},
        'comment': '',
        'result': None
    }

    if resp.endswith('not installed'):
        ret['result'] = True
        ret['comment'] = resp

    elif resp.startswith('Successfully installed'):
        ret['result'] = True
        rs = resp[22:].split(' ')
        ret['changes'].update({
            packages: {
                'old': [],
                'new': rs
            }
        })

    elif resp.startswith('Successfully uninstalled'):
        ret['result'] = True
        rs = resp[24:].split(' ')
        ret['changes'].update({
            packages: {
                'old': rs,
                'new': []
            }
        })

    else:
        ret = {
            'name': packages,
            'changes': {},
            'comment': res,
            'result': False
        }

    return ret


def install(name, path, env='', channel='', user=None,
            present=True, use_pip=False):
    if not use_pip:
        ret = _conda_install(name, path, env, channel, present, user)
    else:
        ret = _pip_install(name, path, env, present, user)

    return ret


def create(name, path, packages='python', channel='', user=None, present=True):
    if channel != '':
        channel = '-c %s' % channel

    cmd = 'create'
    if not present:
        cmd = 'env remove'
        channel = ''
        packages = ''

    res = (__salt__['cmd.run']
           ('%(bin)s %(cmd)s %(env)s %(chan)s -q --json -y %(packages)s' %
            {'bin': '%s/bin/conda' % path,
             'packages': packages,
             'env': '-n %s' % name,
             'cmd': cmd,
             'chan': channel
             }, runas=user))

    return _conda_return(name, res)
