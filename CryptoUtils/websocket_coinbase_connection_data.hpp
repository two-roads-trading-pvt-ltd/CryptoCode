// =====================================================================================
//
//       Filename:  ws_using_websocketpp.cpp
//
//    Description:
//
//        Version:  1.0
//        Created:  09/12/2022 04:50:02 AM
//       Revision:  none
//       Compiler:  g++
//
//         Author:  (c) Copyright Two Roads Technological Solutions Pvt Ltd 2011
//
//        Address:  Suite No 162, Evoma, #14, Bhattarhalli,
//                  Old Madras Road, Near Garden City College,
//                  KR Puram, Bangalore 560049, India
//          Phone:  +91 80 4190 3551
//
// =====================================================================================
/*
 * Copyright (c) 2014, Peter Thorson. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the WebSocket++ Project nor the
 *       names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL PETER THORSON BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// **NOTE:** This file is a snapshot of the WebSocket++ utility client tutorial.
// Additional related material can be found in the tutorials/utility_client
// directory of the WebSocket++ repository.

#include <websocketpp/client.hpp>
#include <websocketpp/config/asio_client.hpp>

#include "CryptoCode/CryptoUtils/websocket_setting.hpp"
#include <boost/property_tree/ptree.hpp>
#include <CryptoCode/Utils/websocket_defines.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <websocketpp/common/memory.hpp>
#include <websocketpp/common/thread.hpp>

#include <cstdlib>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <unistd.h>
#include <unordered_map>

class ConnectionCoinBasedata {
public:
  typedef websocketpp::lib::shared_ptr<ConnectionCoinBasedata> ptr;

  ConnectionCoinBasedata(
      int id, websocketpp::connection_hdl hdl, std::string uri,
      websocketpp::client<websocketpp::config::asio_tls_client> *m_endpoint_)
      : m_id(id), m_hdl(hdl), m_status("Connecting"), m_uri(uri),
        m_endpoint(m_endpoint_), m_server("N/A") {}

  void on_open(client *c, websocketpp::connection_hdl hdl) {
    m_status = "Open";
    websocketpp::lib::error_code ec;
    std::vector<std::string> product_ids =
        CRYPTO::WebSocketSettings::GetUniqueInstance().getValue("product_ids");
    if (product_ids.size() == 0) {
      std::cerr << "Error No Products passed: " << std::endl;
      exit(-1);
    }
    std::vector<std::string> channels =
        CRYPTO::WebSocketSettings::GetUniqueInstance().getValue("channels");
    if (channels.size() == 0) {
      std::cerr << "Error No Products passed: " << std::endl;
      exit(-1);
    }

    std::string subscribe_ = "{ \"type\": \"subscribe\", \"product_ids\": [ \"";
    for (unsigned int it = 0; it < product_ids.size(); it++) {
      if (it == product_ids.size() - 1) {
        subscribe_ += product_ids[it];
      } else {
        subscribe_ += product_ids[it] + "\", \"";
      }
    }
    subscribe_ += "\" ], \"channels\": [ \"";
    for (unsigned int it = 0; it < channels.size(); it++) {
      if (it == channels.size() - 1) {
        subscribe_ += channels[it];
      } else {
        subscribe_ += channels[it] + "\", \"";
      }
    }

    subscribe_ += "\" ] }";

    std::cout << "Subscribe Messge to send: " << subscribe_ << std::endl;
    m_endpoint->send(hdl, subscribe_, websocketpp::frame::opcode::text, ec);
    if (ec) {
      std::cout << "> Error sending message: " << ec.message() << std::endl;
      return;
    }

    client::connection_ptr con = c->get_con_from_hdl(hdl);
    m_server = con->get_response_header("Server");
    std::cout << "ClientStatus: " << m_status << " ServerStatus: " << m_server
              << std::endl;
  }

  void on_fail(client *c, websocketpp::connection_hdl hdl) {
    m_status = "Failed";
    client::connection_ptr con = c->get_con_from_hdl(hdl);
    m_server = con->get_response_header("Server");
    m_error_reason = con->get_ec().message();
    std::cout << "ClientStatus: " << m_status << " ServerStatus: " << m_server
              << " Reason: " << m_error_reason << std::endl;
  }

  void on_close(client *c, websocketpp::connection_hdl hdl) {
    m_status = "Closed";
    client::connection_ptr con = c->get_con_from_hdl(hdl);
    std::stringstream s;
    s << "close code: " << con->get_remote_close_code() << " ("
      << websocketpp::close::status::get_string(con->get_remote_close_code())
      << "), close reason: " << con->get_remote_close_reason();
    m_error_reason = s.str();
    std::cout << "ClientStatus: " << m_status << " ServerStatus: " << m_server
              << " Reason: " << m_error_reason << std::endl;
  }

  void on_message(websocketpp::connection_hdl, client::message_ptr msg) {
    //	  std::cout <<"Open On_message: " << m_status << std::endl;
    if (msg->get_opcode() == websocketpp::frame::opcode::text) {
      m_messages.push_back("<< " + msg->get_payload());
      std::cout << "Getting Payload opcode" << msg->get_payload()
                << std::endl; // current getting in this

    } else {
      m_messages.push_back("<< " +
                           websocketpp::utility::to_hex(msg->get_payload()));
      std::cout << "Getting Payload hex "
                << websocketpp::utility::to_hex(msg->get_payload())
                << std::endl;
    }

    std::stringstream ss(msg->get_payload());
    boost::property_tree::read_json(ss, pt);
    std::string type_ = pt.get<std::string>("type") ;
    if (type_ == "l2update") {
      std::cout << "Message Type Not Handled: " << type_ << std::endl;
    } else if (type_ == "received" || type_ == "open" || type_ == "done" ||
               type_ == "match" || type_ == "change" or type_ == "activate") {
	std::string product_id_ = pt.get<std::string>("product_id");
	long long seq_ = pt.get<long long>("sequence");
//	std::cout << product_id_ << " "  << seq_ << std::endl;
	if ( seq_ > product_to_seq[product_id_] ){
		std::cout << "Drop for " << product_id_  << " of: " << product_to_seq[product_id_] << " from Seq: " 
			<< seq_ << " of Size: " << seq_ - product_to_seq[product_id_] << std::endl;
	} else if ( seq_ < product_to_seq[product_id_]){
              std::cout << "Msg Sequence already recieved for " << product_id_ << ": " << seq_ << " Expected: "
		      << product_to_seq[product_id_] << std::endl;
          }
	product_to_seq[product_id_] = seq_ + 1;

    } else if (type_ == "ticker") {
      std::cout << "Message Type Not Handled: " << type_ << std::endl;
    } else if (type_ == "snapshot") {
      std::cout << "Message Type Not Handled: " << type_ << std::endl;
    } else if (type_ == "heartbeat") {
      std::cout << "Message Type Not Handled: " << type_ << std::endl;
    } else if (type_ == "subscriptions") {
      std::cout << "Subscribed: " << msg->get_payload() << std::endl;
    } else {
      std::cout << "Message Type Not Handled: " << type_ << std::endl;
    }
  }

  websocketpp::connection_hdl get_hdl() const { return m_hdl; }

  int get_id() const { return m_id; }

  std::string get_status() const { return m_status; }

  void record_sent_message(std::string message) {
    m_messages.push_back(">> " + message);
  }
  friend std::ostream &operator<<(std::ostream &out,
                                  ConnectionCoinBasedata const &data);

private:
  int m_id;
  websocketpp::connection_hdl m_hdl;
  std::string m_status;
  std::string m_uri;
  websocketpp::client<websocketpp::config::asio_tls_client> *m_endpoint;
  std::string m_server;
  std::string m_error_reason;
  std::vector<std::string> m_messages;
  std::unordered_map<std::string, long long> product_to_seq;
  boost::property_tree::ptree pt;
  //  CRYPTO::CoinBaseDecoder  coinbasedecoder;
};

std::ostream &operator<<(std::ostream &out,
                         ConnectionCoinBasedata const &data) {
  out << "> URI: " << data.m_uri << "\n"
      << "> Status: " << data.m_status << "\n"
      << "> Remote Server: "
      << (data.m_server.empty() ? "None Specified" : data.m_server) << "\n"
      << "> Error/close reason: "
      << (data.m_error_reason.empty() ? "N/A" : data.m_error_reason) << "\n";
  out << "> Messages Processed: (" << data.m_messages.size() << ") \n";

  std::vector<std::string>::const_iterator it;
  for (it = data.m_messages.begin(); it != data.m_messages.end(); ++it) {
    out << *it << "\n";
  }

  return out;
}
