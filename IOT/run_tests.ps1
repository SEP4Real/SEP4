$ErrorActionPreference = "Stop"

$commonFlags = @(
    "-std=c11",
    "-I./test/fakes",
    "-I./test/unity",
    "-I./src",
    "-I./lib/drivers",
    "-I./lib/util",
    '-DSERVER_HOST=\"localhost\"',
    "-DSERVER_PORT=8080"
)

gcc @commonFlags src/wifi_http.c test/unity/unity.c test/wifi_http_tests.c -o test_wifi_http.exe
.\test_wifi_http.exe

gcc @commonFlags src/server_api.c test/unity/unity.c test/server_api_tests.c -o test_server_api.exe
.\test_server_api.exe

Remove-Item -Force test_wifi_http.exe, test_server_api.exe
