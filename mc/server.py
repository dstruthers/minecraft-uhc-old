import os, subprocess

class MinecraftServer:
    '''Encapsulates a running Minecraft server'''

    def __init__(self, minecraft_dir, minecraft_jar, java_opts = ''):
        self.process = None
        self.minecraft_dir = minecraft_dir
        self.minecraft_jar = minecraft_jar
        self.java_opts = java_opts

    def start(self):
        '''Start the Minecraft server'''
        os.chdir(self.minecraft_dir)
        self.process = subprocess.Popen(['java', '-jar', self.minecraft_jar],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)

    def stop(self):
        '''Stop the Minecraft server'''
        if self.process:
            self.process.stdin.write('/stop\n')
                                        
    def is_running(self):
        '''Returns True if server is running'''
        self.process.poll()
        return self.process.returncode == None

    def returncode(self):
        '''Return code of stopped server, or None if server is still running'''
        self.process.poll()
        return self.process.returncode

    def readline(self):
        '''Read a line of server output'''
        return self.process.stdout.readline()

    def write(self, input):
        """Write to server's stdin"""
        self.process.stdin.write(input)
