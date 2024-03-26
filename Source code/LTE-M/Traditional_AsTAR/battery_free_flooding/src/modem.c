#include "modem.h"

#define UDP_IP_HEADER_SIZE 28

// UDP Addresses and Sockets 
static int server_send_fd;
static struct sockaddr_in6 addr_server_sendto;

// Random number initialised message ID 
uint32_t msg_rand_id;

//static struct sockaddr_in6 addr_recv_check;

//static struct k_work_delayable server_transmission_work;

static char client_id_imei[16] = {0};
static char client_rsrp[5] = {0};
static char client_rsrp_val = 0;
//static uint16_t rxBufDataLen = 0;
static uint8_t txbuf[TX_BUFFER_LEN] = {0};
static uint16_t txbuf_len = TX_BUFFER_LEN;

K_SEM_DEFINE(lte_connected, 0, 1);

void rsrp_cb(char rsrp_value)
{
	client_rsrp_val = rsrp_value;
	printk("The RSRP of the system: %d\n", client_rsrp_val);
}

void modem_transmitData(uint16_t capMilliVolt, uint16_t sleepTime) {
	memset(txbuf, 0, TX_BUFFER_LEN);
	memcpy(&txbuf[0], client_id_imei, 15);
	txbuf[15] = (capMilliVolt >> 8) & 0xFFu;
	txbuf[16] = capMilliVolt & 0xFFu;
	txbuf[17] = (sleepTime >> 8) & 0xFFu;
	txbuf[18] = sleepTime & 0xFFu;
	txbuf_len = TX_BUFFER_LEN;
    modem_server_transmission_work_fn(NULL);
}

void modem_server_transmission_work_fn(struct k_work *work)
{
	int err;
	printk("IP address %s, port number %d\n",
		       CONFIG_UDP_SERVER_ADDRESS_STATIC,
		       CONFIG_UDP_SERVER_PORT);	

	printk("\n*********************************************\n");
	printk("Data to send over LTE-M (as integers, with IMEI embedded as ASCII):\n");
	for(int i = 0; i < txbuf_len; i++) {
		printk("%d\t", txbuf[i]);
	}
	printk("\n*********************************************\n");
	
	err = send(server_send_fd, txbuf, (size_t )txbuf_len, 0);
	if (err < 0) {
		printk("Failed to transmit UDP packet, %d %s\n", errno, strerror(errno));
	} else {
		printk("Successfully transmitted UDP packet\n");
	}
}

void modem_main_init(void)
{
    int err;
    char imei_buf[20 + sizeof("OK\r\n")];
	char rsrp_buf[10 + sizeof("OK\r\n")];

	//printk("UDP sample has started\n");

	//k_work_init_delayable(&server_transmission_work,
	//		      modem_server_transmission_work_fn);

    printk("Connecting");
	// for (int i = 0; i < 15; i++) {
	// 	k_sleep(K_SECONDS(2));
	// 	printk(".");
	// }
	printk("\n");

#if defined(CONFIG_NRF_MODEM_LIB)

	/* Initialize the modem before calling modem_configure_low_power(). This is
	 * because the enabling of RAI is dependent on the
	 * configured network mode which is set during modem initialization.
	 */
	modem_modem_init();

	err = modem_configure_low_power();
	if (err) {
		printk("Unable to set low power configuration, error: %d\n",
		       err);
	}

	modem_modem_connect();

	k_sem_take(&lte_connected, K_FOREVER);
#endif

	err = modem_udp_init();
	if (err) {
		printk("Not able to initialize UDP server connection\n");
		return;
	}

	printk("Initialising modem info library...\n");
	err = modem_info_init();
	if (err) {
		printk("Unable to initialise modem info library, error: %d\n", err);
	}

    printk("Querying IMEI\n");
	/*err = nrf_modem_at_cmd(imei_buf, sizeof(imei_buf), "AT+CGSN");
	if (err) {
		printk("Not able to retrieve device IMEI from modem\n");
    	//return;
	}*/
	modem_info_string_get(MODEM_INFO_IMEI, imei_buf, sizeof(imei_buf));
	strncpy(client_id_imei, imei_buf, sizeof(client_id_imei) - 1);
	printk("IMEI : %s\n", client_id_imei);

	//modem_info_rsrp_register(rsrp_cb);
	modem_info_string_get(MODEM_INFO_RSRP, rsrp_buf, sizeof(rsrp_buf));
	strncpy(client_rsrp, rsrp_buf, sizeof(client_rsrp) - 1);
	printk("RSRP : %s\n", client_rsrp);
}

#if defined(CONFIG_NRF_MODEM_LIB)
void modem_lte_handler(const struct lte_lc_evt *const evt)
{
	switch (evt->type) {
	case LTE_LC_EVT_NW_REG_STATUS:
		if ((evt->nw_reg_status != LTE_LC_NW_REG_REGISTERED_HOME) &&
		     (evt->nw_reg_status != LTE_LC_NW_REG_REGISTERED_ROAMING)) {
			break;
		}

		printk("Network registration status: %s\n",
			evt->nw_reg_status == LTE_LC_NW_REG_REGISTERED_HOME ?
			"Connected - home network" : "Connected - roaming\n");
		k_sem_give(&lte_connected);
		break;
	case LTE_LC_EVT_PSM_UPDATE:
		printk("PSM parameter update: TAU: %d, Active time: %d\n",
			evt->psm_cfg.tau, evt->psm_cfg.active_time);
		break;
	case LTE_LC_EVT_EDRX_UPDATE: {
		char log_buf[60];
		ssize_t len;

		len = snprintf(log_buf, sizeof(log_buf),
			       "eDRX parameter update: eDRX: %f, PTW: %f\n",
			       evt->edrx_cfg.edrx, evt->edrx_cfg.ptw);
		if (len > 0) {
			printk("%s\n", log_buf);
		}
		break;
	}
	case LTE_LC_EVT_RRC_UPDATE:
		printk("RRC mode: %s\n",
			evt->rrc_mode == LTE_LC_RRC_MODE_CONNECTED ?
			"Connected" : "Idle\n");
		break;
	case LTE_LC_EVT_CELL_UPDATE:
		printk("LTE cell changed: Cell ID: %d, Tracking area: %d\n",
		       evt->cell.id, evt->cell.tac);
		break;
	default:
		break;
	}
}

int modem_configure_low_power(void)
{
	int err;

#if defined(CONFIG_UDP_PSM_ENABLE)
	/** Power Saving Mode */
	err = lte_lc_psm_req(true);
	if (err) {
		printk("lte_lc_psm_req, error: %d\n", err);
	}
#else
	err = lte_lc_psm_req(false);
	if (err) {
		printk("lte_lc_psm_req, error: %d\n", err);
	}
#endif

#if defined(CONFIG_UDP_EDRX_ENABLE)
	/** enhanced Discontinuous Reception */
	err = lte_lc_edrx_req(true);
	if (err) {
		printk("lte_lc_edrx_req, error: %d\n", err);
	}
#else
	err = lte_lc_edrx_req(false);
	if (err) {
		printk("lte_lc_edrx_req, error: %d\n", err);
	}
#endif

#if defined(CONFIG_UDP_RAI_ENABLE)
	/** Release Assistance Indication  */
	err = lte_lc_rai_req(true);
	if (err) {
		printk("lte_lc_rai_req, error: %d\n", err);
	}
#endif

	return err;
}

void modem_modem_init(void)
{
	int err;

	printk("Modem initialization...\n");

	if (IS_ENABLED(CONFIG_LTE_AUTO_INIT_AND_CONNECT)) {
		/* Do nothing, modem is already configured and LTE connected. */
	} else {
		err = lte_lc_init();
		if (err) {
			printk("Modem initialization failed, error: %d\n", err);
			return;
		}
	}
}

void modem_modem_connect(void)
{
	int err;

	if (IS_ENABLED(CONFIG_LTE_AUTO_INIT_AND_CONNECT)) {
		/* Do nothing, modem is already configured and LTE connected. */
	} else {
		err = lte_lc_connect_async(modem_lte_handler);
		if (err) {
			printk("Connecting to LTE network failed, error: %d\n",
			       err);
			return;
		}
	}
}
#endif

void modem_server_disconnect(void)
{
	(void)close(server_send_fd);
}

int modem_udp_init(void)
{
	int err;
	int status;

	// Initialise random number based message ID
	msg_rand_id = sys_rand32_get();

	// Set up server and client addresses
	addr_server_sendto.sin6_family = AF_INET6;
	addr_server_sendto.sin6_port = htons(CONFIG_UDP_SERVER_PORT);
	status = inet_pton(AF_INET6, CONFIG_UDP_SERVER_ADDRESS_STATIC, &addr_server_sendto.sin6_addr);
	if (status == 0) {
		printk("src does not contain a character string representing a valid network address\n");
		return -1;
	} else if(status < 0) {
		printk("inet_pton failed: %d %s\n", errno, strerror(errno));
		err = -errno;
		goto error;
	}
	addr_server_sendto.sin6_scope_id = 0;

	// Set up server socket and connect
	server_send_fd = socket(AF_INET6, SOCK_DGRAM, IPPROTO_UDP);
	if (server_send_fd < 0) {
		printk("UDP socket creation failed: %d\n", errno);
		err = -errno;
		goto error;
	}
	err = connect(server_send_fd, (struct sockaddr *)&addr_server_sendto,
		      sizeof(struct sockaddr_in6));
	if (err < 0) {
		printk("Connect failed : %d\n", errno);
		goto error;
	}

	return 0;
error:
	modem_server_disconnect();
	return err;
}
/*
void modem_survey_update_handler(void) {
	static struct sockaddr_in6 addr_update_conn;
	static int update_fd;
	static int sockaddrlen = sizeof(struct sockaddr_in6);
	static ssize_t msglen;
	char update_conn_ip[INET6_ADDRSTRLEN];
	int64_t updatetime_begin = k_uptime_get();
	int64_t updatetime_current = updatetime_begin;
	uint32_t segstart = 0;
	uint32_t segend = 0;
	uint32_t currentpos = 0;
	uint32_t endofbuf = 0;
	uint16_t rx_len = 0;
	char responsebuf[255] = {0};
	char startmarker = '<';
	char endmarker = '>';

	memset(update_conn_ip, 0, sizeof(update_conn_ip));
	do {
		// 30 sec timeout
		updatetime_current = k_uptime_get();
		if((updatetime_current - updatetime_begin) > 30000) {
			return;
		}
		update_fd = accept(local_update_recv_fd, (struct sockaddr *)&addr_update_conn, &sockaddrlen);
		if (update_fd < 0) {
			if (errno != EAGAIN) {
				printk("Accept failed : %d %s\n", errno, strerror(errno));
				return;
			}
		} else {
			// Verify connection is from server
			inet_ntop(AF_INET6, &addr_update_conn.sin6_addr, update_conn_ip, sizeof(update_conn_ip));
		}
	} 
	while (strcmp(update_conn_ip, CONFIG_UDP_SERVER_ADDRESS_STATIC) != 0);

	updatetime_begin = k_uptime_get();
	updatetime_current = updatetime_begin;
	currentpos = 0;
	// 3min timeout
	while ((updatetime_current - updatetime_begin) < 180000) {
		updatetime_current = k_uptime_get();
		msglen = recv(update_fd, &updatebuf[currentpos], sizeof(updatebuf) - currentpos, MSG_DONTWAIT);
		if ((msglen < 0) && (errno != EAGAIN)) {
			printk("TCP update receive error: %d %s\n", errno, strerror(errno));
			return;
		} else if (msglen == 0) {
			// end of file
			break;
		} else if (msglen > 0) {
			currentpos += msglen;
		}	
	}
	printk("recv time: %lli ms\n", k_uptime_get() - updatetime_begin);
	printk("size of recv: %u\n", currentpos);
	if ((msglen <= 0) && (currentpos == 0)) {
		printk("Failed to receive any data\n");
		close(update_fd);
		return;
	}
	endofbuf = currentpos;
	//printk("Message Received : %s\n", updatebuf);

	close(update_fd);

	// Send UART command to get cdkManager into update mode
	cdk_sendAck(2);

	// Wait to receive update signal
	do {
		memset(responsebuf, 0, sizeof(responsebuf));\
		cdk_uart_receive(responsebuf, &rx_len);
		printk("UART Received: %s\n", responsebuf);
	}
	while (strcmp(responsebuf, "UPDATE_ME") != 0);

	currentpos = 0;
	// Send update file line by line 
	while(currentpos < sizeof(updatebuf)) {
		if ((updatebuf[currentpos] == '\n') || (currentpos == endofbuf)) {
			segend = currentpos;
			do {
				memset(responsebuf, 0, sizeof(responsebuf));
				printk("UART Sent buf positions: %u - %u\n", segstart, segend);	
				cdk_uart_transmit(&startmarker, 1);
				cdk_uart_transmit(&updatebuf[segstart], (segend - segstart));
				cdk_uart_transmit(&endmarker, 1);
				cdk_uart_receive(responsebuf, &rx_len);
				printk("UART Received: %s\n", responsebuf);			
			}
			while (strcmp(responsebuf, "ACK") != 0);
			currentpos++;
			segstart = currentpos;
		}
		if ((currentpos - 1) == endofbuf) {
			printk("Update complete!\n");
			break;
		}
		currentpos++;
	}
}*/