# Network Exploration and Security Auditing

In this project we wrote a tool for network exploration and security auditing. The tool takes list of domains, it will return a report which contains certain network characterstics and security features of each domains.

## Learnings

1. The project gave us high-level understanding of several important web security protocols.
2. How to build a python tool that uses command-line utilities
3. How to desgin a software and how to implement complex set of interralted tasks.

## Running the project

To run the project run the following commands:

1. Run Scanner to scan all the attributes and save it in json file

   ```
   python scan.py test_websites.txt out.json
   ```
   
2. Run Report genrator to scan all the collected information and store it in a tabular and readable form.

   ```
   python report.py out.json report.txt
   ```

## Report

The report contained the following attributes of a domain:

1. A textual or tabular listing of all the information returned in Part 2, with a section for each domain.
2. A table showing the RTT ranges for all domains, sorted by the minimum RTT (ordered from fastest to slowest).
3. A table showing the number of occurrences for each observed root certificate authority (from Part 2i), sorted from most popular to least.
4. A table showing the number of occurrences of each web server (from Part 2d), ordered from most popular to least.
5. A table showing the percentage of scanned domains supporting:
    * each version of TLS listed in Part 2h. I expect to see close to zero percent for SSLv2 and SSLv3.
    * "plain http" 
    * "https redirect" 
    * "hsts" 
    * "ipv6"
## Ouput

To see the ouptut of scan.py plesase go to [report_out.txt](report_out.txt)
