import os
import sys

import optparse
import commands

import argparse

import getpass

from telnetlib import Telnet
import paramiko

progName = "lunadm"
version = "0.1"
copyright = "(C) NetApp Inc"
terminal_license = "This program is licensed under the terms of the GNU GPLv2 (or at your option) any later version"

class Log:
    
    '''A OOP implementation for logging.
    warnings is to tackle the warning option
    verbose is to tackle the verbose option
    color is if you want to colorize your output
    
    You should pass these options, taking it from optparse/getopt,
    during instantiation'''
    
    ''' WConio can provide simple coloring mechanism for Microsoft Windows console
    Color Codes:
    Black = 0
    Green = 2
    Red = 4
    White = 15
    Light Red = 12
    Light Cyan = 11
    
    #FIXME: The Windows Command Interpreter does support colors natively. I think that support has been since Win2k.
    
    That's all for Windows Command Interpreter.
    
    
    As for ANSI Compliant Terminals (which most Linux/Unix Terminals are.).....
    I think the ANSI Color Codes would be good enough for my requirements to print colored text on an ANSI compliant terminal.

    The ANSI Terminal Specification gives programs the ability to change the text color or background color.
    An ansi code begins with the ESC character [^ (ascii 27) followed by a number (or 2 or more separated by a semicolon) and a letter.
    
    In the case of colour codes, the trailing letter is "m"...
    
    So as an example, we have ESC[31m ... this will change the foreground colour to red.
    
    The codes are as follows:
    
    For Foreground Colors
    1m - Hicolour (bold) mode
    4m - Underline (doesn't seem to work)
    5m - BLINK!!
    8m - Hidden (same colour as bg)
    30m - Black
    31m - Red
    32m - Green
    33m - Yellow
    34m - Blue
    35m - Magenta
    36m - Cyan
    37m - White
    
    For Background Colors
    
    40m - Change Background to Black
    41m - Red
    42m - Green
    43m - Yellow
    44m - Blue
    45m - Magenta
    46m - Cyan
    47m - White
    
    7m - Change to Black text on a White bg
    0m - Turn off all attributes.
    
    Now for example, say I wanted blinking, yellow text on a magenta background... I'd type ESC[45;33;5m 
    '''
    
    def __init__(self, verbose, lock = None):
            
        self.VERBOSE = bool(verbose)
        
        self.color_syntax = '\033[1;'
        
        if lock is None or lock != 1:
            self.DispLock = False
            self.lock = False
        else:
            self.DispLock = threading.Lock()
            self.lock = True
            
        if os.name == 'posix':
            self.platform = 'posix'
            self.color = {'Red': '31m', 'Black': '30m',
                         'Green': '32m', 'Yellow': '33m',
                         'Blue': '34m', 'Magneta': '35m',
                         'Cyan': '36m', 'White': '37m',
                         'Bold_Text': '1m', 'Underline': '4m',
                         'Blink': '5m', 'SwitchOffAttributes': '0m'}
           
        elif os.name in ['nt', 'dos']:
            self.platform = None
            
            if WindowColor is True:
                self.platform = 'microsoft'
                
                self.color = {'Red': 4, 'Black': 0,
                          'Green': 2, 'White': 15,
                          'Cyan': 11, 'SwitchOffAttributes': 15}
        else:
            self.platform = None
            self.color = None
 
    def set_color(self, color):
        '''Check the platform and set the color'''
        
        if self.platform == 'posix':
            sys.stdout.write(self.color_syntax + self.color[color])
            sys.stderr.write(self.color_syntax + self.color[color])
        elif self.platform == 'microsoft':
            WConio.textcolor(self.color[color])
            
    def msg(self, msg):
        '''Print general messages. If locking is available use them.'''
        
        if self.lock:
            self.DispLock.acquire(True)
          
        self.set_color('White')
        sys.stdout.write(msg)
        sys.stdout.flush()
        self.set_color('SwitchOffAttributes')
        
        if self.lock:
            self.DispLock.release()
        
    def err(self, msg):
        '''Print messages with an error. If locking is available use them.'''
        
        if self.lock:
            self.DispLock.acquire(True)
            
        self.set_color('Red')
        sys.stderr.write("ERROR: " + str(msg) )
        sys.stderr.flush()
        self.set_color('SwitchOffAttributes')
        
        if self.lock:
            self.DispLock.release()
        
    def success(self, msg):
        '''Print messages with a success. If locking is available use them.'''
        
        if self.lock:
            self.DispLock.acquire(True)
            
        self.set_color('Green')
        sys.stdout.write(str(msg) )
        sys.stdout.flush()
        self.set_color('SwitchOffAttributes')
        
        if self.lock:
            self.DispLock.release()
    
    # For the rest, we need to check the options also

    def verbose(self, msg):
        '''Print verbose messages. If locking is available use them.'''
        
        if self.lock:
            self.DispLock.acquire(True)
            
        if self.VERBOSE is True:
            
            self.set_color('Cyan')
            sys.stdout.write("VERBOSE: " + str(msg) )
            sys.stdout.flush()
            self.set_color('SwitchOffAttributes')
        
        if self.lock:
            self.DispLock.release()
    
    def calcSize(self, size):
       ''' Takes number of kB and returns a string
       of proper size. Like if > 1024, return a megabyte '''
       if size > 1024:
            size = size // 1024
            if size > 1024:
                size = size // 1024
                return ("%d gB" % (size) )
            return ("%d mB" % (size) )
       return ("%d kB" % (size) )
      
      
class connectTargetSSH:
        
        def __init__(self, target, credentials, keys):
                self.__user = None
                
                if target.find('@') >= 0:
                        self.__user, self.__targetName = target.split('@')
                elif target is not None:
                        self.__targetName = target
                else:
                        self.__targetName = raw_input("Hostname: ")
                        
                if len(self.__targetName) == 0:
                        log.err("Hostname required\n")
                        sys.exit(1)
                self.__targetPort = 22
                if self.__targetName.find(":") >= 0:
                        self.__targetName, self.__targetPort = self.__targetName.split(":")
                        self.__targetPort = int(self.__targetPort)
                #self.__targetName = target
                self.__keys = keys
                self.__targetCred = credentials
                
                if self.__user is None:
                        default_username = getpass.getuser()
                        username = raw_input("Username [%s]: " % default_username)
                        if len(username) == 0:
                                self.__user = default_username
                        else:
                                self.__user = username
                self.__password = getpass.getpass("Password for %s@%s: " % (self.__user, self.__targetName))
                
                self.hostkeytype = None
                self.hostkey = None
                
                try:
                        self.host_keys = paramiko.util.load_host_keys(os.path.expanduser("~/.ssh/known_hosts") )
                except IOError:
                        try:
                                #For windows, ssh folder is ssh without the dot
                                self.host_keys = paramiko.util.load_host_keys(os.path.expanduser("~/ssh/known_hosts") )
                        except IOError:
                                log.err("Unable to open host keys file")
                                self.host_keys = {}
                
                if self.host_keys.has_key(self.__targetName):
                        self.hostkeytype = self.host_keys[self.__targetName].keys()[0]
                        self.hostkey = self.host_keys[self.__targetName][self.hostkeytype]
                        log.verbose("Using host key of type %s" % (self.hostkeytype) )
                        
                # For SSHClient class, we just need the client instance here
                self.__conn = paramiko.SSHClient()
                try:
                        self.__hostKeyFile = os.path.expanduser("~/.ssh/known_hosts")
                except IOError:
                        try:
                                self.__hostKeyFile = os.path.expanduser("~/ssh/known_hosts")
                        except IOError:
                                log.err("Unable to open host keys file")
                                
        def connectSSH(self, username=None):
                
                #try:
                        # For Transport class
                        #self.conn = paramiko.Transport( (self.__targetName, self.__targetPort) )
                        #self.conn.connect(username=self.__user, password=self.__targetCred, hostkey=self.hostkey)
                        
                        # For SSHClient class
                        x = self.__conn.get_host_keys()
                        if x  == {}:
                                self.__conn.load_host_keys(self.__hostKeyFile)
                        #self.__conn.connect(self.__targetName, self.__targetPort, self.__user, self.__password, self.hostkey, None, None, True, True)
                        self.__conn.connect(self.__targetName, self.__targetPort, self.__user, self.__password)
                        
                        
                        
                        
		#except paramiko.SSHException:
                        # Hmmm!!! Are thee SSH keys loaded
                #        log.err("cannot determine server authenticity\n")
                #        sys.exit(1)
        
        def execCmdSSH(self, command):
                #if self.connected:
                stdin, stdout, stderr = self.__conn.exec_command(command)
                #log.msg(stdout.read() )
                #return True
                return (stdin, stdout, stderr)
        
        def closeConnSSH(self):
		if self.__conn:
			try:
				self.__conn.close()
			except SSHException:
                                # Hmmm!!! Are thee SSH keys loaded
                                log.err("cannot determine server authenticity\n")
                                sys.exit(1)
                        except:
				#TODO: Handle the exception
				return False
			return True
                
class connectTargetTelnet:
	
	def __init__(self, target, credentials=None, execCmd=None):
		self.__targetName = target
		self.__targetCredentials = credentials #INFO: Should be a list
		self.__execCmd = execCmd
		self.conn = None
		
	def connectTelnet(self):
		try:
			self.conn = Telnet(self.__targetName)
		except:
			#TODO: Handle exceptions here.
			self.conn = False
			
		if not self.conn:
			if self.__targetCredentials:
				try:
					self.conn.read_until("login: ")
					self.conn.write(self.__targetCredentials['user'] + "\n")
					self.conn.read_until("Password: ")
					self.conn.write(self.__targetCredentials['password'] + "\n")
				except:
					#TODO: Handle the exception
					return False
			return False
		
	def execCmdTelnet(self):
		if self.conn:
			try:
				self.conn.write(self.__execCmd + '\n')
				self.conn.write("exit\n")
			except:
				#TODO: Handle the exception
				return False
			return self.conn.read_all()
		else:
			return False
		
	def closeConnTelnet(self):
		if self.conn:
			try:
				self.conn.close()
			except:
				#TODO: Handle the exception
				return False
			return True


class connectTarget(connectTargetTelnet, connectTargetSSH):
    ''' This class connects to the target '''
    
    def __init__(self, target, connectionType, credentials=None, execCmd=None):
        self.__targetName = target
        self.__targetCredentials = credentials
        self.__execCmd = execCmd
        self.__connectionType = connectionType
        self.__connectionTypes = ['TELNET', 'RSH', 'ZAPI', 'HTTP', 'SSH']
        
        if self.__connectionType in self.__connectionTypes:
        	if self.__connectionType is 'TELNET':
        		connectTargetTelnet.__init__(self, self.__targetName, self.__targetCredentials, self.__execCmd)
        	elif self.__connectionType is 'RSH':
        		#TODO
        		pass
        	elif self.__connectionType is 'ZAPI':
        		#TODO
        		pass
        	elif self.__connectionType is 'HTTP':
        		#TODO
        		pass
                elif self.__connectionType is 'SSH':
                        connectTargetSSH.__init__(self, self.__targetName, self.__targetCredentials, self.__execCmd)
        	else:
        		#Do Nothing
        		pass
        
    def connect(self):
        ''' Connect to the target '''
        if self.__connectionType is 'TELNET':
        	return self.connectTelnet()
        elif self.__connectionType is 'SSH':
                return self.connectSSH()
        else:
                return False
        	
    def execCmd(self, command):
    	''' Execute a command on the target '''
    	if self.__connectionType is 'TELNET':
    		return self.execCmdTelnet()
        elif self.__connectionType is 'SSH':
                return self.execCmdSSH(command)
    	else:
                return False
    
    def closeConn(self):
    	''' Close the connection '''
    	if self.__connectionType is 'TELNET':
    		return self.closeConnTelnet()
        elif self.__connectionType is 'SSH':
                return self.closeConnSSH()
        else:
                return False

        
        
def main():
        # INFO: One way to handle global options in argparse so that they are available to 
        # subparsers also
        
        # Global options
        global_options = argparse.ArgumentParser(add_help=False)
        
        global_options.add_argument("--verbose", dest="verbose", help="Enable verbose messages", action="store_true" )
        
	global_options.add_argument("-t", "--target", dest="target", help="Target Name/IP",
                      action="store", type=str, metavar="Target Name/Address")
        
	global_options.add_argument("-c", "--command", dest="command",
                      help="Execute command on the target", action="store", metavar="Target Command")
        
        parser = argparse.ArgumentParser( prog=progName + " - " + version,
                                          description="LUN Administration Utility",
                                          epilog=copyright + " - " + terminal_license, parents=[global_options])
        parser.add_argument("-v", "--version", action='version', version=version)
        
        subparsers = parser.add_subparsers()
        
        parser_add = subparsers.add_parser('add', parents=[global_options])
        parser_add.add_argument('add',
                          help="Add LUNs on the Storage Controller and the Initiator host",
                          action="store", type=str, nargs='*', metavar="LUN_N")
        parser_add.add_argument("--type", dest="lun_type", help="Type of LUN to add", action="store",
                                type=str, metavar="LUN Type")
        parser_add.add_argument("--size", dest="lun_size", help="Size of LUN", action="store",
                                type=str, metavar="LUN Size")
        parser_add.add_argument("--igroup", dest="add_igroup", help="igroup to associate with", action="store",
                                type=str, metavar="igroup")
        
        parser_del = subparsers.add_parser('del', parents=[global_options])
        parser_del.add_argument('del',
                          help="Delete LUNs from the Storage Controller and the Initiator host",
                          action="store", type=str, nargs='*', metavar="LUN_N")
        
        parser_show = subparsers.add_parser('show', parents=[global_options])
        parser_show.add_argument('show',
                          help="Show LUNs mapped on the running host",
                          action="store_true")
        parser_show.add_argument("--type", dest="lun_type", help="Type of LUN to show",
                                 action="store", type=str)
        parser_show.add_argument("--igroups", dest="igroup_show", help="Show igroup information",
                                 action="store", type=str)
        parser_show.add_argument("--mapped", dest="mapped_lun", help="Display mapped LUN",
                                 action="store_false")
        parser_show.add_argument("--offline", dest="offline_lun", help="Display offline LUN",
                                 action="store_false")
        parser_show.add_argument("--online", dest="online_lun", help="Display online LUN",
                                 action="store_false")
        parser_show.add_argument("--unmapped", dest="unmapped_lun", help="Display unmapped LUN",
                                 action="store_false")
        parser_show.add_argument("--staging", dest="staging_lun", help="Display staging LUN",
                                 action="store_false")
        
	
        parser_space_reclaim = subparsers.add_parser('space-reclaim', parents=[global_options])
        parser_space_reclaim.add_argument('space-reclaim',
                          help="Reclaim/Free unutilized space on a Thin Provisioned LUN",
                          action="store", type=str, nargs='*', metavar="LUN_N")
        
        
        args = parser.parse_args()
	#(options, args) = parser.parse_args()
	
	try:
		
		# Initialize the logger
                global log
		log = Log(verbose=args.verbose, lock=None)
                target = args.target
                if args.show:
                        lun_type = args.lun_type
                
                        if lun_type is None:
                                lun_type = "all"
                        cmd = "show " + lun_type
		
		if target:
			
			log.verbose("Target is: %s\n" % (target) )
			log.verbose("Command is: %s\n" % (cmd) )
			
			#connection = connectTarget(options.target, 'TELNET', None,  "lun show " + options.lun_show)
			connection = connectTarget(target, 'SSH', None,  "lun " + cmd)
			#print connection.connectNtapTargetRSH()
			connection.connect()
			#connection.execCmd()
			#if not connection.execCmd("lun " + cmd):
                        #        print "Failed"
			#log.verbose("Closing connection: %s\n" % (connection.closeConn() ) )
                        
                        (stdin, stdout, stderr) = connection.execCmd("lun " + cmd)
                        #print stdout.read()
                        for eachline in stdout.readlines():
				try:
                                	eachline.lstrip(eachline.whitespace())
				except:
					pass
                                print eachline
			#print connection.connectNtapTargetTelnet()
	except KeyboardInterrupt:
		sys.stderr.write("Exiting on user request.\n")
			
