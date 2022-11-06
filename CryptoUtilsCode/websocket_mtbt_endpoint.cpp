/**
   \file CryptoCode/Utils/websocket_setting.cpp

   \author: (c) Copyright Two Roads Technological Solutions Pvt Ltd 2011
   Address:
   Suite 217, Level 2, Prestige Omega,
   No 104, EPIP Zone, Whitefield,
   Bangalore - 560066
   India
   +91 80 4060 0717
 */

#include <iostream>
#include <sstream>
#include <string>
#include <unistd.h>
#include <unordered_map>
#include <vector>

#include "CryptoCode/CryptoUtils/websocket_mtbt_endpoint.hpp"

namespace CRYPTO {

context_ptr on_tls_init_cb(websocketpp::connection_hdl) {
  context_ptr ctx = websocketpp::lib::make_shared<boost::asio::ssl::context>(boost::asio::ssl::context::sslv23);

  try {
    ctx->set_options(boost::asio::ssl::context::default_workarounds | boost::asio::ssl::context::no_sslv2 |
                     boost::asio::ssl::context::no_sslv3 | boost::asio::ssl::context::single_dh_use);
  } catch (std::exception &e) {
    std::cout << e.what() << std::endl;
  }
  return ctx;
}

int WebsocketMTBTEndpoint::connect() {
  websocketpp::lib::error_code ec;

  // Register the TLS handler with the endpoint. Note this must happen before
  // any calls to get_connection().

  m_endpoint.set_tls_init_handler(&on_tls_init_cb);

  std::string uri = websocket_raw_handler_->get_connect_url();

  client::connection_ptr con = m_endpoint.get_connection(uri, ec);
  if (ec) {
    std::cout << "> Connect initialization error: " << ec.message() << std::endl;
    return -1;
  }

  hdl = con->get_handle();
  con->set_open_handler(
      websocketpp::lib::bind(&WebsocketMTBTEndpoint::on_open, this, &m_endpoint, websocketpp::lib::placeholders::_1));
  con->set_fail_handler(
      websocketpp::lib::bind(&WebsocketMTBTEndpoint::on_fail, this, &m_endpoint, websocketpp::lib::placeholders::_1));
  con->set_close_handler(
      websocketpp::lib::bind(&WebsocketMTBTEndpoint::on_close, this, &m_endpoint, websocketpp::lib::placeholders::_1));
  con->set_message_handler(websocketpp::lib::bind(&WebsocketMTBTEndpoint::on_message, this,
                                                  websocketpp::lib::placeholders::_1,
                                                  websocketpp::lib::placeholders::_2));
  m_endpoint.connect(con);
  websocket_raw_handler_->connect();
  return m_id;
}

void WebsocketMTBTEndpoint::on_message(websocketpp::connection_hdl, client::message_ptr msg) {
  //    std::cout <<"Open On_message: " << m_status << std::endl;
  if (msg->get_opcode() == websocketpp::frame::opcode::text) {
    //   std::cout << "Getting Payload opcode" << msg->get_payload() << std::endl;  // current getting in this
    websocket_raw_handler_->on_message(msg->get_payload());
  } else {
    std::cout << "Getting Payload hex " << websocketpp::utility::to_hex(msg->get_payload()) << std::endl;
    //  websocket_raw_handler_->on_message(websocketpp::utility::to_hex(msg->get_payload()));
  }
}

void WebsocketMTBTEndpoint::on_fail(client *c, websocketpp::connection_hdl hdl) {
  m_status = "Failed";
  client::connection_ptr con = c->get_con_from_hdl(hdl);
  m_server = con->get_response_header("Server");
  m_error_reason = con->get_ec().message();
  print_status(" Reason: " + m_error_reason);
  websocket_raw_handler_->on_fail();
}

void WebsocketMTBTEndpoint::on_close(client *c, websocketpp::connection_hdl hdl) {
  m_status = "Closed";
  client::connection_ptr con = c->get_con_from_hdl(hdl);
  std::stringstream s;
  gettimeofday(&tv_, NULL);
  s << "At Time: " << tv_.tv_sec << "." << tv_.tv_usec << "close code: " << con->get_remote_close_code() << " ("
    << websocketpp::close::status::get_string(con->get_remote_close_code())
    << "), close reason: " << con->get_remote_close_reason();
  m_error_reason = s.str();
  print_status(" Reason: " + m_error_reason);

  connect();
  std::cout << "Reconnection Tried " << tv_.tv_sec << "." << tv_.tv_usec << std::endl;
  websocket_raw_handler_->on_close();
}

void WebsocketMTBTEndpoint::on_open(client *c, websocketpp::connection_hdl hdl) {
  m_status = "Open";
  websocketpp::lib::error_code ec;
  std::string subscribe_ = websocket_raw_handler_->get_subsribe_str();

  if (exchange_ == "COINBASE") {
    std::cout << "Subscribe Messge to send: " << subscribe_ << std::endl;
    m_endpoint.send(hdl, subscribe_, websocketpp::frame::opcode::text, ec);
  }
  if (ec) {
    std::cout << "> Error sending message: " << ec.message() << std::endl;
    return;
  }

  client::connection_ptr con = c->get_con_from_hdl(hdl);
  m_server = con->get_response_header("Server");
  print_status();
  websocket_raw_handler_->on_open();
}

}  // namespace CRYPTO
