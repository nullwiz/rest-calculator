#!/bin/bash
# Run setupy.py bdist 
echo "\e[1;32mRunning setup.py bdist_wheel\e[0m"
python setup.py bdist_wheel
# Copy build/ and dist/ to the restcalculator/ folder
echo "\e[1;32mCopying build/ and dist/ to the restcalculator/ folder\e[0m"
cp -r build/ restcalculator/
cp -r dist/ restcalculator/
cp -r restcalculator.egg-info/ restcalculator/

echo "\e[1;32mRemoving build/ and dist/ from the root folder\e[0m"
# Remove build/, dist/ .egg-info/  from the root folder
rm -r build/ dist/ restcalculator.egg-info/
# Export variables in .env 
echo "\e[1;32mSourcing variables in local.env\e[0m"
while IFS= read -r line; do
    export "$line"
done < local.env

echo "FRONTEND_URL: $FRONTEND_URL"
echo "AWS_PGSQL_PATH: $AWS_PGSQL_PATH"