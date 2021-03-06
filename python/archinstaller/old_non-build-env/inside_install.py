import sys, time, os
from getpass import getpass
from subprocess import PIPE, Popen, STDOUT

if os.geteuid() >  0:
	sys.stdout.write(" ![ERROR] Must be root to run this script\n")
	sys.exit(1)


## =========== Python programatical way of getting Network Interfaces:
# Credit: http://programmaticallyspeaking.com/getting-network-interfaces-in-python.html
# Credit: http://code.google.com/p/pydlnadms/
from socket import AF_INET, AF_INET6, inet_ntop
from ctypes import (
	Structure, Union, POINTER,
	pointer, get_errno, cast,
	c_ushort, c_byte, c_void_p, c_char_p, c_uint, c_int, c_uint16, c_uint32
)
import ctypes.util
import ctypes
 
class struct_sockaddr(Structure):
	_fields_ = [
		('sa_family', c_ushort),
		('sa_data', c_byte * 14),]
 
class struct_sockaddr_in(Structure):
	_fields_ = [
		('sin_family', c_ushort),
		('sin_port', c_uint16),
		('sin_addr', c_byte * 4)]
 
class struct_sockaddr_in6(Structure):
	_fields_ = [
		('sin6_family', c_ushort),
		('sin6_port', c_uint16),
		('sin6_flowinfo', c_uint32),
		('sin6_addr', c_byte * 16),
		('sin6_scope_id', c_uint32)]
 
class union_ifa_ifu(Union):
	_fields_ = [
		('ifu_broadaddr', POINTER(struct_sockaddr)),
		('ifu_dstaddr', POINTER(struct_sockaddr)),]
 
class struct_ifaddrs(Structure):
	pass
struct_ifaddrs._fields_ = [
	('ifa_next', POINTER(struct_ifaddrs)),
	('ifa_name', c_char_p),
	('ifa_flags', c_uint),
	('ifa_addr', POINTER(struct_sockaddr)),
	('ifa_netmask', POINTER(struct_sockaddr)),
	('ifa_ifu', union_ifa_ifu),
	('ifa_data', c_void_p),]
 
libc = ctypes.CDLL(ctypes.util.find_library('c'))
 
def ifap_iter(ifap):
	ifa = ifap.contents
	while True:
		yield ifa
		if not ifa.ifa_next:
			break
		ifa = ifa.ifa_next.contents
 
def getfamaddr(sa):
	family = sa.sa_family
	addr = None
	if family == AF_INET:
		sa = cast(pointer(sa), POINTER(struct_sockaddr_in)).contents
		addr = inet_ntop(family, sa.sin_addr)
	elif family == AF_INET6:
		sa = cast(pointer(sa), POINTER(struct_sockaddr_in6)).contents
		addr = inet_ntop(family, sa.sin6_addr)
	return family, addr
 
class NetworkInterface(object):
	def __init__(self, name):
		self.name = name
		self.index = libc.if_nametoindex(name)
		self.addresses = {}
 
	def __str__(self):
		return "%s [index=%d, IPv4=%s, IPv6=%s]" % (
			self.name, self.index,
			self.addresses.get(AF_INET),
			self.addresses.get(AF_INET6))
 
def get_network_interfaces():
	ifap = POINTER(struct_ifaddrs)()
	result = libc.getifaddrs(pointer(ifap))
	if result != 0:
		raise OSError(get_errno())
	del result
	try:
		retval = {}
		for ifa in ifap_iter(ifap):
			name = ifa.ifa_name
			i = retval.get(name)
			if not i:
				i = retval[name] = NetworkInterface(name)
			family, addr = getfamaddr(ifa.ifa_addr.contents)
			if addr:
				i.addresses[family] = addr
		return retval.values()
	finally:
		libc.freeifaddrs(ifap)

## ===================================================
## ===================================================
class openboxMenu_generator():
	def __init__(self):
		self.text = '<?xml version="1.0" encoding="utf-8"?>\n'
		self.text += '<openbox_menu xmlns="http://openbox.org/3.4/menu">\n'

		self.menu = '<menu id="root-menu" label="Openbox 3">\n'
		self.menu += '<separator label="Applications"/>\n'
		self.items = []
	def add_menu(self, _lbl, _id):
		self.menu += '<menu id="' + _id + '"/>\n'
		self.text += '<menu id="' + _id + '" label="' + _lbl + '">\n'
		self.text += '\n'.join(self.items)
		self.text += '</menu>\n'
		self.items = []

	def add_item(self, _lbl, _exec):
		s = ''
		s += '<item label="' + _lbl + '">\n'
		s += '	<action name="Execute">\n'
		s += '		<execute>' + _exec + '</execute>\n'
		s += '	</action>\n'
		s += '</item>\n'
		self.items.append(s)

	def save(self):
		self.menu += '	<separator label="System"/>\n'
		self.menu += '	<menu id="system-menu"/>\n'
		self.menu += '	<separator/>\n'
		self.menu += '	<item label="Log Out">\n'
		self.menu += '		<action name="Exit">\n'
		self.menu += '			<prompt>yes</prompt>\n'
		self.menu += '		</action>\n'
		self.menu += '	</item>\n'
		self.menu += '	<item label="Shut down">\n'
		self.menu += '		<action name="Execute">\n'
		self.menu += '			<execute>systemctl poweroff -i</execute>\n'
		self.menu += '		</action>\n'
		self.menu += '	</item>\n'
		self.menu += '</menu>\n'

		"""
		self.text = ""<menu id="system-menu" label="System">
						<item label="Openbox Configuration Manager">
							<action name="Execute">
								<command>obconf</command>
								<startupnotify>
									<enabled>yes</enabled>
								</startupnotify>
							</action>
						</item>
						<item label="Openbox Menu Editor">
							<action name="Execute">
								<execute>obmenu</execute>
							</action>
						</item>
						<item label="Openbox Theme Editor">
							<action name="Execute">
								<execute>lxappearance</execute>
							</action>
						</item>
						<separator/>
						<item label="Reconfigure Openbox">
							<action name="Reconfigure"/>
						</item>
					</menu>""
		"""

		self.text += self.menu + '</openbox_menu>'

		return self.text

def output(what, flush=True):
	sys.stdout.write(what)
	if flush:
		sys.stdout.flush()

class output_line():
	def __init__(self, starter=''):
		self.len = 0
		self.line = starter
		if self.line != '':
			output(self.line)

	def add(self, what, flush=True):
		self.line += what
		output(what, flush)

	def beginning(self, what, linebreak=True, flush=True):
		output('\b' * len(self.line), False)
		self.line = what + self.line
		if linebreak:
			self.line += '\n'
		output(self.line)

	def replace(self, what, num=1):
		output('\b' * num, False)
		self.line = self.line[:0-num] + what
		output(what)

class run():
	def __init__(self, cmd):
		self.cmd = cmd
		self.stdout = None
		self.stdin = None
		self.x = None
		self.run()

	def run(self):
		self.x = Popen(self.cmd, shell=True, stdout=PIPE, stderr=STDOUT, stdin=PIPE)
		self.stdout, self.stdin = self.x.stdout, self.x.stdin

	def wait(self, text):
		i = 0
		self.output = output_line(text)
		graphics = ['/', '-', '\\', '|']
		while self.x.poll() == None:
			self.output.replace(graphics[i%len(graphics)-1])
			i += 1
			time.sleep(0.2)

		self.output.replace(' ')
		if self.poll() in (0, '0'):
			self.output.beginning(' [OK] ')
			self.close()
			return True
		else:
			self.output.beginning(' ![Error] ')
			output_line('\t' + str([self.cmd]))
			output_line('\t' + self.stdout.read())
			self.close()
			return False

	def write(self, what, enter=True):
		if enter:
			if len(what) <= 0 or not what[-1] == '\n':
				what += '\n'
		self.stdin.write(what)

	def poll(self):
		return self.x.poll()

	def getline(self):
		while True:
			try:
				line = self.stdout.readline()
			except:
				break
			if len(line) <= 0: break
			yield line

	def getlines(self):
		return self.stdout.readlines()

	def close(self):
		self.stdout.close()
		self.stdin.close()

def passwd(USR, PWD):
	passwd = run('echo -e "' + PWD + '\\\\n' + PWD + '" | passwd ' + USR)
	passwd.wait( ' Setting ' + USR + '\'s password |')
	return True

def checkInternet():
	x = output_line('Checking for a internet connection ')
	internet = run('ping -c 2 www.google.com')
	for line in internet.getline():
		x.add('.')
		if '0% packet loss' in line and not '100% packet loss' in line:
			internet.close()
			x.beginning(' [OK] ')
			del x
			return True
	try:
		internet.close()
	except:
		pass
	x.beginning(' ![ERROR] ')
	del x
	return False

def listHDDs():
	## TODO: Show the device name
	hdds = []
	for root, folders, files in os.walk('/sys/block'):
		for drive in folders:
			if drive[:4] == 'loop': continue
			with open(os.path.abspath(root + '/' + drive + '/removable')) as fh:
				if int(fh.readline().strip()) == 0:
					hdds.append(drive)
	return hdds

def listPartitions(drive):
	parts = []
	for root, folders, files in os.walk(os.path.abspath('/sys/block/' + drive + '/')):
		for partition in folders:
			if not drive in partition: continue
			parts.append(partition[len(drive):])
	return parts

def get_graphiccard_driver():
	x = run('lspci | grep VGA')
	raw = x.getline()
	x.close()
	raw = str(raw)

	if 'intel' in raw.lower():
		return 'Intel', 'xf86-video-intel libva-intel-driver'
	elif 'nvidia' in raw.lower():
		return 'nVidia', select(['nvidia', 'nvidia-304xx'], 'nVidia driver (304 is for GeForce 6/7)')
	elif 'ati' in raw.lower() or 'amd' in raw.lower():
		## Prior steps:
		# https://wiki.archlinux.org/index.php/AMD_Catalyst#Installation
		return 'ATi', 'catalyst catalyst-utils'
	else:
		return 'Generic', 'xf86-video-vesa'
	return None, None

def select(List, text=''):
	index = {}
	output(' | Select one of the following' + text + ':\n', False)
	for i in range(0, len(List)):
		output('   ' + str(i) + ': ' + str(List[i]) + '\n', False)
	try:
		sys.stdin.flush()
		sys.stdout.flush()
	except:
		pass
	output(' | Choice: ')
	choice = sys.stdin.readline().replace('\r', '').replace('\n', '')
	if len(choice) <= 0:
		choice = 0
	return List[int(choice)]

def install(package_list, text='Installing packages'):
	x = run('echo | pacman --noconfirm -S ' + ' '.join(package_list))
	x.wait(' ' + text + ' |')

graphics, graphicdriver = get_graphiccard_driver()

output(' |\n')
output(' | Welcome root to your new environment, let me prepare it for you!\n |\n')
output(' |--- Assuming:\n', False)
output(' | Graphics: ' + graphics)
output(' | Bootload: MBR for bootloader\n', False)
output(' | Language: ENG (US) base-language\n', False)
output(' | Keyboard: SWE layout\n',False)
output(' | Timezone: Europe/Stockholm\n')

X = select([None, 'OpenBox', 'KDE', 'Gnome'], ' Graphical environments')
WEBBROWSER = select([None, 'Chromium', 'FireFox'], ' Browser of poison')
MEDIAPLAYER = select([None, 'VLC', 'DragonPlayer'])
ROOT_PWD = getpass(' [<<] Enter "ROOT" password: ')

output(' [<<] Enter a bad-ass hostname for your machine: ')
with open('/etc/hostname', 'wb') as fh:
	fh.write(sys.stdin.readline())

USER = raw_input(' [<<] Enter a desired username: ')
while USER == 'root':
	USER = raw_input(' [<<] Enter a desired username (Not root): ')

if len(USER) <= 0:
	print ' | Defaulting to "root" user"'
	USER = 'root'
	## Try to default to root,
	## Some things should not be run as root, but they "can".
	## For instance, X will run (shaky) under root while audio won't
	## So we can try to install X but we'll skip Audio features.
else:
	PASS = getpass(' [<<] Enter a password for "' + USER + '": ')

	x = run('useradd -m -g users -s /bin/bash ' + USER)
	x.wait(' Generating new user "' + USER + '" |')
	passwd(USER, PASS)

info = output_line(' | Entering fully automated install in 3')
time.sleep(1)
info.replace('2')
time.sleep(1)
info.replace('1')
time.sleep(1)
info.replace(' ')
info.beginning(' [OK] ')

X_MAP = {'OpenBox' : ['pacman --noconfirm -S openbox',
					'mkdir -p /home/' + USER + '/.config/openbox',
					'cp /etc/xdg/openbox/{rc.xml,menu.xml,autostart,environment} /home/' + USER + '/.config/openbox',
					'echo "exec openbox-session" >> /home/' + USER + '/.xinitrc',
					'echo "[[ -z \$DISPLAY && \$XDG_VTNR -eq 1 ]] && exec startx" >> /home/' + USER + '/.bash_profile']}

lang = output_line(' | Writing language configuration')
with open('/etc/locale.gen', 'wb') as fh:
	fh.write('en_US.UTF-8 UTF-8\n')
with open('/etc/locale.conf', 'wb') as fh:
	fh.write('LANG=en_US.UTF-8\n')
with open('/etc/vconsole.conf', 'wb') as fh:
	fh.write('KEYMAP=sv-latin1\n')
	fh.write('FONT=lat1-12\n')
lang.beginning(' [OK] ')

x = run('locale-gen')
x.wait(' Generating language files |')

run('ln -s /usr/share/zoneinfo/Europe/Stockholm /etc/localtime').close()
clock = run('hwclock --systohc --utc')
clock.wait(' Setting system clock to UTC (Installing Windows later might get time issues) |')


#output(' | == Don\'t forget to run: "systemctl start dhcpcd" after reboot!\n')
for ni in get_network_interfaces():
	dhcp = run('systemctl enable dhcpcd@' + ni.name + '.service')
	dhcp.wait(' Enabling DHCP on interface ' + ni.name + ' |')

install(['iw','wpa_supplicant'], 'Installing Wireless tools')
install(['alsa-plugins',], 'Installing Audio tools')
install(['pyglet',], 'Installing a Python graphical library for the "first-time-login"')
install(['sudo',], 'Installing sudo and adding "' + USER + '" to sudo access list')
with open('/etc/sudoers', 'ab') as fh:
	fh.write('\n' + USER + '   ALL=(ALL) ALL\n')

install(['grub-bios',], 'Installing GRUB binaries')

grub = run('grub-install --recheck /dev/' + sys.argv[1][:-1])
grub.wait(' Installing GRUB to MBR |')
run('cp /usr/share/locale/en\@quot/LC_MESSAGES/grub.mo /boot/grub/locale/en.mo').close()

grubcfg = run('grub-mkconfig -o /boot/grub/grub.cfg')
grubcfg.wait(' Generating GRUB configuration |')


if X:
	install([graphicdriver,], 'Installing "' + graphics + '" graphical drivers')
	install('xorg-server xorg-xinit xorg-apps'.split(' '), 'Preparing graphical environment')

	counter = 1
	tot_steps = len(X_MAP[X])
	for step in X_MAP[X]:
		x = run(step)
		x.wait(' Installing ' + X + ' step ' + str(counter) + '(' + str(tot_steps) + ') |')
		counter += 1

	if X == 'OpenBox':
		gen = openboxMenu_generator()
		gen.add_item('AlsaMixer', 'xterm alsamixer')
		if MEDIAPLAYER:
			gen.add_item(MEDIAPLAYER, MEDIAPLAYER.lower())
		gen.add_item('Thunar', 'thunar')
		gen.add_menu('Accessories', 'apps-accessories-menu')

		gen.add_menu('Games', 'apps-games-menu')

		gen.add_item('Nano', 'xterm -e nano -w -S')
		gen.add_menu('Editors', 'apps-editors-menu')

		gen.add_item('Xterm', 'xterm')
		gen.add_menu('Terminals', 'apps-term-menu')

		if WEBBROWSER:
			gen.add_item(WEBBROWSER, WEBBROWSER.lower())
		gen.add_menu('Internet', 'apps-net-menu')

		with open('/home/' + USER + '/.config/openbox/menu.xml', 'wb') as fh:
			fh.write(gen.save())

if WEBBROWSER:
	install([WEBBROWSER.lower(),], 'Installing ' + WEBBROWSER)

if MEDIAPLAYER:
	media_map = {'DragonPlayer' : 'kdemultimedia-dragonplayer', 'VLC' : 'vlc'}
	install([media_map[MEDIAPLAYER],], 'Installing ' + MEDIAPLAYER)


prepping_first_launch = output_line('Prepping first launch ')

if not os.path.exists('/etc/systemd/system/getty@tty1.service.d'):
	os.makedirs('/etc/systemd/system/getty@tty1.service.d')
with open('/etc/systemd/system/getty@tty1.service.d/autologin.conf', 'wb') as fh:
	fh.write('[Service]\n')
	fh.write('ExecStart=\n')
	fh.write('ExecStart=-/usr/bin/agetty --autologin ' + USER + ' --noclear %I 38400 linux\n')
	fh.write('Type=simple\n')
with open('/home/' + USER + '/.config/openbox/autostart', 'ab') as fh:
	fh.write('python2 ~/first_boot.py &\n')

prepping_first_launch.beginning(' [OK] ')


passwd('root', ROOT_PWD)
print ' | Done, inside installer handing off'
