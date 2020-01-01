#include <memory>
#include <vector>

template <typename T>
struct TreeNode {
  TreeNode(T v): value_(v) {};
  std::vector<std::shared_ptr<TreeNode>> children_;
  T value_;
};
