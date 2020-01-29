#!/bin/bash
for file in `find ./resources -name "*.py" ! -name "__init__.py"`;
  do
      echo "Check $file with pylint"
      python3 -m flake8 $file
  done
