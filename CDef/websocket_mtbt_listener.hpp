
// =====================================================================================
//
//       Filename:  websocket_mtbt_listener.hpp
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

#include <netinet/tcp.h>
#include <stdbool.h>
#include <stdio.h>
#include <sys/time.h>
#include <unistd.h>

#include <sstream>
#include <vector>
#include <websocketpp/client.hpp>
#include <websocketpp/common/memory.hpp>
#include <websocketpp/common/thread.hpp>
#include <websocketpp/config/asio_client.hpp>

#include "CryptoCode/CryptoUtils/websocket_defines.hpp"
#include "dvccode/CDef/debug_logger.hpp"
namespace CRYPTO {

class WebSocketMTBTListener {
   public:
    virtual ~WebSocketMTBTListener() {}
    virtual void connect() = 0;
    virtual void on_message(const std::string msg) = 0;
    virtual void on_fail() = 0;
    virtual void on_close() = 0;
    virtual void on_open() = 0;
    virtual std::string get_connect_url() = 0;
    virtual std::string get_subsribe_str() = 0;
};
}  // namespace CRYPTO