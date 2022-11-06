
#include "CryptoCode/CDef/channels_config_reader.hpp"

namespace CryptoUtil {

bool ReadChannelConfig(std::ifstream &stream_config, std::map<std::string, std::vector<std::string>> &config_loaded) {
  if (!stream_config.good()) {
    printf("Failed to open streams.cfg\n");
    exit(0);
  }
  char buffer[1024];
  int MAX_LINE_SIZE = 1024;
  while (stream_config.good()) {
    stream_config.getline(buffer, MAX_LINE_SIZE);
    std::string line_buffer = buffer;
    // Comments
    if (line_buffer.find("#") != std::string::npos) continue;
    HFSAT::PerishableStringTokenizer pst(buffer, MAX_LINE_SIZE);
    std::vector<char const *> const &tokens = pst.GetTokens();
    if (tokens.size() != 3) continue;
    std::string key_ = tokens[0];
    std::string value_ = tokens[2];
    std::stringstream sstr(value_);
    std::vector<std::string> values_conf;
    while (sstr.good()) {
      std::string substr;
      getline(sstr, substr, ',');
      values_conf.push_back(substr);
    }
    config_loaded[key_] = values_conf;
  }
  return true;
}

};  // namespace CryptoUtil
