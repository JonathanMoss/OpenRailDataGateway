#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <zlib.h>
#include <amqp.h>
#include <amqp_tcp_socket.h>
#include <amqp_socket.h> 

#define BUFFER_SIZE 1024

void error(const char *msg) {
    fprintf(stderr, "%s\n", msg);
    exit(1);
}

char *receive_frame(int sockfd) {
    char buffer[BUFFER_SIZE];
    char *frame = NULL;
    int pos = 0;
    int len = 0;
    int frame_len = 0;

    // Read until we have received the complete frame
    while (1) {
        len = read(sockfd, buffer, BUFFER_SIZE);
        if (len < 0) {
            error("Error reading from socket");
        }
        if (len == 0) {
            error("Connection closed by server");
        }
        frame = realloc(frame, pos + len);
        memcpy(frame + pos, buffer, len);
        pos += len;
        frame_len = pos - 1;
        if (frame[frame_len - 1] == '\n' && frame[frame_len] == '\0') {
            break;
        }
    }

    // Strip trailing newline and null characters from frame
    if (frame_len > 1) {
        frame[frame_len - 1] = '\0';
    } else {
        error("Error receiving message frame");
    }

    return frame;
}

int main(int argc, char *argv[]) {
    // Read environment variables for connection details
    char *stomp_host = getenv("DARWIN_HOST");
    char *stomp_port = getenv("DARWIN_PORT");
    char *stomp_topic = getenv("DARWIN_TOPIC");
    char *stomp_username = getenv("DARWIN_USER");
    char *stomp_password = getenv("DARWIN_PASS");
    char *rabbitmq_host = "192.168.1.170";
    char *rabbitmq_port = getenv("RMQ_PORT");
    char *rabbitmq_username = getenv("RMQ_PROD_USER");
    char *rabbitmq_password = getenv("RMQ_PROD_PASS");

    // Create a socket and connect to the STOMP broker
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        error("Error creating socket");
    }
    struct hostent *server = gethostbyname(stomp_host);
    if (server == NULL) {
        error("Error resolving STOMP broker hostname");
    }
    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    memcpy(&serv_addr.sin_addr.s_addr, server->h_addr, server->h_length);
    serv_addr.sin_port = htons(atoi(stomp_port));
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        error("Error connecting to STOMP broker");
    }

    // Send a CONNECT frame to the STOMP broker
    char connect_frame[256];
    sprintf(connect_frame, "CONNECT\nlogin:%s\npasscode:%s\naccept-version:1.2\n\n", stomp_username, stomp_password);
    if (write(sockfd, connect_frame, strlen(connect_frame)) < 0) {
        error("Error sending CONNECT frame to STOMP broker");
    }

    // Receive a CONNECTED frame from the STOMP broker
    char *connected_frame = receive_frame(sockfd);
    if (strstr(connected_frame, "CONNECTED") == NULL) {
        error("Error receiving CONNECTED frame from STOMP broker");
    }
    free(connected_frame);

    // Subscribe to the specified topic
    char subscribe_frame[256];
    sprintf(subscribe_frame, "SUBSCRIBE\ndestination:%s\nack:auto\n\n", stomp_topic);
    if (write(sockfd, subscribe_frame, strlen(subscribe_frame)) < 0) {
        error("Error sending SUBSCRIBE frame to STOMP broker");
    }

    // Create a RabbitMQ connection and channel
    amqp_connection_state_t conn;
    amqp_socket_t *socket = NULL;
    amqp_rpc_reply_t reply;
    amqp_channel_t channel = 1;
    conn = amqp_new_connection();
    socket = amqp_tcp_socket_new(conn);
    amqp_socket_set_timeout(socket, 10000);
    if (!socket) {
        error("Error creating RabbitMQ socket");
    }
    int status = amqp_socket_open(socket, rabbitmq_host, atoi(rabbitmq_port));
    if (status) {
        error("Error opening RabbitMQ socket");
    }
    reply = amqp_login(conn, "/", 0, 131072, 0, AMQP_SASL_METHOD_PLAIN, rabbitmq_username, rabbitmq_password);
    if (reply.reply_type != AMQP_RESPONSE_NORMAL) {
        error("Error logging in to RabbitMQ server");
    }
    amqp_channel_open(conn, channel);
    reply = amqp_get_rpc_reply(conn);
    if (reply.reply_type != AMQP_RESPONSE_NORMAL) {
        error("Error opening RabbitMQ channel");
    }

    // Receive and process messages from the STOMP broker
    while (1) {
        char *message_frame = receive_frame(sockfd);
        char *message_body = strstr(message_frame, "\n\n") + 2;
        char *message_type_header = strstr(message_frame, "MessageType:");
        char *message_type = NULL;
        if (message_type_header != NULL) {
            message_type = message_type_header + 12;
        }
        int message_len = strlen(message_body);
        char message[message_len + 1];
        memcpy(message, message_body, message_len);
        message[message_len] = '\0';

        // Check if message is compressed
        char *compression_header = strstr(message_frame, "Compression:");
        if (compression_header != NULL && strncmp(compression_header + 12, "zlib", 4) == 0) {
            // Message is compressed with zlib, so decompress it
            char *decompressed = malloc(message_len * 10);
            z_stream strm;
            strm.zalloc = Z_NULL;
            strm.zfree = Z_NULL;
            strm.opaque = Z_NULL;
            strm.avail_in = message_len;
            strm.next_in = (Bytef *) message;
            strm.avail_out = message_len * 10;
            strm.next_out = (Bytef *) decompressed;
            inflateInit(&strm);
            inflate(&strm, Z_FINISH);
            inflateEnd(&strm);
            message_len = strm.total_out;
            memcpy(message, decompressed, message_len);
            message[message_len] = '\0';
            free(decompressed);
        }

        // Publish message to RabbitMQ exchange
        amqp_basic_properties_t props;
        props._flags = AMQP_BASIC_CONTENT_TYPE_FLAG | AMQP_BASIC_DELIVERY_MODE_FLAG;
        props.content_type = amqp_cstring_bytes("text/plain");
        props.delivery_mode = 2; // persistent
            amqp_bytes_t exchange_name = amqp_cstring_bytes("rabbitmq_exchange");
        amqp_bytes_t routing_key;
        if (message_type != NULL) {
            routing_key = amqp_cstring_bytes(message_type);
        } else {
            routing_key = amqp_empty_bytes;
        }
        amqp_basic_publish(conn, channel, exchange_name, routing_key, 0, 0, &props, amqp_cstring_bytes(message));
        reply = amqp_get_rpc_reply(conn);
        if (reply.reply_type != AMQP_RESPONSE_NORMAL) {
            error("Error publishing message to RabbitMQ exchange");
        }

        free(message_frame);
    }

    // Close the STOMP socket
    close(sockfd);

    // Close the RabbitMQ channel and connection
    amqp_channel_close(conn, channel, AMQP_REPLY_SUCCESS);
    amqp_connection_close(conn, AMQP_REPLY_SUCCESS);
    amqp_destroy_connection(conn);

    return 0;
}
