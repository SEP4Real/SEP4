.PHONY: test coverage clean

CC = gcc
CFLAGS = -std=c11 \
    -I./test/fakes \
    -I./test/unity \
    -I./src \
    -I./lib/drivers \
    -I./lib/util \
    -DSERVER_HOST='"localhost"' \
    -DSERVER_PORT=8080 \

test:
	$(CC) $(CFLAGS) src/wifi_http.c test/unity/unity.c test/wifi_http_tests.c -o test_wifi_http
	./test_wifi_http
	rm -f test_wifi_http

	$(CC) $(CFLAGS) src/server_api.c test/unity/unity.c test/server_api_tests.c -o test_server_api
	./test_server_api
	rm -f test_server_api

	$(CC) $(CFLAGS) src/display_status.c test/unity/unity.c test/display_status_test.c -o test_display_status
	./test_display_status
	rm -f test_display_status

coverage:
	$(CC) $(CFLAGS) --coverage src/wifi_http.c test/unity/unity.c test/wifi_http_tests.c -o test_wifi_http
	./test_wifi_http
	rm -f test_wifi_http

	$(CC) $(CFLAGS) --coverage src/server_api.c test/unity/unity.c test/server_api_tests.c -o test_server_api
	./test_server_api
	rm -f test_server_api

	$(CC) $(CFLAGS) --coverage src/display_status.c test/unity/unity.c test/display_status_test.c -o test_display_status
	./test_display_status
	rm -f test_display_status

	lcov --capture --directory . --output-file coverage.info \
	     --ignore-errors mismatch,unused
	lcov --remove coverage.info \
	     '*/fakes/*' '*/unity/*' '*/test/*' '/usr/*' \
	     --output-file coverage.info --ignore-errors unused
	genhtml coverage.info --output-directory coverage-html
	rm -f *.gcda *.gcno

clean:
	rm -f test_wifi_http test_server_api test_display_status *.gcda *.gcno coverage.info
	rm -rf coverage-html