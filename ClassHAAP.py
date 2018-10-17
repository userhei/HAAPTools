import ClassConnect
import re


def deco_Exception(func):
    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            print('Please Check HAAP connection...')
    return _deco


class HAAP():
    def __init__(self, strIP, intPort, strPasswd, intTimeout=5):
        self._host = strIP
        self._port = intPort
        self._password = strPasswd
        self._timeout = intTimeout
        self._Connection = None
        self._connect()

    def _connect(self):
        try:
            self._Connection = ClassConnect.HAAPConn(self._host,
                                                     self._port,
                                                     self._password)
        except Exception as E:
            print('Connect to HAAP Engine Failed...')

    @deco_Exception
    def get_vpd(self):
        if self._Connection:
            return self._Connection.ExecuteCommand('vpd')
        else:
            self._connect()
            return self._Connection.ExecuteCommand('vpd')

    def get_engine_status(self):
        pass

    def get_uptime(self):
        strVPD_Info = self.get_vpd()
        reUpTime = re.compile(r'uptime')
        strUpTime = reUpTime.match(strVPD_Info)
        def list():
            pass
        def human():
            pass

    def is_master_engine(self):
        pass

    def get_mirror_info(self):
        pass

    def get_mirror_status(self):
        pass

    def backup(self):
        pass

    def execute_multi_command(self):
        pass

    def get_trace(self):
        pass

    def periodic_check(self):
        pass

    def trace_analize(self):
        pass


if __name__ == '__main__':
    aa = HAAP('172.16.254.71', 21, '.com')
    print(aa.get_vpd())
