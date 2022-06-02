import sys
import socket


# class definition begins
class HTTP_CLIENT:

    def __init__(self):
    
        self.scheme = None
        self.host_name = None
        self.port = None
        self.query = None
        self.html_body = None
        self.redirect_count = 0
        self.s = None
        self.port = None
        self.url = None
        self.response = None
        self.path = None
        self.defaul_port = 80
    
    def url_parser(self, url):
        
        #parsing url in the form of scheme://host:port/path?query
        self.response = {}
        if(self.redirect_count == 10):
            sys.stderr.write("Redirected upto 10 times\n")
            sys.exit(1)
        scheme = ""
        host_name = ""
        port = ""
        query = ""
        path = ""

        new_url = url.split("://")
       
        scheme = new_url[0]
        if(len(new_url) == 2):
            new_url2 = new_url[1].split("/", 1)
            host_name = new_url2[0]
             #extracting port if its there
            if(':' in host_name):
                res = host_name.split(":")
                port = res[1]
                host_name = res[0]
            #extracting path if its there
            if(len(new_url2) == 2):
                path = new_url2[1]
                 #extracting query if its there
                if '?' in new_url2:
                    res = path.split("?")
                    query = res[1]
                    path = res[0]
                    
        self.scheme = scheme
        self.host_name = host_name
        self.port = port
        self.query = query
        self.path = path
        self.get()
    
    def get(self):
        

        tmp_port = None

        #declaring socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostbyname(self.host_name)
        
        #checking if url has port if it has than assgining it to tmp port
        if self.port:
            tmp_port = int(self.port)
        else:
            tmp_port = self.defaul_port
        s.connect((host, tmp_port))
        
        #reciving whole message till its empty
        recieve_final = b''
        s.send(self.form_request(self.path,self.host_name).encode())
        while True:
            
            recieve = s.recv(4096)
            recieve_final += recieve
            
            if len(recieve) < 4096 :
                break
            
        
        #extracting message response
        self.extract_response(recieve_final)

        #closing the socket connection
        s.close()
        
        #checking the content type
        if(self.response["content_type"] != 'text/html'):
            sys.stderr.write("Wrong content type requested we support only text/html\n")
            sys.exit(1)
        
        #checking status code and replynig to syastem depending on it.
        if int(self.response["status_code"]) >= 400:

            sys.stderr.write(str(self.response["status_code"] + ": " + self.response["status_msg"]))
            sys.exit(1)

        elif int(self.response["status_code"]) == 301 or int(self.response["status_code"]) == 302:

            
            self.redirect_count += 1
            
            if(self.response["location"] is None):
                sys.stderr.write("No redirect link found in response\n")
                sys.exit(1)
            
            if("http://" not in self.response["location"]):
                sys.stderr.write("Wrong redirect link\n")
                sys.exit(1)
            
            sys.stderr.write("Redirected to " + self.response["location"] +"\n" )
            self.url_parser(self.response["location"])

        elif int(self.response["status_code"]) == 200:

            if(self.html_body):
                sys.stdout.write(self.html_body)
                sys.exit(0)
            else:
                sys.stderr.write(str(self.response["status_code"] + ": " + self.response["status_msg"]))
                sys.exit(1)
        else:
            sys.exit(1)
    
    # extracting response using\r\n and \r\n\r\n theory
    def extract_response(self,response):
        
        decoded_Response = response.decode("ASCII",errors="ignore")
        lines = decoded_Response.split('\r\n')
        status_response = lines[0]
        status_parts = status_response.split(" ")
        self.response["http-version"] = status_parts[0]
        self.response["status_code"] = status_parts[1]
        self.response["status_msg"] = status_parts[2]
        for line in lines:
            values = line.split(' ')
            if(len(values)>= 2):
                header_tag = values[0][:-1]
                if(header_tag == "Content-Type"):
                    header_value = ' '.join(values[1:])
                    tmp = header_value.split(';')[0].strip()
                    if tmp == 'text/html':
                        self.response["content_type"] = 'text/html'
                    elif tmp == 'application/json':
                        self.response["content_type"] = 'application/json'
                    else:
                        self.response["content_type"] = 'unknown'
                elif(header_tag == "Location"):
                    self.response['location'] = ' '.join(values[1:])
                elif(header_tag == "Host"):
                    self.response['host'] = ' '.join(values[1:])
                elif(header_tag == "Content-Length"):
                    self.response['content_length'] = int(' '.join(values[1:]))
                    
        self.html_body = response.decode().split('\r\n\r\n', 1)[1]
                    
    
    def form_request(self,path,host_name):
        
        return "GET /"+path+" HTTP/1.1\r\nHost:"+host_name+" \r\n\r\n"

# class definition ends

def wrong_arguments_passed():
    
    sys.stderr.write("Either there was no arguments passed or unncessary argumets were passed the file requires only one argumemts that is the url")
    sys.exit(1)


def wrong_input_format():

    sys.stderr.write("Arguments passed was wrong correct format should be of formart: \n python.py http://<url>")
    sys.exit(1)


def check_args(argv):
    
    if argv is None:
        
        wrong_arguments_passed()
    
    if len(argv) != 2:
        
        wrong_arguments_passed()
        
    url = argv[1]
    
    if len(url) < 7:
        
        wrong_input_format()
    
    if url[0:7] != "http://":
        
        wrong_input_format()

    http_handler = HTTP_CLIENT()
    http_handler.url_parser(url)

def main(argv):
    
    check_args(argv)
    
    


if __name__ == "__main__":

    main(sys.argv)
