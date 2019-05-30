#include <folly/Conv.h>
#include <folly/String.h>

#include <deque>
#include <iostream>
#include <string>
#include <vector>

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

  long num = folly::to<long>(std::string(argv[1]));
  if (num == 0) {
    std::cout << "0" << std::endl;
    std::cout << "Num of bit(s) required: 1" << std::endl;
    return 0;
  }

  std::deque<bool> s;
  while (num != 0) {
    s.push_front(num % 2);
    num = num / 2;
  }
  std::cout << folly::join('\0', s) << std::endl;
  std::cout << "Num of bit(s) required: " << s.size() << std::endl;
  return 0;
}
