#-*- coding:utf-8 -*-

from ftplib import FTP
import paramiko
import telnetlib
import time


class FTPConn(object):
    def __init__(self, strIP, intPort, strUserName, strPasswd):
        self._host = strIP
        self._port = intPort
        self._username = strUserName
        self._password = strPasswd
        self._connect()

    def _connect(self):

        ftp = FTP()
        try:
            ftp.connect(self._host, self._port)
        except TimeoutError as E:
            print('\nFTP Connect to {} Failed'.format(self._host))
        try:
            ftp.login(self._username, self._password)
        except Exception as E:
            print(E)
        return ftp

    def GetFile(self, strRemoteFolder, strLocalFolder, strRemoteFileName,
                strLocalFileName, FTPtype='bin', intBufSize=1024):
        ftp = self._connect()
        # print(ftp.getwelcome())
        ftp.cwd(strRemoteFolder)
        objOpenLocalFile = open(strLocalFolder + '/' + strLocalFileName, "wb")

        if FTPtype == 'bin':
            ftp.retrbinary('RETR {}'.format(strRemoteFileName),
                           objOpenLocalFile.write)
        elif FTPtype == 'asc':
            ftp.retrlines('RETR {}'.format(strRemoteFileName),
                          objOpenLocalFile.write)

        objOpenLocalFile.close()
        ftp.close()

    def PutFile(self, strRemoteFolder, strLocalFolder, strRemoteFileName,
                strLocalFileName, FTPtype='bin', intBufSize=1024):
        ftp = self._connect()
        # print(ftp.getwelcome())
        ftp.cwd(strRemoteFolder)
        objOpenLocalFile = open(strLocalFolder + '/' + strLocalFileName, 'rb')

        if FTPtype == 'bin':
            ftp.storbinary('STOR {}'.format(strRemoteFileName),
                           objOpenLocalFile, intBufSize)
        elif FTPtype == 'asc':
            ftp.storlines('STOR {}'.format(
                strRemoteFileName), objOpenLocalFile)

        ftp.set_debuglevel(0)
        objOpenLocalFile.close()
        ftp.close()


class SSHConn(object):
    def __init__(self, host, port, username, password, timeout):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._username = username
        self._password = password
        self._transport = None
        self._client = None
        self._sftp = None
        self._connect()

    def _connect(self):
        try:
            objSSHClient = paramiko.SSHClient()
            objSSHClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            objSSHClient.connect(self._host, port=self._port,
                                 username=self._username,
                                 password=self._password,
                                 timeout=self._timeout)

            self._transport = objSSHClient

        except Exception as E:
            print('''
    Connect to {} Failed in {} Seconds ...
            '''.format(self._host, self._timeout))

    def download(self, remotepath, localpath):
        if self._sftp is None:
            self._sftp = self._transport.open_sftp()
        self._sftp.get(remotepath, localpath)

    def upload(self, localpath, remotepath):
        if self._sftp is None:
            self._sftp = self._transport.open_sftp()
        self._sftp.put(localpath, remotepath)

    def exec_command(self, command):
        if self._client is None:
            self._client = self._transport
        stdin, stdout, stderr = self._client.exec_command(command)
        data = stdout.read()
        if len(data) > 0:
            # print(data.strip())
            return data
        err = stderr.read()
        if len(err) > 0:
            print(err.strip())
            return err

    def close(self):
        if self._transport:
            self._transport.close()


class HAAPConn(object):
    def __init__(self, strIP, intPort, strPasswd):
        self._host = strIP
        self._port = intPort
        self._password = strPasswd
        self._strLoginPrompt = 'Enter password'
        self._strMainMenuPrompt = 'Coredump Menu'
        self._strCLIPrompt = 'CLI>'
        self._strCLIConflict = 'Another session owns the CLI'
        self._Connection = None
        self._connect()

    def _connect(self):
        try:
            objTelnetConnect = telnetlib.Telnet(self._host, self._port)

            objTelnetConnect.read_until(
                self._strLoginPrompt.encode(encoding="utf-8"), timeout=2)
            objTelnetConnect.write(self._password.encode(encoding="utf-8"))
            objTelnetConnect.write(b'\r')
            objTelnetConnect.read_until(
                self._strMainMenuPrompt.encode(encoding="utf-8"), timeout=2)
            objTelnetConnect.write(b'7')

            strOutPut = objTelnetConnect.read_until(
                self._strCLIPrompt.encode(encoding="utf-8"), timeout=2)
            if int(strOutPut.find(self._strCLIPrompt.encode(
                    encoding="utf-8"))) > 0:
                self._Connection = objTelnetConnect
                time.sleep(0.25)
            elif int(strOutPut.find(self._strCLIConflict.encode(
                    encoding="utf-8"))) > 0:
                objTelnetConnect.write(b'y' + b'\r')
                strOutPut = objTelnetConnect.read_until(
                    self._strCLIPrompt.encode(encoding="utf-8"), timeout=2)
                if int(strOutPut.find(self._strCLIPrompt.encode(
                        encoding="utf-8"))) > 0:
                    self._Connection = objTelnetConnect
                    time.sleep(0.25)
            #                 print('''
            # ------Handle the CLI Succesfully For Engine: {}
            #                     '''.format(self._strIP))

        except Exception as E:
            print("------Goto CLI Failed For Engine: " + self._strIP)

    def ExecuteCommand(self, *lstCommand):
        strCommandResult = ''
        if self._Connection:
            for strCommand in lstCommand:
                self._Connection.write(strCommand.encode(
                    encoding="utf-8") + b'\r')
                strCommandResult += self._Connection.read_until(
                    self._strCLIPrompt.encode(
                        encoding="utf-8"), timeout=5).decode()
            return strCommandResult
        else:
            return None

    def Close(self):
        if self._Connection:
            self._Connection.close()

