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

#include "CryptoCode/CryptoUtils/websocket_setting.hpp"
#include <iostream>
#include <sstream>
#include <string>
#include <unistd.h>
#include <vector>

namespace CRYPTO {
WebSocketSettings *unique_instance_ = nullptr;
WebSocketSettings::WebSocketSettings(const std::string file)
    : config_file_(file) {
  values.clear();
  /// read key value pairs of settings from file

  std::ifstream stream_config;
  stream_config.open(config_file_.c_str(), std::ifstream::in);
  std::cout << "Reading Config File: " << config_file_ << std::endl;
  if (!CryptoUtil::ReadChannelConfig(stream_config, values)) {
    std::cout << "Failed to parse config file : " << config_file_ << std::endl;
    exit(1);
  }
  stream_config.close();
}

void WebSocketSettings::SetUniqueInstance(const std::string file) {
  if (unique_instance_ == nullptr) {
    unique_instance_ = new WebSocketSettings(file);
  }
}

WebSocketSettings &WebSocketSettings::GetUniqueInstance() {
  if (unique_instance_ == nullptr) {
    std::cerr << "SetUniqueInstance() not called for WebSocketSettings before "
                 "calling GetUniqueInstance() \n";
    exit(-1);
  }
  return *unique_instance_;
}

bool WebSocketSettings::has(std::string key) const {
  return (values.find(key) != values.end());
}

std::vector<std::string> WebSocketSettings::getValue(std::string key) const {
  auto v = values.find(key);
  if (v == values.end()) {
    std::cout << "Value For Key " << key << "  Does exist Exiting... "
              << std::endl;
    exit(-1);
  } else {
    v->second;
  }
  return v->second;
}

std::string WebSocketSettings::GetFileName() { return config_file_; }

std::string WebSocketSettings::ToString() {
  std::ostringstream t_temp_oss;
  t_temp_oss << "===================== ORS Config File =====================\n";

  for (auto &itr : values) {
    std::cout << itr.first << "->";
    for (auto value : itr.second)
      std::cout << value;
    std::cout << "\n";
  }

  t_temp_oss << "===========================================================\n";

  return t_temp_oss.str();
}
} // namespace CRYPTO
