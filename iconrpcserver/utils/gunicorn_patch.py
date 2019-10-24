
import os
import platform
import tempfile

from gunicorn import util

PLATFORM = platform.system()
IS_CYGWIN = PLATFORM.startswith('CYGWIN')


def __worker_tmp_init__(self, cfg):
    old_umask = os.umask(cfg.umask)
    fdir = cfg.worker_tmp_dir
    if fdir and not os.path.isdir(fdir):
        raise RuntimeError("%s doesn't exist. Can't create workertmp." % fdir)
    fd, name = tempfile.mkstemp(prefix="wgunicorn-", dir=fdir)

    # avoid os.chown when running via snap with strict confinement
    # ref : https://github.com/benoitc/gunicorn/issues/2059
    if cfg.uid != os.geteuid() or cfg.gid != os.getegid():
        # allows the process to write to the file
        util.chown(name, cfg.uid, cfg.gid)
    os.umask(old_umask)

    # unlink the file so we don't leak tempory files
    try:
        if not IS_CYGWIN:
            util.unlink(name)
        self._tmp = os.fdopen(fd, 'w+b', 1)
    except:
        os.close(fd)
        raise

    self.spinner = 0
