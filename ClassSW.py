from ClassConnect import *
from collections import OrderedDict
import re
import pprint


def deco(func):
    def _deco(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception:
            print('Please Check SAN Switch connection...')
    return _deco


class SANSW(object):
    def __init__(self, strIP, intPort, strUserName, strPasswd,
                 lstSWPort, intTimeout=5):
        self._host = strIP
        self._port = intPort
        self._username = strUserName
        self._password = strPasswd
        self._timeout = intTimeout
        self._allSWPort = lstSWPort
        self._strAllPortError = None
        self._dicPartPortError = None
        self._SANSWConnection = None
        self._getporterrshow()
        self._PutErrorToDict()

    def _getporterrshow(self):
        try:
            objConnectToSW = SSHConn(self._host,
                                     self._port,
                                     self._username,
                                     self._password,
                                     self._timeout)
            self._strAllPortError = objConnectToSW.exec_command(
                'porterrshow')
            self._SANSWConnection = objConnectToSW
        except Exception as E:
            print('Connect to SAN Switch {} Failed...'.format(self._host))

    def _PutErrorToDict(self):

        def _portInLine(intSWPort, strLine):
            lstLine = strLine.split()
            if (str(intSWPort) + ':') in lstLine:
                return True
            else:
                return False

        def _getErrorAsList(intPortNum, lstPortErrLines):
            for portErrLine in lstPortErrLines:
                if _portInLine(intPortNum, portErrLine):
                    reDataAndErr = re.compile(
                        r'(.*:)((\s+\S+){2})((\s+\S+){6})((\s+\S+){5})(.*)')
                    resultDataAndErr = reDataAndErr.match(portErrLine)
                    return(resultDataAndErr.group(2).split() +
                           resultDataAndErr.group(6).split())

        def _putToDict():
            dicPort_Error = OrderedDict()
            lstPortErrLines = self._strAllPortError.split('\n')
            for intPortNum in self._allSWPort:
                lstErrInfo = _getErrorAsList(intPortNum, lstPortErrLines)
                dicPort_Error[intPortNum] = lstErrInfo
            self._dicPartPortError = dicPort_Error

        if self._strAllPortError:
            _putToDict()
        else:
            try:
                self._getporterrshow()
                _putToDict()
            except Exception:
                print('Check SAN Switch Connect...')

    @deco
    def get_linkfail_by_port(self, intSWPort):
        if self._dicPartPortError:
            if intSWPort in self._dicPartPortError.keys():
                return self._dicPartPortError[intSWPort][4]
            else:
                return 'Please Correct the Port Number...'
        else:
            print('Please initialization SAN Switch connect first...')
            return None

    @deco
    def get_encout_by_port(self, intSWPort):
        if intSWPort in self._dicPartPortError.keys():
            return self._dicPartPortError[intSWPort][2]
        else:
            print('Please Correct the Port Number...')
            return None

    @deco
    def get_discC3_by_port(self, intSWPort):
        if intSWPort in self._dicPartPortError.keys():
            return self._dicPartPortError[intSWPort][3]
        else:
            print('Please Correct the Port Number...')
            return None

    @deco
    def get_encout_total(self):
        int_encoutTotal = 0
        for i in self._dicPartPortError:
            if 'k' in self._dicPartPortError[i][2]:
                return 'Over Thousand Errors of encout detected...'
            elif 'm' in self._dicPartPortError[i][2]:
                return 'Over Million Errors of encout detected...'
            int_encoutTotal += int(self._dicPartPortError[i][2])
        return int_encoutTotal

    @deco
    def get_discC3_total(self):
        int_encoutTotal = 0
        for i in self._dicPartPortError:
            if 'k' in self._dicPartPortError[i][3]:
                return 'Over Thousand Errors of discC3 detected...'
            elif 'm' in self._dicPartPortError[i][3]:
                return 'Over Million Errors of discC3 detected...'
            int_encoutTotal += int(self._dicPartPortError[i][3])
        return int_encoutTotal

    @deco
    def clear_porterr_All(self):
        if self._SANSWConnection:
            try:
                self._SANSWConnection.exec_command('statsclear')
                return True
            except Exception as E:
                print('Clear Error Count Failed...')
                return False
        else:
            print('Connect to SAN Switch lost...')
            return False

    @deco
    def clear_porterr_by_port(self, intSWPort):
        if self._boolConnectStatus:
            try:
                self._SANSWConnection.exec_command(
                    'portstatsclear {}'.format(str(intSWPort)))
                return True
            except Exception as E:
                print('Clear Error Count Failed...')
                return False
        else:
            print('Connect to SAN Switch lost...')
            return False


if __name__ == '__main__':

    lstPort = [2, 3, 4, 5]
    sw1 = SANSW('172.16.254.75', 22, 'admin', 'password', lstPort)
    # pprint.pprint(sw1._dicPartPortError)
    # print(sw1.get_encout_total())
    # print(sw1.get_discC3_total())
    print(sw1.get_encout_by_port(3))
    # print(sw1.get_encout_by_port(20))
    # print(sw1.get_linkfail_by_port(4))
    # sw1.clear_porterr_by_port(3)
    print(sw1.get_encout_by_port(3))
    sw1._dicPartPortError = None
    print(sw1.get_encout_by_port(3))
    lstSW = ['172.16.254.75', '172.16.254.76']

    lstSWinstance = []
    oddSWObject = OrderedDict()
    for i in lstSW:
        locals()['SW' + str(i)] = SANSW(i, 22, 'admin', 'password', lstPort)
        lstSWinstance.append(locals()['SW' + str(i)])
        # print(str('SW' + str(i)))
        oddSWObject[str('SW' + str(i))] = locals()['SW' +
                                                   str(i)]._dicPartPortError

    pprint.pprint(oddSWObject)

    # print(dir(SANSW))
