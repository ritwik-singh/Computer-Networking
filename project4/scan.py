import subprocess
import json
import sys
import time
import math
from requests import Response, Session
import maxminddb



def extract_ipv4(website):
    
    list_addr = []
    request = "nslookup -type=A " + website + " 1.1.1.1"
    result = None
    try:
        result = subprocess.check_output(request,timeout=3,stderr=subprocess.STDOUT,shell=True).decode("utf-8")
    except Exception as e:

        result =  None

    if result and "Name" in result:
        
        lines = result.split("Name:")[1:]
        for line in lines:
            if ':' in line:
                addrs = line.split(":",1)[1].splitlines()
                ips = [i.strip(" \r\n\t") for i in addrs]
                for addr in ips:
                    if addr != "" and addr not in list_addr:
                        
                        if '.' in addr:
                            
                            list_addr.append(addr)

    return list_addr    





def extract_ipv6(website):

    list_addr = []
    request = "nslookup -type=AAAA " + website + " 1.1.1.1"
    result = None
    try:
        result = subprocess.check_output(request,timeout=3,stderr=subprocess.STDOUT,shell=True).decode("utf-8")
    except Exception as e:
        result =  None

    if result and "Name" in result:
        lines = result.split("Name:")[1:]
        for line in lines:
            if ':' in line:

                addrs = line.split(":",1)[1].splitlines()
                ips = [i.strip(" \r\n\t") for i in addrs]

                for addr in ips:
                    if addr != "" and addr not in list_addr:
                        if ':' in addr :
                            list_addr.append(addr)

    return list_addr   



def extract_http(website):
    
    session = Session()
    http_server = None
    insecure_http = True
    redirect_http = None
    hsts = None

    try:
        response = None
        if 'http' in website:
            website = website.split(':')
            website = website[1][2:]
            if website[-1] == '/':
                website = website[:-1]
            else:
                website = website
        try:
            response = session.get('http://'+website,timeout=2)
        except:
            response = None

        if 300 <= response.status_code < 310:
            raise Exception("Redirected more than 10 times")
        
        if response.url[:8] == 'https://':
            redirect_http = True

        http_server = response.headers.get(key='Server')
        hsts_res = response.headers.get(key="Strict-Transport-Security")

        if hsts_res is None:
            hsts = False
        else:
            hsts = True

    except Exception as ex:
        
        if ex is not Exception("Redirected more than 10 times"):
                insecure_http = False
                try:
                    response = None
                    if 'http' in website:
                        website = website.split(':')
                        website = website[1][2:]
                        if website[-1] == '/':
                            website = website[:-1]
                        else:
                            website = website
                    try:
                        response = session.get('https://' + website, timeout=2)
                    except:
                        response = None

                        http_server = response.headers.get(key='Server')
                        hsts_res = response.headers.get(key="Strict-Transport-Security")

                        if hsts_res is None:
                            hsts = False
                        else:
                            hsts = True
                except:
                    pass


    return http_server, insecure_http, redirect_http, hsts


def extract_tls(website):
    response = None

    try:

        request = req = "nmap --script ssl-enum-ciphers -p 443 " + website
        response = subprocess.check_output(request, timeout=10, stderr=subprocess.STDOUT, shell=True).decode("utf-8")

    except Exception as e:

        response = ""

    result = []

    if 'TLSv1.0' in response:
        result.append('TLSv1.0')
    if 'TLSv1.1' in response:
        result.append('TLSv1.1')
    if 'TLSv1.2' in response:
        result.append('TLSv1.2')

    try:
        
        request =  "echo | timeout 2 openssl s_client -connect " + website + ":443"
        response = subprocess.check_output(request, timeout=10, stderr=subprocess.STDOUT, shell=True).decode("utf-8")

    except Exception as e:

        response = ""

    if 'New, TLSv1.3, Cipher' in response:
        result.append('TLSv1.3')
    
    ca_arg = None
    if response is not None and len(result) > 0:

        lines = response.split('---')
        ca_line = None
        for line in lines:
                if 'Certificate chain' in line:
                    ca_line = line
                    break
        #to be chnage
        if ca_line is not None:
            arg = ca_line.split('\n')
            if 'O = ' in arg[-2]:
                tmp = arg[-2].split('O = ')
                if 'CN = ' in tmp[-1]:
                        ca_arg = tmp[-1].split('CN = ')[0]
                        if 'OU = ' in ca_arg:
                                ca_arg = ca_arg.split('OU = ')[0]

    
    return result, ca_arg




def extract_dns(ips):
    
    names = []
    for ip in ips:
        req = 'nslookup ' + ip
        res = None
        try:
            res = subprocess.check_output(req,timeout=2,stderr=subprocess.STDOUT,shell=True).decode("utf-8")
        except:
            res = None
        if res:
            for line in res.splitlines():
                if 'name =' in line or 'Name:' in line:
                    name = line.split('name =')[1]
                    name = name.strip(' \t\r\n')
                    if 'name =' in line:
                        name = name[:-1]
                    if name not in names:
                        names.append(name)
    return names




def extract_rtt(ips,port):
    
    min_rtt = float("inf")
    max_rtt = float("-inf")

    for ip in ips:
        response = None
        try:
            requests = 'sh -c "time echo -e \'\\x1dclose\\x0d\' | timeout 2 telnet ' + ip + ' ' + port + '"'
            response = subprocess.check_output(requests, timeout=2,stderr=subprocess.STDOUT, shell=True).decode("utf-8")
        except subprocess.CalledProcessError as e:
            response = e.output.decode("utf-8")
        except Exception as ex:
            response = None
        
        if response and "real" in response:

            msg = response.split('real')
            msg = msg[1].splitlines()[0]
            msg = msg.strip(' \t\r\n')
            try:
                time_taken = float(msg[2:-1])

                if min_rtt > time_taken:
                    min_rtt = time_taken
                if max_rtt < time_taken:
                    max_rtt = time_taken
            
            except Exception as e:
                pass
    if math.isinf(min_rtt) or math.isinf(max_rtt):
        if port == "443":
            return extract_rtt(ips,"80")
        elif port == "80":
            return extract_rtt(ips,"22")
        else:
            return None

    else:
        return [min_rtt, max_rtt]
        




def extract_geo(reader,ips):
    
    locations_list = []

    for ip in ips:

        location = reader.get(ip)
        city = None
        province = None 
        country = None

        if "country" in location and "en" in location["country"]["names"]:
            country = location["country"]["names"]["en"]
        elif "continent" in location and "en" in location["continent"]["names"]:
            country = location["continent"]["names"]["en"]
        if "subdivisions" in location and len(location["subdivisions"]) > 0 and "en" in location["subdivisions"][0]["names"]:
            province = location["subdivisions"][0]["names"]["en"]
        if "city" in location and "en" in location["city"]["names"]:
            city = location["city"]["names"]["en"]
        
        location_text = ""

        if city:
                location_text = city
        if province:
            if len(location_text) > 0:
                location_text += ', '
            location_text += province
        if country:
            if len(location_text) > 0:
                location_text += ', '
            location_text += country

        if location_text not in locations_list:
            locations_list.append(location_text)

    return locations_list




def parse_txt(file):

    list = []

    with open(file) as f:
        for lines in f:
            website = lines.split('\n')[0]
            list.append(website)
    
    return list


def main():

    websites =  parse_txt(sys.argv[1])
    geo_reader = maxminddb.open_database('GeoLite2-City_20201103/GeoLite2-City.mmdb')
    final_scan = dict()

    for website in websites:

        website_details = dict()
        # Details to be extracted
        # Scan Time

        website_details['scan_time'] = time.time()
 
        # Ipv4 Address 

        website_details['ipv4_addresses'] = extract_ipv4(website)

        # Ipv6 Address

        website_details['ipv6_addresses'] = extract_ipv6(website)




        # http server, insecure http, redirect to https, and hsts
        website_details["http_server"], website_details["insecure_http"], website_details["redirect_to_https"], website_details["hsts"] = extract_http(website)




        # tls versions and root ca
        website_details['tls_versions'], website_details['root_ca'] = extract_tls(website)




        # rdns name
        website_details['rdns_names'] = extract_dns(website_details['ipv4_addresses'])



        # rtt range
        website_details["rtt_range"] = extract_rtt(website_details['ipv4_addresses'],'443')



        # geo locations_list
        website_details["geo_locations_list"] = extract_geo(geo_reader,website_details['ipv4_addresses'])




        #scanning complete
        final_scan[website] = website_details



    geo_reader.close()
    
    # write to the file

    with open(sys.argv[2],"w") as f:
        json.dump(final_scan,f,sort_keys=True,indent=4)


#calling of the main method
if __name__ == '__main__':

    main()
