#include <folly/Conv.h>
#include <folly/String.h>

#include <algorithm>
#include <deque>
#include <iostream>
#include <string>
#include <vector>

/**
 * Divide a decimal num string with a number n.
 * @param[out] dividend dividend, to replaced with the quotient in the end
 * @param[in] n
 * @return the remainder
 */
template <typename T>
T decimalStringDiv(std::string& dividend, T n) {
  std::vector<T> v;
  uint32_t pass = 0;
  for (auto& i : dividend) {
    if (i == '\0') {
      continue;
    }
    if (i < 48 || i > 57) {
      std::cout << "Bad input " << i << " in " << dividend;
      exit(1);
    }
    uint32_t num = pass * 10 + (i - 48);
    v.push_back(num / n);
    pass = num % n;
  }
  if (std::all_of(v.cbegin(), v.cend(), [](int i){ return i == 0; })) {
    dividend = "";
  } else {
    dividend = folly::join('\0', v);
  }
  return pass;
}

int main(int argc, char** argv) {
  if (argc <= 1) {
    std::cout << "Need argument." << std::endl;
    return 1;
  }
  if (std::string(argv[1]) == "--help") {
    std::cout << "Print the binary form of a decimal number, count how many "
                 "bits required."
              << std::endl;
    std::cout << "Usage: ./count_bits <decimal_num>" << std::endl;
    return 0;
  }

  auto num = std::string(argv[1]);

  std::deque<uint32_t> s;
  while (num.size() > 0) {
    s.push_front(decimalStringDiv(num, (uint32_t)2));
  }
  std::cout << folly::join('\0', s) << std::endl;
  std::cout << "Num of bit(s) required: " << s.size() << std::endl;
  return 0;
}
