
#pragma once

#include <boost/algorithm/string.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <lzo/lzo1z.h>
#include <lzo/lzoconf.h>

#include "dvccode/CDef/debug_logger.hpp"
#include "dvccode/CDef/defines.hpp"
#include "dvccode/CDef/stored_market_data_common_message_defines.hpp"
#include "dvccode/Utils/mds_logger.hpp"
#include "dvccode/Utils/rdtscp_timer.hpp"

namespace CRYPTO {

class CryptoCoinBaseDataDecoder {
  // For Logger Mode//

  MDSLogger<CRYPTO_MDS::CoinBaseMktStruct>* data_logger_thread_;
  CRYPTO_MDS::CoinBaseMktStruct coinbase_mtbt_data;
  HFSAT::DebugLogger& dbglogger_;
  struct tm tm {};
  char buf[9];
  int prev_date;

  CryptoCoinBaseDataDecoder(CryptoCoinBaseDataDecoder const& disabled_copy_constructor);
  CryptoCoinBaseDataDecoder(HFSAT::DebugLogger& dbglogger, bool run_logger_thread = false) : dbglogger_(dbglogger) {
    data_logger_thread_ = new MDSLogger<CRYPTO_MDS::CoinBaseMktStruct>("COINBASE");

    if (run_logger_thread == true) {
      dbglogger_ << "Running With Logger Thread for CoinBase "
                 << "\n";
      RunLoggerThread();
    } else {
      dbglogger_ << "No Logger in Logger Thread for CoinBase"
                 << "\n";
    }
    prev_date = stoi(HFSAT::DateTime::GetCurrentIsoDateLocalAsString());
  }

  ~CryptoCoinBaseDataDecoder() {
    if (data_logger_thread_ != nullptr) {
      data_logger_thread_->closeFiles();
      delete data_logger_thread_;
      data_logger_thread_ = nullptr;
    }
  }

 public:
  // To ensure there is only 1 decoder instance of the class in a program
  static CryptoCoinBaseDataDecoder& GetUniqueInstance(HFSAT::DebugLogger& dbglogger, bool run_logger_thread = false) {
    static CryptoCoinBaseDataDecoder unqiue_instance(dbglogger, run_logger_thread);
    return unqiue_instance;
  }

  CRYPTO_MDS::CB_MsgType getCoinbaseMsgStr(std::string msg_type) {
    if (msg_type == "received")
      return CRYPTO_MDS::CB_MsgType::received;
    else if (msg_type == "open")
      return CRYPTO_MDS::CB_MsgType::open;
    else if (msg_type == "done")
      return CRYPTO_MDS::CB_MsgType::done;
    else if (msg_type == "match")
      return CRYPTO_MDS::CB_MsgType::match;
    else if (msg_type == "change")
      return CRYPTO_MDS::CB_MsgType::change;
    else if (msg_type == "activate")
      return CRYPTO_MDS::CB_MsgType::activate;
    else
      return CRYPTO_MDS::CB_MsgType::kInvalid;
  }

  void decode_l2update_message(boost::property_tree::ptree pt, const timeval tv_) {
    std::string tmp_str = "";

    tmp_str = pt.get<std::string>("product_id", "Invalid");
    bzero(coinbase_mtbt_data.product_id, COINBASE_MKT_SYMBOL_LENGTH);
    strcpy(coinbase_mtbt_data.product_id, tmp_str.c_str());

    tmp_str = pt.get<std::string>("time", "0");
    strptime(tmp_str.c_str(), "%Y-%m-%dT%H:%M:%S.%fZ", &tm);
    strftime(buf, sizeof(buf), "%Y%m%d", &tm);
    int current_date = atoi(buf);
    if (current_date != prev_date) {
      prev_date = current_date;
      data_logger_thread_->SetDate(current_date);
    }

    coinbase_mtbt_data.source_time.tv_sec = mktime(&tm);
    coinbase_mtbt_data.source_time.tv_usec = stol(tmp_str.substr(tmp_str.find(".") + 1, tmp_str.size() - 1));

    coinbase_mtbt_data.local_time = tv_;
    CRYPTO_MDS::CB_MsgType msg_type = getCoinbaseMsgStr(pt.get<std::string>("type", "kInvalid"));
    coinbase_mtbt_data.msg_type = msg_type;
    coinbase_mtbt_data.sequence = pt.get<uint64_t>("sequence", 0);

    switch (msg_type) {
      case CRYPTO_MDS::CB_MsgType::received: {
        tmp_str = pt.get<std::string>("order_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_recieved_order.order_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_recieved_order.order_id, tmp_str.c_str());

        tmp_str = pt.get<std::string>("client_oid", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_recieved_order.client_oid, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_recieved_order.client_oid, tmp_str.c_str());

        coinbase_mtbt_data.data.coinbase_mkt_recieved_order.size = pt.get<double>("size", 0);
        coinbase_mtbt_data.data.coinbase_mkt_recieved_order.price = pt.get<double>("price", 0);
        coinbase_mtbt_data.data.coinbase_mkt_recieved_order.funds = pt.get<double>("funds", 0);
        if (boost::algorithm::to_lower_copy(pt.get<std::string>("side", "sell")) == "buy")
          coinbase_mtbt_data.data.coinbase_mkt_recieved_order.buysell = HFSAT::kTradeTypeBuy;
        else
          coinbase_mtbt_data.data.coinbase_mkt_recieved_order.buysell = HFSAT::kTradeTypeSell;
        if (boost::algorithm::to_lower_copy(pt.get<std::string>("order_type", "market")) == "limit")
          coinbase_mtbt_data.data.coinbase_mkt_recieved_order.order_type = 'L';
        else
          coinbase_mtbt_data.data.coinbase_mkt_recieved_order.order_type = 'M';
      } break;
      case CRYPTO_MDS::CB_MsgType::open: {
        tmp_str = pt.get<std::string>("order_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_open_order.order_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_open_order.order_id, tmp_str.c_str());
        coinbase_mtbt_data.data.coinbase_mkt_open_order.price = pt.get<double>("price", 0);
        coinbase_mtbt_data.data.coinbase_mkt_open_order.remaining_size = pt.get<double>("remaining_size", 0);
        if (boost::algorithm::to_lower_copy(pt.get<std::string>("side", "sell")) == "buy")
          coinbase_mtbt_data.data.coinbase_mkt_open_order.buysell = HFSAT::kTradeTypeBuy;
        else
          coinbase_mtbt_data.data.coinbase_mkt_open_order.buysell = HFSAT::kTradeTypeSell;
      } break;
      case CRYPTO_MDS::CB_MsgType::done: {
        // There are no more messages for an order_id after a done message.
        /* Cancel Order Reason only for authencicated users
            101:Time In Force
            102:Self Trade Prevention
            103:Admin
            104:Price Bound Order Protection
            105:Insufficient Funds
            106:Insufficient Liquidity
            107:Broker
        */

        tmp_str = pt.get<std::string>("order_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_done_order.order_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_done_order.order_id, tmp_str.c_str());

        coinbase_mtbt_data.data.coinbase_mkt_done_order.price = pt.get<double>("price", 0);
        coinbase_mtbt_data.data.coinbase_mkt_done_order.remaining_size = pt.get<double>("remaining_size", 0);
        coinbase_mtbt_data.data.coinbase_mkt_done_order.cancel_reason = pt.get<int>("cancel_reason", 0);

        if (boost::algorithm::to_lower_copy(pt.get<std::string>("reason", "Cancel")) == "Filled")
          coinbase_mtbt_data.data.coinbase_mkt_done_order.reason = 'F';
        else
          coinbase_mtbt_data.data.coinbase_mkt_done_order.reason = 'C';
        if (boost::algorithm::to_lower_copy(pt.get<std::string>("side", "sell")) == "buy")
          coinbase_mtbt_data.data.coinbase_mkt_done_order.buysell = HFSAT::kTradeTypeBuy;
        else
          coinbase_mtbt_data.data.coinbase_mkt_done_order.buysell = HFSAT::kTradeTypeSell;

      } break;
      case CRYPTO_MDS::CB_MsgType::match: {
        tmp_str = pt.get<std::string>("maker_order_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_match_order.maker_order_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_match_order.maker_order_id, tmp_str.c_str());

        tmp_str = pt.get<std::string>("taker_order_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_match_order.taker_order_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_match_order.taker_order_id, tmp_str.c_str());

        coinbase_mtbt_data.data.coinbase_mkt_match_order.trade_id = pt.get<uint64_t>("trade_id", 0);

        coinbase_mtbt_data.data.coinbase_mkt_match_order.size = pt.get<double>("size", 0);
        coinbase_mtbt_data.data.coinbase_mkt_match_order.price = pt.get<double>("price", 0);
        if (boost::algorithm::to_lower_copy(pt.get<std::string>("side", "sell")) == "buy")
          coinbase_mtbt_data.data.coinbase_mkt_match_order.buysell = HFSAT::kTradeTypeBuy;
        else
          coinbase_mtbt_data.data.coinbase_mkt_match_order.buysell = HFSAT::kTradeTypeSell;
      } break;
      case CRYPTO_MDS::CB_MsgType::change: {
        tmp_str = pt.get<std::string>("order_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_change_order.order_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_change_order.order_id, tmp_str.c_str());

        coinbase_mtbt_data.data.coinbase_mkt_change_order.old_size = pt.get<double>("old_size", 0);
        coinbase_mtbt_data.data.coinbase_mkt_change_order.new_size = pt.get<double>("new_size", 0);
        coinbase_mtbt_data.data.coinbase_mkt_change_order.old_price = pt.get<double>("old_price", 0);
        coinbase_mtbt_data.data.coinbase_mkt_change_order.new_price = pt.get<double>("new_price", 0);
        if (boost::algorithm::to_lower_copy(pt.get<std::string>("side", "sell")) == "buy")
          coinbase_mtbt_data.data.coinbase_mkt_change_order.buysell = HFSAT::kTradeTypeBuy;
        else
          coinbase_mtbt_data.data.coinbase_mkt_change_order.buysell = HFSAT::kTradeTypeSell;
      } break;
      case CRYPTO_MDS::CB_MsgType::activate: {
        tmp_str = pt.get<std::string>("profile_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_active_order.profile_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_active_order.profile_id, tmp_str.c_str());

        tmp_str = pt.get<std::string>("order_id", "Invalid");
        bzero(coinbase_mtbt_data.data.coinbase_mkt_active_order.order_id, COINBASE_ORDER_ID_SIZE);
        strcpy(coinbase_mtbt_data.data.coinbase_mkt_active_order.order_id, tmp_str.c_str());

        coinbase_mtbt_data.data.coinbase_mkt_active_order.stop_price = pt.get<double>("stop_price", 0);
        coinbase_mtbt_data.data.coinbase_mkt_active_order.size = pt.get<double>("size", 0);
        coinbase_mtbt_data.data.coinbase_mkt_active_order.funds = pt.get<double>("funds", 0);
        coinbase_mtbt_data.data.coinbase_mkt_active_order.user_id = pt.get<uint64_t>("user_id", 0);

        if (boost::algorithm::to_lower_copy(pt.get<std::string>("side", "sell")) == "buy")
          coinbase_mtbt_data.data.coinbase_mkt_active_order.buysell = HFSAT::kTradeTypeBuy;
        else
          coinbase_mtbt_data.data.coinbase_mkt_active_order.buysell = HFSAT::kTradeTypeSell;
        if (boost::algorithm::to_lower_copy(pt.get<std::string>("stop_type", "Invalid")) == "entry")
          coinbase_mtbt_data.data.coinbase_mkt_active_order.stop_type = 'E';  // Entry
        else
          coinbase_mtbt_data.data.coinbase_mkt_active_order.stop_type = 'I';  // Invalid
        coinbase_mtbt_data.data.coinbase_mkt_active_order.private_ = pt.get<bool>("private", false);
      } break;
      default: {
        dbglogger_ << "L2UPDATE NOT_IMPLEMENTED_FOR_THIS_EVENT : " << pt.get<std::string>("type", "kInvalid") << "\n";
      } break;
    }
    // std::cout << coinbase_mtbt_data.ToString() << std::endl;

    Log();
  };
  void Log() { data_logger_thread_->log(coinbase_mtbt_data); }
  void RunLoggerThread() { data_logger_thread_->run(); }
};
}  // namespace CRYPTO
