.PHONY: test coverage clean

CC = gcc
CFLAGS = -std=c11 \
    -I./test/fakes \
    -I./test/unity \
    -I./src \
    -I./lib/drivers \
    -I./lib/util \
    -DSERVER_HOST='"localhost"' \
    -DSERVER_PORT=8080

SRCS = \
    src/wifi_http.c \
    test/unity/unity.c \
    test/wifi_http_tests.c

test:
	$(CC) $(CFLAGS) $(SRCS) -o test_runner
	./test_runner
	rm -f test_runner

coverage:
	$(CC) $(CFLAGS) --coverage $(SRCS) -o test_runner
	./test_runner
	lcov --capture --directory . --output-file coverage.info \
	     --ignore-errors mismatch,unused
	lcov --remove coverage.info \
	     '*/fakes/*' '*/unity/*' '*/test/*' '/usr/*' \
	     --output-file coverage.info --ignore-errors unused
	genhtml coverage.info --output-directory coverage-html
	rm -f test_runner *.gcda *.gcno coverage.info

clean:
	rm -f test_runner *.gcda *.gcno coverage.info
	rm -rf coverage-html