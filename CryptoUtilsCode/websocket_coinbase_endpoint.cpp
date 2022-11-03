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

#include "CryptoCode/CryptoUtils/websocket_coinbase_endpoint.hpp"
#include <iostream>
#include <sstream>
#include <string>
#include <unistd.h>
#include <vector>
#include <unordered_map>

namespace CRYPTO {

context_ptr on_tls_init_cb(websocketpp::connection_hdl) {
  context_ptr ctx = websocketpp::lib::make_shared<boost::asio::ssl::context>(
      boost::asio::ssl::context::sslv23);

  try {
    ctx->set_options(boost::asio::ssl::context::default_workarounds |
                     boost::asio::ssl::context::no_sslv2 |
                     boost::asio::ssl::context::no_sslv3 |
                     boost::asio::ssl::context::single_dh_use);
  } catch (std::exception &e) {
    std::cout << e.what() << std::endl;
  }
  return ctx;
}

  int WebsocketCoinBaseEndpoint::connect(std::string exchange_) {
    websocketpp::lib::error_code ec;

    // Register the TLS handler with the endpoint. Note this must happen before
    // any calls to get_connection().
    std::vector<std::string> uri =
        CRYPTO::WebSocketSettings::GetUniqueInstance().getValue("Endpoint");
    m_endpoint.set_tls_init_handler(&on_tls_init_cb);
    if (uri.size() != 1) {
      std::cout << "Invalid Url Passed " << std::endl;
      exit(1);
    }
    client::connection_ptr con = m_endpoint.get_connection(uri[0], ec);

    if (ec) {
      std::cout << "> Connect initialization error: " << ec.message()
                << std::endl;
      return -1;
    }

    if (exchange_ == "COINBASE") {
      hdl = con->get_handle();

      con->set_open_handler(websocketpp::lib::bind(
          &WebsocketCoinBaseEndpoint::on_open, this, &m_endpoint,
          websocketpp::lib::placeholders::_1));
      con->set_fail_handler(websocketpp::lib::bind(
          &WebsocketCoinBaseEndpoint::on_fail, this, &m_endpoint,
          websocketpp::lib::placeholders::_1));
      con->set_close_handler(websocketpp::lib::bind(
          &WebsocketCoinBaseEndpoint::on_close, this, &m_endpoint,
          websocketpp::lib::placeholders::_1));
      con->set_message_handler(websocketpp::lib::bind(
          &WebsocketCoinBaseEndpoint::on_message, this,
          websocketpp::lib::placeholders::_1,
          websocketpp::lib::placeholders::_2));
      m_endpoint.connect(con);
      return 0;
    } else {
      std::cout << "Wrong Exchange " << std::endl;
      return -1;
    }
  }

void WebsocketCoinBaseEndpoint::on_message(websocketpp::connection_hdl, client::message_ptr msg) {
    //    std::cout <<"Open On_message: " << m_status << std::endl;
/*    if (msg->get_opcode() == websocketpp::frame::opcode::text) {
      std::cout << "Getting Payload opcode" << msg->get_payload()
                << std::endl; // current getting in this

    } else {
      std::cout << "Getting Payload hex "
                << websocketpp::utility::to_hex(msg->get_payload())
                << std::endl;
    }
*/
    std::stringstream ss(msg->get_payload());
    boost::property_tree::read_json(ss, pt);
    std::string type_ = pt.get<std::string>("type") ;
    if (type_ == "l2update") {
      std::cout << "Message Type Not Handled: " << type_ << std::endl;
    } else if (type_ == "received" || type_ == "open" || type_ == "done" ||
               type_ == "match" || type_ == "change" or type_ == "activate") {
        std::string product_id_ = pt.get<std::string>("product_id");
        long long seq_ = pt.get<long long>("sequence");
//      std::cout << product_id_ << " "  << seq_ << std::endl;
        if ( seq_ > product_to_seq[product_id_] ){
                std::cout << "Drop for " << product_id_  << " from: " << product_to_seq[product_id_] << " to Seq: "
                        << seq_ << " of DropSize: " << seq_ - product_to_seq[product_id_] << std::endl;
        } else if ( seq_ < product_to_seq[product_id_]){
              std::cout << "Msg Sequence already recieved for " << product_id_ << ": " << seq_ << " Expected: "
                      << product_to_seq[product_id_] << std::endl;
          }
        product_to_seq[product_id_] = seq_ + 1;
	if (seq_ % 6000 == 0){
		std::cout << "MM_COUNT " << product_id_ << " "  << seq_ << std::endl;
	}

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


 void WebsocketCoinBaseEndpoint::on_fail(client *c, websocketpp::connection_hdl hdl) { 
    m_status = "Failed"; 
    client::connection_ptr con = c->get_con_from_hdl(hdl); 
    m_server = con->get_response_header("Server"); 
    m_error_reason = con->get_ec().message(); 
    std::cout << "ClientStatus: " << m_status << " ServerStatus: " << m_server 
              << " Reason: " << m_error_reason << std::endl; 
  } 
 
 void WebsocketCoinBaseEndpoint::on_close(client *c, websocketpp::connection_hdl hdl) { 
    m_status = "Closed"; 
    client::connection_ptr con = c->get_con_from_hdl(hdl); 
    std::stringstream s; 
    s << "close code: " << con->get_remote_close_code() << " (" 
      << websocketpp::close::status::get_string(con->get_remote_close_code()) 
      << "), close reason: " << con->get_remote_close_reason(); 
    m_error_reason = s.str(); 

    std::cout << "ClientStatus: " << m_status << " ServerStatus: " << m_server 
              << " Reason: " << m_error_reason << std::endl; 
    connect("COINBASE");
    std::cout << "Reconnection Tried " << std::endl;
  } 
  void  WebsocketCoinBaseEndpoint::on_open(client *c, websocketpp::connection_hdl hdl) {
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
    m_endpoint.send(hdl, subscribe_, websocketpp::frame::opcode::text, ec);
    if (ec) {
      std::cout << "> Error sending message: " << ec.message() << std::endl;
      return;
    }

    client::connection_ptr con = c->get_con_from_hdl(hdl);
    m_server = con->get_response_header("Server");
    std::cout << "ClientStatus: " << m_status << " ServerStatus: " << m_server
              << std::endl;
  }


} // namespace CRYPTO
