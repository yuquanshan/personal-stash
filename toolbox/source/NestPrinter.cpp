#include "NestPrinter.h"

#include <folly/Conv.h>
#include <gflags/gflags.h>
#include <glog/logging.h>

#include <deque>
#include <iostream>
#include <memory>
#include <stack>

DEFINE_string(filter_chars, "", "Characters to filter");
DEFINE_string(brackets, "[]", "A pair of bracket characters");

const std::string kJoints[] = {"─", "│", "┬", "├", "└"};
enum State {STATE0, STATE1, STATE2, STATE3, STATE4};

// TODO(yuquanshan): add explanation of printTree and parseForest.
template <typename T>
void printTree(
    const std::shared_ptr<TreeNode<T>>& root,
    std::deque<std::shared_ptr<TreeNode<T>>>& parents,
    std::deque<std::string>& joints) {
  if (root == nullptr) {
    return;
  }
  if (root->children_.size() > 0) {
    parents.push_back(root);
    joints.push_back(root->children_.size() == 1 ? kJoints[0] : kJoints[2]);
    for (int idx = 0; idx < root->children_.size(); ++idx) {
      printTree(root->children_[idx], parents, joints);
      joints.pop_back();
      joints.push_back(
          idx == root->children_.size() - 2 ? kJoints[4] : kJoints[3]);
    }
    parents.pop_back();
    joints.pop_back();
  } else {
    std::string line = "";
    for (int idx = 0; idx < parents.size(); ++idx) {
      if (joints[idx] == kJoints[1]
          || joints[idx] == kJoints[3]
          || joints[idx] == kJoints[4]
          || joints[idx] == " ") {
        for (int i = 0;
             i < folly::to<std::string>(parents[idx]->value_).size();
             ++i) {
          line = line + " ";
        }
        line = line + joints[idx];
        if (joints[idx] == kJoints[4] || joints[idx] == " ") {
          joints[idx] = " ";
        } else {
          joints[idx] = kJoints[1];
        }
      } else {
        line = line + folly::to<std::string>(parents[idx]->value_);
        line = line + joints[idx];
        if (joints[idx] == kJoints[0]) {
          joints[idx] = " ";
        } else {
          joints[idx] = kJoints[1];
        }
      }
    }
    std::cout << line << folly::to<std::string>(root->value_) << std::endl;
  }
}

auto parseForest(const std::string& input) {
  CHECK_EQ(FLAGS_brackets.size(), 2);
  const char lbracket = FLAGS_brackets[0];
  const char rbracket = FLAGS_brackets[1];
  auto rr = std::make_shared<TreeNode<std::string>>("*");  // root of roots
  std::string tmp = "";
  int bracketCount = 0;
  std::stack<std::shared_ptr<TreeNode<std::string>>> storedRoots;
  std::shared_ptr<TreeNode<std::string>> cur = rr;
  State state = STATE0;
  for (auto c : input) {
    if (FLAGS_filter_chars.find(c) != std::string::npos) {
      continue;
    }
    switch (state) {
      case STATE0:
        {
          if (c == ' ') {
          } else if (c == lbracket) {
            bracketCount++;
            auto newNode = std::make_shared<TreeNode<std::string>>(
                FLAGS_brackets);
            cur->children_.push_back(newNode);
            storedRoots.push(cur);
            cur = newNode;
            state = STATE1;
          } else {
            std::cout << "Syntax error0" << std::endl;
            exit(1);
          }
          break;
        }
      case STATE1:
        {
          if (c == ' ') {
          } else if (c == lbracket) {
            bracketCount++;
            auto newNode = std::make_shared<TreeNode<std::string>>("[]");
            cur->children_.push_back(newNode);
            storedRoots.push(cur);
            cur = newNode;
          } else if (c == rbracket) {
            bracketCount--;
            cur = storedRoots.top();
            storedRoots.pop();
            if (bracketCount == 0) {
              state = STATE0;
            } else {
              state = STATE4;
            }
          } else if (c == ',') {
            std::cout << "Syntax error1" << std::endl;
            exit(1);
          } else {
            tmp.push_back(c);
            state = STATE2;
          }
          break;
        }
      case STATE2:
        {
          if (c == ' ') {
            std::cout << "Syntax error2" << std::endl;
            exit(1);
          } else if (c == lbracket) {
            std::cout << "Syntax error3" << std::endl;
            exit(1);
          } else if (c == ',') {
            auto newNode = std::make_shared<TreeNode<std::string>>(tmp);
            tmp.clear();
            cur->children_.push_back(newNode);
            state = STATE3;
          } else if (c == rbracket){
            bracketCount--;
            auto newNode = std::make_shared<TreeNode<std::string>>(tmp);
            tmp.clear();
            cur->children_.push_back(newNode);
            cur = storedRoots.top();
            storedRoots.pop();
            if (bracketCount == 0) {
              state = STATE0;
            } else {
              state = STATE4;
            }
          } else {
            tmp.push_back(c);
          }
          break;
        }
      case STATE3:
        {
          if (c == ' ') {
          } else if (c == ',') {
            std::cout << "Syntax error4" << std::endl;
            exit(1);
          } else if (c == rbracket) {
            std::cout << "Syntax error5" << std::endl;
            exit(1);
          } else if (c == lbracket) {
            bracketCount++;
            auto newNode = std::make_shared<TreeNode<std::string>>("[]");
            cur->children_.push_back(newNode);
            storedRoots.push(cur);
            cur = newNode;
            state = STATE1;
          } else {
            tmp.push_back(c);
            state = STATE2;
          }
          break;
        }
      case STATE4:
        {
          if (c == ' ') {
            std::cout << "Syntax error6" << std::endl;
            exit(1);
          } else if (c == lbracket) {
            std::cout << "Syntax error7" << std::endl;
            exit(1);
          } else if (c == ',') {
            state = STATE3;
          } else if (c == rbracket) {
            bracketCount--;
            cur = storedRoots.top();
            storedRoots.pop();
            if (bracketCount == 0) {
              state = STATE0;
            } else {
              state = STATE4;
            }
          } else {
            std::cout << "Syntax error8" << std::endl;
            exit(1);
          }
          break;
        }
    }
  }
  if (bracketCount > 0) {
    std::cout << "Syntax error4" << std::endl;
    exit(1);
  }
  return rr->children_;
}

int main(int argc, char** argv) {
  if (argc <= 1) {
    std::cout << "Need argument." << std::endl;
    return 1;
  }
  auto inputStr = std::string(argv[argc - 1]);
  if (inputStr == "--help") {
    std::cout << "Print nested lists as a forest (with multiple trees)."
              << std::endl;
    std::cout << "Usage: ./nest_breaker <input_string>" << std::endl;
    return 0;
  }
  auto forest = parseForest(inputStr);
  auto parents = std::deque<std::shared_ptr<TreeNode<std::string>>>(0);
  auto joints =  std::deque<std::string>(0);
  for (auto tree: forest) {
    printTree(tree, parents, joints);
  }
  return 0;
}
