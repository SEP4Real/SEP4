#include "wifi.h"
#include <string.h>
#include <stdbool.h>
#include <stdio.h>
#include <util/delay.h>
#include "uart.h"

#define WIFI_DATABUFFERSIZE 128
static uint8_t wifi_dataBuffer[WIFI_DATABUFFERSIZE];
static uint8_t wifi_dataBufferIndex;
static uint32_t wifi_baudrate;
static void (*_callback)(uint8_t byte);

typedef enum { TCP_IDLE, TCP_MATCH_PREFIX, TCP_LENGTH, TCP_DATA } tcp_state_t;
static tcp_state_t tcp_state = TCP_IDLE;
static int tcp_length = 0;
static int tcp_index = 0;
static int tcp_prefix_index = 0;

static void wifi_TCP_callback(uint8_t byte);

static void wifi_callback(uint8_t received_byte)
{
    if(NULL != _callback){
        _callback(received_byte);
    }
}

static void wifi_command_callback(uint8_t received_byte)
{
    if (wifi_dataBufferIndex < WIFI_DATABUFFERSIZE - 1) {
        wifi_dataBuffer[wifi_dataBufferIndex] = received_byte;
        wifi_dataBufferIndex++;
        wifi_dataBuffer[wifi_dataBufferIndex] = '\0';
    }
}

void wifi_init()
{
    wifi_baudrate = 115200;
    uart_init(UART2_ID, wifi_baudrate, wifi_callback, 0);
}

void static wifi_clear_databuffer_and_index()
{
    for (uint16_t i = 0; i < WIFI_DATABUFFERSIZE; i++){
        wifi_dataBuffer[i] = 0;
    }
    wifi_dataBufferIndex = 0;
}

WIFI_ERROR_MESSAGE_t wifi_command(const char *str, uint16_t timeOut_s)
{
    void* callback_state = _callback;
    _callback = wifi_command_callback;

    char sendbuffer[128];
    strcpy(sendbuffer, str);

    uart_send_string_blocking(UART2_ID, strcat(sendbuffer, "\r\n"));

    for (uint16_t i = 0; i < timeOut_s * 100UL; i++) 
    {
        _delay_ms(10);
        
        if (strstr((char *)wifi_dataBuffer, "OK\r\n") != NULL || strstr((char *)wifi_dataBuffer, "ERROR\r\n") != NULL || strstr((char *)wifi_dataBuffer, "UNLINK\r\n") != NULL)
        {
            break;
        }
    }

    WIFI_ERROR_MESSAGE_t error;

    if (wifi_dataBufferIndex == 0)
        error=WIFI_ERROR_NOT_RECEIVING;
    else if (strstr((char *)wifi_dataBuffer, "OK") != NULL)
        error=WIFI_OK;
    else if (strstr((char *)wifi_dataBuffer, "ERROR") != NULL)
        error= WIFI_ERROR_RECEIVED_ERROR;
    else if (strstr((char *)wifi_dataBuffer, "FAIL") != NULL)
        error= WIFI_FAIL;
    else
        error= WIFI_ERROR_RECEIVING_GARBAGE;
    
    wifi_clear_databuffer_and_index();
    _callback = callback_state;
    return error; 
}

WIFI_ERROR_MESSAGE_t wifi_command_AT()
{
    return wifi_command("AT", 1);
}

WIFI_ERROR_MESSAGE_t wifi_command_join_AP(char *ssid, char *password)
{
    char sendbuffer[128];
    strcpy(sendbuffer, "AT+CWJAP=\"");
    strcat(sendbuffer, ssid);
    strcat(sendbuffer, "\",\"");
    strcat(sendbuffer, password);
    strcat(sendbuffer, "\"");

    return wifi_command(sendbuffer, 20);
}

WIFI_ERROR_MESSAGE_t wifi_command_disable_echo()
{
    return wifi_command("ATE0", 1);
}

WIFI_ERROR_MESSAGE_t wifi_command_get_ip_from_URL(char * url, char *ip_address){
    char sendbuffer[128];
    strcpy(sendbuffer, "AT+CIPDOMAIN=\"");
    strcat(sendbuffer, url);
    strcat(sendbuffer, "\"");
    
    uint16_t timeOut_s = 5;

    void* callback_state = _callback;
    _callback = wifi_command_callback;

    uart_send_string_blocking(UART2_ID, strcat(sendbuffer, "\r\n"));

    for (uint16_t i = 0; i < timeOut_s * 100UL; i++)
    {
        _delay_ms(10);
        if (strstr((char *)wifi_dataBuffer, "OK\r\n") != NULL)
            break;
    }

    WIFI_ERROR_MESSAGE_t error;

    if (wifi_dataBufferIndex == 0)
        error=WIFI_ERROR_NOT_RECEIVING;
    else if (strstr((char *)wifi_dataBuffer, "OK") != NULL)
        error=WIFI_OK;
    else if (strstr((char *)wifi_dataBuffer, "ERROR") != NULL)
        error= WIFI_ERROR_RECEIVED_ERROR;
    else if (strstr((char *)wifi_dataBuffer, "FAIL") != NULL)
        error= WIFI_FAIL;
    else
        error= WIFI_ERROR_RECEIVING_GARBAGE;
    
    char *ipStart = strstr((char *)wifi_dataBuffer, "CIPDOMAIN:");
    if (ipStart != NULL) {
        ipStart += strlen("CIPDOMAIN:");
        char * ipEnd = strchr(ipStart, '\r');
        if (ipEnd != NULL && (ipEnd - ipStart) < 16) {
            strncpy(ip_address, ipStart, ipEnd - ipStart);
            ip_address[ipEnd - ipStart] = '\0';
        } 
    }

    wifi_clear_databuffer_and_index();
    _callback = callback_state;
    return error; 
}


WIFI_ERROR_MESSAGE_t wifi_command_quit_AP(){
    return wifi_command("AT+CWQAP", 5);
}

WIFI_ERROR_MESSAGE_t wifi_command_set_mode_to_1()
{
    return wifi_command("AT+CWMODE=1", 1);
}

WIFI_ERROR_MESSAGE_t wifi_command_set_to_single_Connection()
{
    return wifi_command("AT+CIPMUX=0", 1);
}

WIFI_ERROR_MESSAGE_t wifi_command_close_TCP_connection()
{
    return wifi_command("AT+CIPCLOSE", 5);
}


#define BUF_SIZE 128
#define IPD_PREFIX "+IPD,"
#define PREFIX_LENGTH 5

WIFI_TCP_Callback_t callback_when_message_received_static;
char *received_message_buffer_static_pointer;

static void wifi_TCP_callback(uint8_t byte)
{
    switch(tcp_state) {
        case TCP_IDLE:
            if(byte == IPD_PREFIX[0]) {
                tcp_state = TCP_MATCH_PREFIX;
                tcp_prefix_index = 1;
            }
            break;

        case TCP_MATCH_PREFIX:
            if(byte == IPD_PREFIX[tcp_prefix_index]) {
                if(tcp_prefix_index == PREFIX_LENGTH - 1) {
                    tcp_state = TCP_LENGTH;
                } else {
                    tcp_prefix_index++;
                }
            } else {
                tcp_state = TCP_IDLE;
                tcp_prefix_index = 0;
            }
            break;

        case TCP_LENGTH:
            if(byte >= '0' && byte <= '9') {
                tcp_length = tcp_length * 10 + (byte - '0');
            } else if(byte == ':') {
                tcp_state = TCP_DATA;
                tcp_index = 0; 
            } else {
                tcp_state = TCP_IDLE;
                tcp_length = 0;
            }
            break;

        case TCP_DATA:
            if(tcp_index < tcp_length) {
                if (tcp_index < 1023) { 
                    received_message_buffer_static_pointer[tcp_index] = byte;
                }
                tcp_index++;
            }
            
            if(tcp_index == tcp_length) {
                if (tcp_length < 1024) {
                    received_message_buffer_static_pointer[tcp_length] = '\0';
                } else {
                    received_message_buffer_static_pointer[1023] = '\0';
                }

                tcp_state = TCP_IDLE;
                tcp_length = 0;
                tcp_index = 0;

                wifi_clear_databuffer_and_index();
                callback_when_message_received_static();
            }
            break;
    }
}

WIFI_ERROR_MESSAGE_t wifi_command_create_TCP_connection(char *IP, uint16_t port, WIFI_TCP_Callback_t callback_when_message_received, char *received_message_buffer)
{
    tcp_state = TCP_IDLE;
    tcp_length = 0;
    tcp_index = 0;
    tcp_prefix_index = 0;

    received_message_buffer_static_pointer = received_message_buffer;
    callback_when_message_received_static = callback_when_message_received;
    char sendbuffer[128];
    char portString[7];

    strcpy(sendbuffer, "AT+CIPSTART=\"TCP\",\"");
    
    strcat(sendbuffer, IP);
    strcat(sendbuffer, "\",");
    sprintf(portString, "%u", port);
    strcat(sendbuffer, portString);

    WIFI_ERROR_MESSAGE_t errorMessage = wifi_command(sendbuffer, 20);
    if (errorMessage != WIFI_OK){
        return errorMessage;
    }
    else{
        _callback = wifi_TCP_callback;
    }

    wifi_clear_databuffer_and_index();
    return errorMessage;
}

WIFI_ERROR_MESSAGE_t wifi_command_TCP_transmit(uint8_t * data, uint16_t length)
{
    char sendbuffer[128];
    char portString[7];
    strcpy(sendbuffer, "AT+CIPSEND=");
    sprintf(portString, "%u", length);
    strcat(sendbuffer, portString);

    WIFI_ERROR_MESSAGE_t errorMessage = wifi_command(sendbuffer, 20);
    if (errorMessage != WIFI_OK){
        return errorMessage;
    }
    
    uart_write_bytes(UART2_ID, data, length);
    return WIFI_OK;
}