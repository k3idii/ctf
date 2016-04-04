import socket
import SocketServer
import struct
import threading  
import time

TGT_IP = '104.236.81.9'
PORT = 1234
OPER = None
VALUE = None
SRV = None

PASS = []

def do_math(i):
  print "  MATH: ",
  if OPER == 'xor':
    return i ^ VALUE
  if OPER == 'mod':
    return i % VALUE
  else:
    print "WTF ?!",

class ThreadedTcpSrv(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
  allow_reuse_address = True

def callback(sock, client_address, server):
  global OPER
  global VALUE
  global PASS
 
  try:
    sock.settimeout(5)
    real_server_addr = sock.getsockopt(socket.SOL_IP, 80, 16)
    srv_port, srv_ip = struct.unpack("!2xH4s8x", real_server_addr)
    srv_ip = socket.inet_ntoa(srv_ip)
    c_ip, c_port = client_address
    # print "[!] New connection from", client_address, " to " , srv_ip, srv_port
    if srv_port == 1110: # incoming operand !
      while True:
        l = sock.recv(999).strip()
        if l is None or l == '':
          break
        if ' ' in l:
          print "Got operator ", l
          OPER, VALUE = l.split(" ")
          VALUE = int(VALUE)
          sock.sendall("test")
    else: # decode port as numeric
      v = do_math(srv_port)
      print " result = " , v
      PASS.append(v) # save result
    #else:
    #  print " !? "  
  except Exception as e:
    print "!! FAIL ", str(e)


def communicate():
  tgt = (TGT_IP, 8111)
  con = socket.create_connection(tgt)
  while True:
    ln = con.recv(1234)
    if ln is None or ln == '':
      print "[!] EOF !"
      break
    print "[>] MASTER SAID: ",`ln`
    if "Code" in ln:
      print "[ !! ] Waiting for code "
      time.sleep(1)
      asc = "".join(map(chr,PASS[:4]))
      nums = "".join(map(str,map(int,PASS[4:])))
      code = asc + nums + "\n"
      print "SEND CODE: [{0}]".format(code)
      con.send(code)
  print " << Connection terminated !"

def start_server():
  global SRV
  print "[+] Will listen on {0}".format(PORT)
  listen_addr = ( '0.0.0.0', PORT )
  SRV = ThreadedTcpSrv( listen_addr, callback)
  SRV.serve_forever()
  print "[-] Server down !"

if __name__ == '__main__':
  print " [!!!] TODO :"
  print "iptables -A PREROUTING -s {0} -p tcp -j REDIRECT --to-ports {1}".format(TGT_IP, PORT)
  print "[+] Starting server ... "
  th = threading.Thread(target=start_server)
  th.start()
  try:
    communicate()
  except KeyboardInterrupt:
    pass
  except:
    pass  
  print "[-] shutdown server ... "
  SRV.shutdown()


