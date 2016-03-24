import socket
import fcntl
import sys
import dbus

class Network(object):
    NM_SERVICE = 'org.freedesktop.NetworkManager'
    NM_OPATH   = '/org/freedesktop/NetworkManager'
    NM_DSERVICE = "%s.Devices" % NM_SERVICE

    @staticmethod
    def get_all_devices():
        bus = dbus.SystemBus()

        proxy = bus.get_object(Network.NM_SERVICE, Network.NM_OPATH)
        devs = proxy.getDevices(dbus_interface=Network.NM_SERVICE)

        devices = []
        for dev in devs:
            device = bus.get_object(Network.NM_SERVICE, dev)
            devices.append(device.getProperties(Network.NM_DSERVICE))

        return devices

    @staticmethod
    def get_default_device():
        ds = Network.get_all_devices()
        for d in ds:
            if d[10] != '0.0.0.0':
                return d
        
    #if __name__ == "__main__":
    #    d = getDefaultDevice()
    #    print '%s: %s/%s' % (d[1], d[6], d[7])


    @staticmethod
    def ifconfig(ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            result = fcntl.ioctl(s.fileno(), 0x8915, #SIOCGIFADDR,
                (ifname+'\0'*32)[:32])
        except IOError:
            return None

        return socket.inet_ntoa(result[20:24])
