import ClassConnect


class HAAP():
    def __init__(self, strIP, intPort, strPasswd, intTimeout=5):
        self._host = strIP
        self._port = intPort
        self._password = strPasswd
        self._timeout = intTimeout
        self._strAllPortError = None
        self._connection = None
        self._connect()
        self._PutErrorToDict()

    def _connect(self):
        try:
            self._connection = ClassConnect.TelnetConn(self._host,
                                                       self._port,
                                                       self._password)
        except Exception as E:
            print('Connect to HAAP Engine Failed...')

    def get_vpd(self):
        if self._connection:
            try:
                return self._connection.ExecuteCommand('vpd')
            except Exception as E:
                print('Execute Failed...')
        else:
            print('Connecttion lost for Engine {}...'.format(self._host))


    # def backup(self, strLocalFolder):

    #     pass

    #     ftp.get(cm.cfg, strLocalFolder + 'cm.cfg')

    def gettrace():
        pass
