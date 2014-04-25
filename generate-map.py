import math, time
from argparse import ArgumentParser
from mc.server import MinecraftServer

def log(msg):
    """Log msg to stdout"""
    now = time.strftime('%H:%M:%S')
    print '[%s] [Terrain Generator] %s' % (now, msg)

def wait_for_startup(server):
    """Wait for a MinecraftServer to finish starting up"""
    while True:
        line = server.readline()
        if line:
            print line,
            if line.find('Done') != -1:
                log('Detected end of server initialization')
                return

argparser = ArgumentParser(description='Pre-generate Minecraft terrain over a \
                                        given area')
argparser.add_argument('--minecraft-dir', dest='minecraft_dir', required=True,
                       help='Directory containing the Minecraft server .jar')
argparser.add_argument('--jar', dest='minecraft_jar', required=True,
                       help='Filename of Minecraft server .jar')
argparser.add_argument('--map-size', dest='map_size', required=True, type=int,
                       help='Desired width/height of terrain to generate')
args = argparser.parse_args()

adjusted_map_size = int(math.ceil(args.map_size / 192.0) * 192)

server = MinecraftServer(args.minecraft_dir, args.minecraft_jar)
spawn_coords_range = range(-(adjusted_map_size / 2) + 96,
                           adjusted_map_size / 2 - 95,
                           192)

log('Will generate %(n)d x %(n)d area around map origin' % \
    {'n': adjusted_map_size})
log('Starting server')
server.start()
wait_for_startup(server)

for x in spawn_coords_range:
    for z in spawn_coords_range:
        log('Changing world spawn point')
        server.write('/setworldspawn %d 60 %d\n' % (x, z))
        # Confirm spawn point was changed before stopping server
        while server.is_running():
            line = server.readline()
            if line:
                print line,
                if line.find('Set the world spawn point') != -1:
                    log('Stopping server')
                    server.stop()
        log('Server terminated with code %d' % server.returncode())

        if x < max(spawn_coords_range) or z < max(spawn_coords_range):
            log('Starting server')
            server.start()
            wait_for_startup(server)

log('Finished generating terrain')
