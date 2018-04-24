#!/bin/bash
for file in *.md docs/fr_FR/*.md; 
  do 
  echo $files
  if [ $file = "docs/fr_FR/index-template.md" ] || [ $file = "docs/fr_FR/index.md" ]
  then
    echo "skip "$file
  else
    echo "process "$file
    cat $file | aspell --personal=./tests/tools/.aspell.fr.pws --lang=fr --encoding=utf-8 list;
  fi
done 
