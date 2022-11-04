/**
   \file websocket_enpoint.hpp

   \author: (c) Copyright Two Roads Technological Solutions Pvt Ltd 2011
   Address:
   Suite No 353, Evoma, #14, Bhattarhalli,
   Old Madras Road, Near Garden City College,
   KR Puram, Bangalore 560049, India
   +91 80 4190 3551
 */

#ifndef _CB_WEBSOCKET_ENDPOINT_H
#define _CB_WEBSOCKET_ENDPOINT_H

#include <websocketpp/client.hpp>
#include <websocketpp/config/asio_client.hpp>

#include "CryptoCode/CryptoUtils/websocket_setting.hpp"
#include <CryptoCode/CryptoUtils/websocket_defines.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <cstdlib>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <unistd.h>
#include <websocketpp/common/memory.hpp>
#include <websocketpp/common/thread.hpp>
#include <unordered_map>

namespace CRYPTO {

class WebsocketCoinBaseEndpoint {
public:
  void on_message(websocketpp::connection_hdl, client::message_ptr msg);
  void on_close(client *c, websocketpp::connection_hdl hdl);
  void on_fail(client *c, websocketpp::connection_hdl hdl);
  void on_open(client *c, websocketpp::connection_hdl hdl);
  int connect(std::string exchange_);

  WebsocketCoinBaseEndpoint(int Id) : m_id(Id) {
    m_endpoint.clear_access_channels(websocketpp::log::alevel::all);
    m_endpoint.clear_error_channels(websocketpp::log::elevel::all);

    m_endpoint.init_asio();
    m_endpoint.start_perpetual();

    m_thread = websocketpp::lib::make_shared<websocketpp::lib::thread>(
        &client::run, &m_endpoint);
  }

  ~WebsocketCoinBaseEndpoint() {
    m_endpoint.stop_perpetual();

      if (get_status() != "Open") {
        // Only close open connections
        return;
      }

      std::cout << "> Closing connection " << get_id() << std::endl;

      websocketpp::lib::error_code ec;
      m_endpoint.close(hdl,
                       websocketpp::close::status::going_away, "", ec);
      if (ec) {
        std::cout << "> Error closing connection " << get_id()
                  << ": " << ec.message() << std::endl;
      }
    m_thread->join();
  }
  void close(int id, websocketpp::close::status::value code,
             std::string reason) {
    websocketpp::lib::error_code ec;

    m_endpoint.close(hdl, code, reason, ec);
    if (ec) {
      std::cout << "> Error initiating close: " << ec.message() << std::endl;
    }
  }

  void send(int id, std::string message) {
    websocketpp::lib::error_code ec;
    m_endpoint.send(hdl, message,
                    websocketpp::frame::opcode::text, ec);
    if (ec) {
      std::cout << "> Error sending message: " << ec.message() << std::endl;
      return;
    }
  }
  int get_id() const { return m_id; }

  std::string get_status() const { return m_status; }
private:

  websocketpp::client<websocketpp::config::asio_tls_client> m_endpoint;
  websocketpp::lib::shared_ptr<websocketpp::lib::thread> m_thread;
  websocketpp::connection_hdl hdl;
  std::unordered_map<std::string, long long> product_to_seq;
  boost::property_tree::ptree pt;
 int m_id;
  std::string m_status;
  std::string m_uri;
  std::string m_server;
  std::string m_error_reason;
 //  CRYPTO::CoinBaseDecoder  coinbasedecoder;

};
}
#endif // _CB_WEBSOCKET_ENDPOINT_H
