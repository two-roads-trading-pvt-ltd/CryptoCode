
#ifndef BASE_TCRYPTO_CHANNEL_READ_CONFIG_H
#define BASE_TCRYPTO_CHANNEL_READ_CONFIG_H

#include "dvccode/CommonDataStructures/perishable_string_tokenizer.hpp"
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace CryptoUtil {

bool ReadChannelConfig(
    std::ifstream &stream_config,
    std::map<std::string, std::vector<std::string>> &config_loaded);

};

#endif // BASE_TCRYPTO_CHANNEL_READ_CONFIG_H
