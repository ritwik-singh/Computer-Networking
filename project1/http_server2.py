import sys
import os
import datetime
import select
import socket

"Requires a file folder that contains html file on server"

class SERVER:
    
   
        
    
        
    def make_connection(self, port):
        
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.s.bind(('',port))
        # self.s.setblocking(0)
        # self.s.listen(10)
        # connection_list = [self.s]
        # outputs = []
        
        # while connection_list:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.bind(('', port))
        

        self.sock.listen(10)

        read_list = [self.sock]

        while read_list:
            reads, writes, exceptions = select.select(read_list, [], read_list)

            for read in reads:
                if read is self.sock:
                    conn, addr = self.sock.accept()
                    print("Connected", addr)
                    conn.setblocking(1)
                    read_list.append(conn)
                else:
                    data = read.recv(4096)
                    self.process(data, read)
                    read_list.remove(read)
                    read.close()
          
            # connections, writes, exceptions = select.select(connection_list, outputs, connection_list)
            
            # print("connection list")
            # print(connection_list)
            # for connection in connections:
                
            #     if connection is self.s:
                    
            #         print("enter connection")
            #         conn, addr = self.s.accept()
            #         conn.setblocking(0)
            #         connection_list.append(conn)
                    
            #     else:
                    
            #         print("enter data")
            #         data = connection.recv(4096)

            #         if not data:
            #             print("data not found")
            #             connection_list.remove(connection)
            #             connection.close()
            #             break
                        
            #         else:
            #             print("got data")
            #             self.process(data,connection)
            for exception in exceptions:
                read_list.remove(exception)
                exception.close()
                        
    
    def process(self,data, connection):
        
        self.message = {}           
        self.extract_message(data)
        print(f"method: "+ self.message["http-method"])
        if self.message["http-method"] == "GET":
            
            if self.message["address"][-4:] != ".htm" and self.message["address"][-5:] != ".html":
                print(self.message["address"])
                return_response =  ('HTTP/1.1' + " " + '403' + " " +  "Forbidden") + \
                ('\r\nHost: ' +  "") + \
                ('\r\nLocation: ' + "") + \
                ('\r\nContent-Type: ' + 'application/json') + \
                ('\r\nContent-Length: ' + str(len(('We support only HTML file').encode('ASCII')))) + \
                ('\r\nDate: ') + \
                ('\r\n\r\n' + 'We support only HTML file')
            
                connection.sendall(str(return_response).encode('ASCII'))
                
                
            else:
                
                file_name = self.message["address"][1:]
                response = self.read_file(file_name)
                
                if response:
                    return_response =  ('HTTP/1.1' + " " + '200' + " " +  "OK") + \
                    ('\r\nHost: ' +  "") + \
                    ('\r\nLocation: ' "") + \
                    ('\r\nContent-Type: ' + 'text/html') + \
                    ('\r\nContent-Length: ' + str(len(response.encode('utf-8')))) + \
                    ('\r\nDate: ' + "") + \
                    ('\r\n\r\n' + response)

                    print(return_response)
                    connection.sendall(str(return_response).encode('utf-8'))
                    
                    
                else:
                    return_response =  ('HTTP/1.1' + " " + '404' + " " +  "Not Found") + \
                    ('\r\nHost: ' +  "") + \
                    ('\r\nLocation: ' "") + \
                    ('\r\nContent-Type: ' + 'application/json') + \
                    ('\r\nContent-Length: ' + str(len(('HTML file not found').encode('ASCII')))) + \
                    ('\r\nDate: '+ "") + \
                    ('\r\n\r\n' + 'HTML file not found')
                
                    connection.sendall(str(return_response).encode('ASCII'))
                    
        else:
            return_response =  ('HTTP/1.1' + " " + '400' + " " +  "Bad Request") + \
            ('\r\nHost: ' ) + \
            ('\r\nLocation: ' ) + \
            ('\r\nContent-Type: ' + 'application/json') + \
            ('\r\nContent-Length: ' + str(len(('We support only get method').encode('ASCII')))) + \
            ('\r\nDate: ' ) + \
            ('\r\n\r\n' + 'We support only get method')

            connection.sendall(str(return_response).encode('ASCII'))
            
            

        
                
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
                elif(header_tag == "Host"):
                    self.message['host'] = ' '.join(values[1:])
                elif(header_tag == "Content-Length"):
                    self.message['content_length'] = int(' '.join(values[1:]))
                    
        self.html_body = message.decode().split('\r\n\r\n', 1)[1]
        
        
        
    
    def read_file(self,file_name):
        
        
        if file_name[-4:] == "html" or file_name[-3:] == "htm":
            
            if file_name[-3:] == "htm":
                file_name = file_name + "l"
            
        
            

        file = None
        if os.path.exists('files/' + file_name):
            file = open('files/' + file_name, 'r')
       
        if file:
            file_content = file.read()
            file.close()

            return file_content
        return None
    


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
    http_server.make_connection(port)

def main(argv):
    
    check_args(argv)
    
    
if __name__ == "__main__":

    main(sys.argv)






