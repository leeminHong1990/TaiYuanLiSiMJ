var http = require('http');
var url = require('url');
var fs = require('fs');
var path = require('path');

var server = http.createServer(function (request, response) {
    var pathname = url.parse(request.url).pathname;
    var realPath = 'index.html';
    if (pathname !== '/')
        realPath = pathname.substr(1);
    fs.exists(realPath, function (exists) {
        if (!exists) {
            console.log(pathname)
            response.writeHead(404, {
                'Content-Type': 'text/plain'
            });

            response.write("This request URL " + pathname + " was not found on this server.");
            response.end();
        } else {
            fs.readFile(realPath, "binary", function (err, file) {
                if (err) {
                    console.log(realPath, err);
                    response.writeHead(500, {
                        'Content-Type': 'text/plain'
                    });
                    response.end();
                } else {
                    response.writeHead(200, {
                        'Content-Type': 'text/html'
                    });
                    if (realPath.endsWith(".html")) {
                        var str = "<head><META HTTP-EQUIV=\"Pragma\" CONTENT=\"no-cache\"><META HTTP-EQUIV=\"Cache-Control\" CONTENT=\"no-cache\"><META HTTP-EQUIV=\"Expires\" CONTENT=\"0\">"
                        file = file.replace("<head>", str)
                    }
                    response.write(file, "binary");
                    response.end();
                }
            });
        }
    });
});
var PORT = 8081;
server.listen(PORT)