#include "NestPrinter.h"

#include <folly/Conv.h>

#include <deque>
#include <iostream>
#include <memory>
#include <stack>

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
        if (joints[idx] == kJoints[4]) {
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
  auto rr = std::make_shared<TreeNode<std::string>>("*");  // root of roots
  std::string tmp = "";
  int bracketCount = 0;
  std::stack<std::shared_ptr<TreeNode<std::string>>> storedRoots;
  std::shared_ptr<TreeNode<std::string>> cur = rr;
  State state = STATE0;
  for (auto c : input) {
    switch (state) {
      case STATE0:
        {
          switch (c) {
            case ' ': break;
            case '[':
              {
                bracketCount++;
                auto newNode = std::make_shared<TreeNode<std::string>>("[]");
                cur->children_.push_back(newNode);
                storedRoots.push(cur);
                cur = newNode;
                state = STATE1;
                break;
              }
            default:
              {
                std::cout << "Syntax error0" << std::endl;
                exit(1);
              }
          }
          break;
        }
      case STATE1:
        {
          switch (c) {
            case ' ': break;
            case '[':
              {
                bracketCount++;
                auto newNode = std::make_shared<TreeNode<std::string>>("[]");
                cur->children_.push_back(newNode);
                storedRoots.push(cur);
                cur = newNode;
                break;
              }
            case ']':
              {
                bracketCount--;
                cur = storedRoots.top();
                storedRoots.pop();
                if (bracketCount == 0) {
                  state = STATE0;
                } else {
                  state = STATE4;
                }
                break;
              }
            case ',':
              {
                std::cout << "Syntax error1" << std::endl;
                exit(1);
              }
            default:
              {
                tmp.push_back(c);
                state = STATE2;
                break;
              }
          }
          break;
        }
      case STATE2:
        {
          switch (c) {
            case ' ':
              {
                std::cout << "Syntax error2" << std::endl;
                exit(1);
              }
            case '[':
              {
                std::cout << "Syntax error3" << std::endl;
                exit(1);
              }
            case ',':
              {
                auto newNode = std::make_shared<TreeNode<std::string>>(tmp);
                tmp.clear();
                cur->children_.push_back(newNode);
                state = STATE3;
                break;
              }
            case ']':
              {
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
                break;
              }
            default:
              {
                tmp.push_back(c);
                break;
              }
          }
          break;
        }
      case STATE3:
        {
          switch (c) {
            case ' ': break;
            case ',':
              {
                std::cout << "Syntax error4" << std::endl;
                exit(1);
              }
            case ']':
              {
                std::cout << "Syntax error5" << std::endl;
                exit(1);
              }
            case '[':
              {
                bracketCount++;
                auto newNode = std::make_shared<TreeNode<std::string>>("[]");
                cur->children_.push_back(newNode);
                storedRoots.push(cur);
                cur = newNode;
                state = STATE1;
                break;
              }
            default:
              {
                tmp.push_back(c);
                state = STATE2;
                break;
              }
          }
          break;
        }
      case STATE4:
        {
          switch (c) {
            case ' ':
              {
                std::cout << "Syntax error6" << std::endl;
                exit(1);
              }
            case '[':
              {
                std::cout << "Syntax error7" << std::endl;
                exit(1);
              }
            case ',':
              {
                state = STATE3;
                break;
              }
            case ']':
              {
                bracketCount--;
                cur = storedRoots.top();
                storedRoots.pop();
                if (bracketCount == 0) {
                  state = STATE0;
                } else {
                  state = STATE4;
                }
                break;
              }
            default:
              {
                std::cout << "Syntax error8" << std::endl;
                exit(1);
              }
          }
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
  auto inputStr = std::string(argv[1]);
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
