#include <iostream>
using namespace std;
int main() 
{
% if say_hello:
  cout << "Hello, ${ planet }!";
% else:
  cout << "Goodbye!";
% endif
  return 0;
}
