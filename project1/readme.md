# Web Sockets and Web Servers

- In this project, we build our own web server from scratch using low-level socket module in python
- Project was subdivided into four subparts.
- Part 1
  - In part 1, we created a simple curl in which we fetch and print the body of an HTML web address.
  - To invoke and use part 1, we have to run the code 
  - python3 http_client.py http://somewebsite.com/path/page.html
  - The command can handle various HTTP responses and print stderr according to it.
- Part 2
  - In part 2, we have built a simple web server that handles one connection at a time and works with a file that ends with .html or .htm
  - Server creates a TCP socket and listens to new connections.
  - Then, the server reads HTTP requests and sees if the file exists, and If it exists, then outputs its response.
  - To run the program, we have to run the code
  - python3 http_server1.py [port]
  - Where port >= 1024
  - curl http://[hostname]:[port]/rfc2616.html

- Part 3
  - In part 3, we created a multi-connection web server.
- Part 4
  - In part 4, we created a dynamic web server that implements JSON-based API for simple multiplication.
  - It returns a JSON file that contains a response in the form of:
  ```
  {
   "operation": "product",
   "operands": [12, 60, 0.5],
   "result": 360
  }
  ```
