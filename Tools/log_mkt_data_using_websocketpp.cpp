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

#include <cstdlib>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <unistd.h>
#include <websocketpp/client.hpp>
#include <websocketpp/common/memory.hpp>
#include <websocketpp/common/thread.hpp>
#include <websocketpp/config/asio_client.hpp>

#include "CryptoCode/CRYPTOMD/coinbase_mtbt_raw_handler.hpp"
#include "CryptoCode/CryptoUtils/websocket_mtbt_endpoint.hpp"
#include "CryptoCode/CryptoUtils/websocket_setting.hpp"
#include "dvccode/CDef/debug_logger.hpp"
#include "dvccode/CommonTradeUtils/date_time.hpp"

HFSAT::DebugLogger *global_dbglogger_;

void PrintUsage(const char *prg_name) {
  printf(" This is the Wocket Loggin daemon exec \n");
  printf(" Usage:%s <config_file> \n", prg_name);
}

int main(int argc, char **argv) {
  std::string input;
  //  WebsocketEndpoint endpoint;
  if (argc < 3) {
    PrintUsage(argv[0]);
    exit(0);
  }

  std::string config_file = argv[1];
  std::string exchange_ = argv[2];
  bool run_logger = false;
  if (argc > 3 && std::string(argv[3]) == "LOGGER") run_logger = true;

  CRYPTO::WebSocketSettings::SetUniqueInstance(config_file);
  CRYPTO::WebSocketSettings::GetUniqueInstance().ToString();

  HFSAT::DebugLogger dbglogger_(10240, 1);
  std::string logfilename = "/spare/local/logs/log_mtbt_crypto_writer_dbg" + std::string("_") + exchange_ +
                            std::string("_") + HFSAT::DateTime::GetCurrentIsoDateLocalAsString() + ".log";

  dbglogger_.OpenLogFile(logfilename.c_str(), std::ios::out | std::ios::app);
  global_dbglogger_ = &dbglogger_;

  dbglogger_ << "\n\nOpenDbglogger\n";
  dbglogger_ << "Running For Exchange_ " << exchange_ << "\n";
  dbglogger_.DumpCurrentBuffer();

  CRYPTO::CoinBaseRawMDHandler *coinbase_raw_handler_ =
      &(CRYPTO::CoinBaseRawMDHandler::GetUniqueInstance(dbglogger_, run_logger));
  CRYPTO::WebsocketMTBTEndpoint *endpoint;
  if (exchange_ == "COINBASE") {
    endpoint = new CRYPTO::WebsocketMTBTEndpoint(coinbase_raw_handler_, dbglogger_, exchange_, 1);
    int id = endpoint->connect();
    if (id != -1) {
      std::cout << "> Created connection with id " << id << std::endl;
    }
  } else {
    std::cout << "Wrong Exchange Passed... " << exchange_ << std::endl;
  }
  //            endpoint.close(id, close_code, reason);
  sleep(10000000);
  return 0;
}
