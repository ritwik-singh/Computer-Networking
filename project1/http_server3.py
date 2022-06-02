import sys
import os
import datetime
import socket
import json



class SERVER:
    
    def __init__(self):
    
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ''
        self.message = None
        self.http_method = None
        self.address = None
        self.http_version = None
        self.html_body = None
        
        
        
    def connection(self, port):
        
        self.message = {}
        self.s.bind((self.host,port))
        self.s.listen()
        
        while True:
            
            conn, addr = self.s.accept()
            data = conn.recv(4096)
            
            if not data:
                break
            self.extract_message(data)
            print(data)
           
            if self.message["http-method"] == "GET":
                
                if '?' not in self.message["address"] or '=' not in self.message["address"]:
                 
                    if(self.message["address"][:8] == "/product"):
                        return_response =  ('HTTP/1.1' + " " + '400' + " " +  "Bad Request") + \
                        ('\r\nHost: ' +  "") + \
                        ('\r\nLocation: ' + "") + \
                        ('\r\nContent-Type: ' + 'application/json') + \
                        ('\r\nContent-Length: ' + str(len(('you should provide a parameter').encode('ASCII')))) + \
                        ('\r\nDate: ') + \
                        ('\r\n\r\n' + 'you should provide a parameter')
                   
                        conn.sendall(str(return_response).encode('ASCII'))
                        conn.close()
                    else:
                    
                        return_response =  ('HTTP/1.1' + " " + '404' + " " +  "Not Found") + \
                        ('\r\nHost: ' +  "") + \
                        ('\r\nLocation: ' + "") + \
                        ('\r\nContent-Type: ' + 'application/json') + \
                        ('\r\nContent-Length: ' + str(len(('you should provide a operation').encode('ASCII')))) + \
                        ('\r\nDate: ') + \
                        ('\r\n\r\n' + 'you should provide a operation')
                   
                        conn.sendall(str(return_response).encode('ASCII'))
                        conn.close()
                    
                else:
                    
                    split_msg = self.message["address"].split('?')
                    operation = split_msg[0][1:]
                    
                    if(operation != 'product'):
                        return_response =  ('HTTP/1.1' + " " + '404' + " " +  "Not Found") + \
                        ('\r\nHost: ' +  "") + \
                        ('\r\nLocation: ' "") + \
                        ('\r\nContent-Type: ' + 'application/json') + \
                        ('\r\nContent-Length: ' + str(len(('Only product is supported').encode('ASCII')))) + \
                        ('\r\nDate: '+ "") + \
                        ('\r\n\r\n' + 'Only product is supported')
                   
                        conn.sendall(str(return_response).encode('ASCII'))
                        conn.close()
                        
                    parameter = split_msg[1]
                   
                    
                    if not parameter:
                        
                        return_response =  ('HTTP/1.1' + " " + '400' + " " +  "Bad Request") + \
                        ('\r\nHost: ' +  "") + \
                        ('\r\nLocation: ' + "") + \
                        ('\r\nContent-Type: ' + "") + \
                        ('\r\nContent-Length: ' + "") + \
                        ('\r\nDate: ') + \
                        ('\r\n\r\n' + "")
                   
                        conn.sendall(str(return_response).encode('ASCII'))
                        conn.close()
                        
                    else:
                        
                        arguments = parameter.split('&')
                        res = 1.0
                        num = []
                        not_number = False
                        for args in arguments:
                            if '=' in args:
                                if len(args.split('=')[1]):
                                    number = args.split('=')[1]
                                    try:
                                        if(number == 'inf'):
                                            num.append(float('inf'))
                                        elif(number == '-inf'):
                                            num.append(float('-inf'))
                                        else:
                                            num.append(float(number))
                                    except:
                                        not_number = True
                                        break
                                else:
                                    not_number = True
                        if not_number:
                        
                            return_response =  ('HTTP/1.1' + " " + '400' + " " +  "Bad Request") + \
                            ('\r\nHost: ' +  "") + \
                            ('\r\nLocation: ' + "") + \
                            ('\r\nContent-Type: ' + 'application/json') + \
                            ('\r\nContent-Length: ' + str(len(("Arguments should be numeric").encode('ASCII')))) + \
                            ('\r\nDate: ') + \
                            ('\r\n\r\n' + "Arguments should be numeric")
                            conn.sendall(str(return_response).encode('ASCII'))
                            conn.close()
                        else:
                            
                            for i in num:
                                res *= i
                            if(res == float('inf')):
                                result = "inf"
                            elif(res == float('-inf')):
                                result = "-inf"
                            
                            response = json.dumps({"operation": operation, "operands": num, "result": res},indent=4)
                            if(operation == 'product' ):
                            
                                return_response =  ('HTTP/1.1' + " " + '200' + " " +  "OK") + \
                                ('\r\nHost: ' +  "") + \
                                ('\r\nLocation: ' "") + \
                                ('\r\nContent-Type: ' + 'application/json') + \
                                ('\r\nContent-Length: ' + str(len(response.encode('utf-8')))) + \
                                ('\r\nDate: ' + "") + \
                                ('\r\n\r\n' + response)
                   
                                conn.sendall(str(return_response).encode('ASCII'))
                                conn.close()
                                    
                
                
                
    def extract_message(self,message):
    
        decoded_Response = message.decode("ASCII",errors="ignore")
        lines = decoded_Response.split('\r\n')
        status_response = lines[0]
        status_parts = status_response.split(" ")
        self.message["http-method"] = status_parts[0]
        self.message["address"] = status_parts[1]
        self.message["http_version"] = status_parts[2]
        for line in lines:
            values = line.split(' ')
            if(len(values)>= 2):
                header_tag = values[0][:-1]
                if(header_tag == "Content-Type"):
                    header_value = ' '.join(values[1:])
                    tmp = header_value.split(';')[0].strip()
                    if tmp == 'text/html':
                        self.message["content_type"] = 'text/html'
                    elif tmp == 'application/json':
                        self.message["content_type"] = 'application/json'
                    else:
                        self.message["content_type"] = 'unknown'
                elif(header_tag == "Location"):
                    self.message['location'] = ' '.join(values[1:])
                elif(header_tag == "Host"):
                    self.message['host'] = ' '.join(values[1:])
                elif(header_tag == "Content-Length"):
                    self.message['content_length'] = int(' '.join(values[1:]))
                    
        self.html_body = message.decode().split('\r\n\r\n', 1)[1]
        
        
        
    
   


def wrong_arguments_passed():
    
    sys.stderr.write("Either there was no arguments passed or unncessary argumets were passed the file requires only one argumemts that is the url")
    sys.exit(1)


def wrong_argumnet():

    sys.stderr.write("Arguments passed was wrong correct format should be of formart: \n python.py http://<url>")
    sys.exit(1)


def check_args(argv):
    
    if argv is None:
        
        wrong_arguments_passed()
    
    if len(argv) != 2:
        
        wrong_arguments_passed()
        
    port = int(argv[1])
    
    if port <= 1024:
        
        wrong_argumnet()
    
    
    http_server = SERVER()
    http_server.connection(port)

def main(argv):
    
    check_args(argv)
    
    


if __name__ == "__main__":

    main(sys.argv)






