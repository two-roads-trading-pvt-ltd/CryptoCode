/**
    \file CDef/websocket_setting.hpp

    \author: (c) Copyright Two Roads Technological Solutions Pvt Ltd 2011
     Address:
         Suite 217, Level 2, Prestige Omega,
         No 104, EPIP Zone, Whitefield,
         Bangalore - 560066
         India
         +91 80 4060 0717
 */

#ifndef BASE_CRYPTO_SETTINGS_H
#define BASE_CRYPTO_SETTINGS_H
#include "CDef/channels_config_reader.hpp"
#include <fstream>
#include <iostream>
#include <map>
#include <stdlib.h>
#include <string.h>
#include <string>

namespace CRYPTO {
class WebSocketSettings {
  WebSocketSettings(const std::string file);
  WebSocketSettings(WebSocketSettings const &disabled_copy_constructor);
  ~WebSocketSettings() { values.clear(); }

 public:
  static void SetUniqueInstance(const std::string file);
  static WebSocketSettings &GetUniqueInstance();

  bool has(std::string key) const;
  std::vector<std::string> getValue(std::string key) const;
  std::string GetFileName();
  std::string ToString();

 protected:
  std::map<std::string, std::vector<std::string>> values;
  std::string config_file_;
};
}  // namespace CRYPTO
#endif  // BASE_CRYPTO_SETTINGS_H
