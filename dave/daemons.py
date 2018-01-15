from daemon import DaemonContext
from daemon.pidfile import TimeoutPIDLockFile as LockFile
import sys
import os


class Daemon(object):
    """A Daemon class which Daemons can inherit from."""

    stdin = stdout = pidpath = None

    def run(self):
        raise NotImplementedError

    def shutdown(self, pid):
        pass

    def _closectx(self):
        """Shuts down the daemon and closes the DaemonContext."""
        pid = self.ctx.pidfile.read_pid()
        self.shutdown(pid)
        if pid is not None:
            os.kill(pid, 15)  # SIGTERM
        self.ctx.close()

    def run_daemon(self):
        """Starts/stops/restarts the daemon based on argv."""
        if self.pidpath is None:
            print("No valid PID path.")
            return
        self.ctx = DaemonContext(
            stdin=self.stdin,
            stdout=self.stdout,
            pidfile=LockFile(self.pidpath),

        )
        if sys.argv[1] == "start":
            with self.ctx:
                self.run()
        elif sys.argv[1] == "stop":
            self._closectx()
        elif sys.argv[1] == "restart":
            self._closectx()
            with self.ctx:
                self.run()
        else:
            print("Unrecognised argument.")
