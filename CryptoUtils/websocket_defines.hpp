#ifndef _WEB_SOCKET_DEFINES_H
#define _WEB_SOCKET_DEFINES_H
// switch to using asio_tls_client config vs just asio_client
typedef websocketpp::client<websocketpp::config::asio_tls_client> client;

// define a tls init handler. This handler sets up the Asio TLS context however
// your application would like it configured. Here you can use the regular asio
// interface to define things like how to perform certificate validation, which
// CAs to trust, what settings and TLS versions to use, etc.
typedef websocketpp::lib::shared_ptr<boost::asio::ssl::context> context_ptr;

#endif // _WEB_SOCKET_DEFINES_H
