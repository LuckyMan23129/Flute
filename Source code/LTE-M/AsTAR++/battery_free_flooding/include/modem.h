#ifndef MODEM_H
#define MODEM_H

#include <modem/lte_lc.h>
#include <zephyr/net/socket.h>
#include <zephyr/random/rand32.h>
#include <nrf_socket.h>
#include <zephyr/kernel.h>
#include <stdio.h>
#include <nrf_modem_at.h>
#include <modem/modem_info.h>

#define UDP_IP_HEADER_SIZE 28
#define TX_BUFFER_LEN   19

#define MSGTYPE_INVALID                 0
#define MSGTYPE_SURVEY_RESULT_UPLOAD    1
#define MSGTYPE_ACK                     5
#define MSGTYPE_ACK_UPDATEREADY         6

void modem_server_transmission_work_fn(struct k_work *work);
void modem_transmitData(uint16_t capMilliVolt, uint16_t sleepTime);
void modem_main_init(void);
void modem_lte_handler(const struct lte_lc_evt *const evt);
int modem_configure_low_power(void);
void modem_modem_init(void);
void modem_modem_connect(void);
void modem_server_disconnect(void);
void modem_server_disconnect_rx(void);
int modem_udp_init(void);
void modem_survey_update_handler(void);

#endif