
// =====================================================================================
//
//       Filename:  coinbase_mtbt_raw_handler.hpp
//
//    Description:
//
//        Version:  1.0
//        Created:  09/16/2015 03:44:05 PM
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

#pragma once

#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <iostream>
#include <unordered_map>
#include <websocketpp/client.hpp>
#include <websocketpp/config/asio_client.hpp>

#include "CryptoCode/CDef/websocket_mtbt_listener.hpp"
#include "CryptoCode/CDef/websocket_setting.hpp"
#include "CryptoCode/CRYPTOMD/coinbase_mtbt_decoder.hpp"
#include "dvccode/CDef/debug_logger.hpp"

namespace CRYPTO {

class CoinBaseRawMDHandler : public CRYPTO::WebSocketMTBTListener {
  timeval tv_;
  std::string prev_date;
  std::unordered_map<std::string, long long> product_to_seq;
  boost::property_tree::ptree pt;
  HFSAT::DebugLogger& dbglogger_;
  CryptoCoinBaseDataDecoder& coinbase_tbt_data_decoder_;
  CoinBaseRawMDHandler(HFSAT::DebugLogger& dbglogger, bool run_logger = false)
      : dbglogger_(dbglogger),
        coinbase_tbt_data_decoder_(CryptoCoinBaseDataDecoder::GetUniqueInstance(dbglogger, run_logger)) {}
  ~CoinBaseRawMDHandler() {}

 public:
  static CoinBaseRawMDHandler& GetUniqueInstance(HFSAT::DebugLogger& dbglogger, bool run_logger = false) {
    static CoinBaseRawMDHandler unique_instance_(dbglogger, run_logger);
    return unique_instance_;
  }

  void connect() {}
  void on_message(const std::string msg) {
    gettimeofday(&tv_, NULL);
   // dbglogger_ << tv_.tv_sec << "." << tv_.tv_usec << "\n";
    std::stringstream ss(msg);
    boost::property_tree::read_json(ss, pt);
    std::string type_ = pt.get<std::string>("type", "Invalid");
    if (type_ == "l2update") {
      dbglogger_ << "Message Type Not Handled: " << type_ << "\n";
    } else if (type_ == "received" || type_ == "open" || type_ == "done" || type_ == "match" || type_ == "change" or
               type_ == "activate") {
      std::string product_id_ = pt.get<std::string>("product_id");
      long long seq_ = pt.get<long long>("sequence");
      if (seq_ > product_to_seq[product_id_]) {
        dbglogger_ << "Drop for " << product_id_ << " from: " << product_to_seq[product_id_] << " to Seq: " << seq_
                   << " of DropSize: " << seq_ - product_to_seq[product_id_] << "\n";
      } else if (seq_ < product_to_seq[product_id_]) {
        dbglogger_ << "Msg Sequence already recieved for " << product_id_ << ": " << seq_
                   << " Expected: " << product_to_seq[product_id_] << "\n";
      }

   //   if (seq_ % 6000 == 0) {
     //   dbglogger_ << "MM_COUNT " << product_id_ << " " << seq_ << "\n";
      //}
      //  if (prev_date != current_date) {
      // close current file
      // update_filepathmds
      // open new file;
      //  }
      coinbase_tbt_data_decoder_.decode_l2update_message(pt, tv_);
      product_to_seq[product_id_] = seq_ + 1;

    } else if (type_ == "ticker") {
      dbglogger_ << "Message Type Not Handled: " << type_ << "\n";
    } else if (type_ == "snapshot") {
      dbglogger_ << "Message Type Not Handled: " << type_ << "\n";
    } else if (type_ == "heartbeat") {
      dbglogger_ << "Message Type Not Handled: " << type_ << "\n";
    } else if (type_ == "subscriptions") {
      dbglogger_ << "Subscribed: " << msg << "\n";
    } else {
      dbglogger_ << "Message Type Not Handled: " << type_ << "\n";
    }
  }
  void on_fail() {}

  void on_close() {}

  void on_open() {}

  std::string get_connect_url() {
    std::vector<std::string> uri = CRYPTO::WebSocketSettings::GetUniqueInstance().getValue("CB_Endpoint");
    if (uri.size() != 1) {
      std::cout << "Invalid Url Passed " << std::endl;
      exit(1);
    }
    return uri[0];
  }

  std::string get_subsribe_str() {
    std::vector<std::string> product_ids = CRYPTO::WebSocketSettings::GetUniqueInstance().getValue("CB_product_ids");
    if (product_ids.size() == 0) {
      std::cerr << "Error No Products passed: " << std::endl;
      exit(-1);
    }
    std::vector<std::string> channels = CRYPTO::WebSocketSettings::GetUniqueInstance().getValue("CB_channels");
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
    return subscribe_;
  }
};
}  // namespace CRYPTO