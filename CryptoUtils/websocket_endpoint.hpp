/**
   \file websocket_enpoint.hpp

   \author: (c) Copyright Two Roads Technological Solutions Pvt Ltd 2011
   Address:
   Suite No 353, Evoma, #14, Bhattarhalli,
   Old Madras Road, Near Garden City College,
   KR Puram, Bangalore 560049, India
   +91 80 4190 3551
 */

#ifndef _WEBSOCKET_ENDPOINT_H
#define _WEBSOCKET_ENDPOINT_H

#include <websocketpp/client.hpp>
#include <websocketpp/config/asio_client.hpp>

#include "CryptoCode/CDef/websocket_coinbase_endpoint.hpp"
#include "CryptoCode/CDef/websocket_setting.hpp"
#include "CryptoCode/CryptoUtils/websocket_coinbase_connection_data.hpp"
#include "CryptoCode/CryptoUtils/websocket_defines.hpp"
#include <cstdlib>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <unistd.h>
#include <websocketpp/common/memory.hpp>
#include <websocketpp/common/thread.hpp>

class WebsocketEndpoint {
 public:
  WebsocketEndpoint() : m_next_id(0) {
    m_endpoint.clear_access_channels(websocketpp::log::alevel::all);
    m_endpoint.clear_error_channels(websocketpp::log::elevel::all);

    m_endpoint.init_asio();
    m_endpoint.start_perpetual();

    m_thread = websocketpp::lib::make_shared<websocketpp::lib::thread>(&client::run, &m_endpoint);
  }

  ~WebsocketEndpoint() {
    m_endpoint.stop_perpetual();

    for (con_list::const_iterator it = m_connection_list.begin(); it != m_connection_list.end(); ++it) {
      if (it->second->get_status() != "Open") {
        // Only close open connections
        continue;
      }

      std::cout << "> Closing connection " << it->second->get_id() << std::endl;

      websocketpp::lib::error_code ec;
      m_endpoint.close(it->second->get_hdl(), websocketpp::close::status::going_away, "", ec);
      if (ec) {
        std::cout << "> Error closing connection " << it->second->get_id() << ": " << ec.message() << std::endl;
      }
    }

    m_thread->join();
  }

  int connect(std::string exchange_) {
    websocketpp::lib::error_code ec;

    // Register the TLS handler with the endpoint. Note this must happen before
    // any calls to get_connection().
    std::vector<std::string> uri = CRYPTO::WebSocketSettings::GetUniqueInstance().getValue("CB_Endpoint");
    m_endpoint.set_tls_init_handler(&on_tls_init);
    if (uri.size() != 1) {
      std::cout << "Invalid Url Passed " << std::endl;
      exit(1);
    }
    client::connection_ptr con = m_endpoint.get_connection(uri[0], ec);

    if (ec) {
      std::cout << "> Connect initialization error: " << ec.message() << std::endl;
      return -1;
    }

    int new_id = m_next_id++;
    if (exchange_ == "COINBASE") {
      ConnectionCoinBasedata::ptr metadata_ptr =
          websocketpp::lib::make_shared<ConnectionCoinBasedata>(new_id, con->get_handle(), uri[0], &m_endpoint);
      m_connection_list[new_id] = metadata_ptr;

      con->set_open_handler(websocketpp::lib::bind(&ConnectionCoinBasedata::on_open, metadata_ptr, &m_endpoint,
                                                   websocketpp::lib::placeholders::_1));
      con->set_fail_handler(websocketpp::lib::bind(&ConnectionCoinBasedata::on_fail, metadata_ptr, &m_endpoint,
                                                   websocketpp::lib::placeholders::_1));
      con->set_close_handler(websocketpp::lib::bind(&ConnectionCoinBasedata::on_close, metadata_ptr, &m_endpoint,
                                                    websocketpp::lib::placeholders::_1));
      con->set_message_handler(websocketpp::lib::bind(&ConnectionCoinBasedata::on_message, metadata_ptr,
                                                      websocketpp::lib::placeholders::_1,
                                                      websocketpp::lib::placeholders::_2));
      m_endpoint.connect(con);
      return new_id;
    } else {
      std::cout << "Wrong Exchange " << std::endl;
    }
  }

  void close(int id, websocketpp::close::status::value code, std::string reason) {
    websocketpp::lib::error_code ec;

    con_list::iterator metadata_it = m_connection_list.find(id);
    if (metadata_it == m_connection_list.end()) {
      std::cout << "> No connection found with id " << id << std::endl;
      return;
    }

    m_endpoint.close(metadata_it->second->get_hdl(), code, reason, ec);
    if (ec) {
      std::cout << "> Error initiating close: " << ec.message() << std::endl;
    }
  }

  void send(int id, std::string message) {
    websocketpp::lib::error_code ec;
    con_list::iterator metadata_it = m_connection_list.find(id);
    if (metadata_it == m_connection_list.end()) {
      std::cout << "> No connection found with id " << id << std::endl;
      return;
    }

    m_endpoint.send(metadata_it->second->get_hdl(), message, websocketpp::frame::opcode::text, ec);
    if (ec) {
      std::cout << "> Error sending message: " << ec.message() << std::endl;
      return;
    }

    metadata_it->second->record_sent_message(message);
  }

  ConnectionCoinBasedata::ptr get_metadata(int id) const {
    con_list::const_iterator metadata_it = m_connection_list.find(id);
    if (metadata_it == m_connection_list.end()) {
      return ConnectionCoinBasedata::ptr();
    } else {
      return metadata_it->second;
    }
  }

 private:
  websocketpp::client<websocketpp::config::asio_tls_client> m_endpoint;
  typedef std::map<int, ConnectionCoinBasedata::ptr> con_list;

  websocketpp::lib::shared_ptr<websocketpp::lib::thread> m_thread;

  con_list m_connection_list;
  int m_next_id;
};

#endif  // _WEBSOCKET_ENDPOINT_H
