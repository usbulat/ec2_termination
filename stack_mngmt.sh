#!/bin/bash

SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 || exit ; pwd -P )"
NAME="ec2_termination"
STACK_NAME="${NAME//_}stack"
CF_FOLDER="cf"
MODULE_FOLDER="module"
TEMPLATE_FILE="${NAME}.yaml"
PARAMETERS_FILE="parameters.json"
PYTHON_FILE="${NAME}.py"
ZIP_FILE="${NAME}.zip"
LAMBDA_FUNCTION_NAME="${NAME}_lambda_function"

function test_python() {
    echo "Testing python file..."
    cd "${SCRIPT_PATH}" || exit 1
    pytest -v
    if [ $? -ne 0 ]; then
        echo "Testing python file failed!"
        exit 2
    else
        echo "Testing python file finished."
    fi
}

function create() {
    test_python

    echo "Stack creation starts..."
    aws cloudformation create-stack \
    --stack-name "${STACK_NAME}" \
    --template-body "file://${SCRIPT_PATH}/${CF_FOLDER}/${TEMPLATE_FILE}" \
    --parameters "file://${SCRIPT_PATH}/${CF_FOLDER}/${PARAMETERS_FILE}" \
    --capabilities CAPABILITY_NAMED_IAM
    if [ $? -ne 0 ]; then
        echo "Stack creation failed!"
        exit 3
    fi

    aws cloudformation wait stack-create-complete \
    --stack-name "${STACK_NAME}"
    if [ $? -ne 0 ]; then
        echo "Stack creation failed!"
        exit 4
    else
        echo "Stack creation finished."
    fi

    upload_python
}

function update() {
    test_python

    echo "Stack update starts..."
    aws cloudformation update-stack \
    --stack-name "${STACK_NAME}" \
    --template-body "file://${SCRIPT_PATH}/${CF_FOLDER}/${TEMPLATE_FILE}" \
    --parameters "file://${SCRIPT_PATH}/${CF_FOLDER}/${PARAMETERS_FILE}" \
    --capabilities CAPABILITY_NAMED_IAM
    if [ $? -ne 0 ]; then
        echo "Stack update failed!"
        exit 3
    fi

    aws cloudformation wait stack-update-complete \
    --stack-name "${STACK_NAME}"
    if [ $? -ne 0 ]; then
        echo "Stack update failed!"
        exit 4
    else
        echo "Stack update finished."
    fi

    upload_python
}

function upload_python() {
    echo "Compressing python file..."
    zip -j "${SCRIPT_PATH}/${MODULE_FOLDER}/${ZIP_FILE}" "${SCRIPT_PATH}/${MODULE_FOLDER}/${PYTHON_FILE}"
    if [ $? -ne 0 ]; then
        echo "Compressing python file failed!"
        exit 5
    else
        echo "Compressing python file finished."
    fi

    echo "Python script upload starts..."
    aws lambda update-function-code \
    --function-name "${LAMBDA_FUNCTION_NAME}" \
    --zip-file "fileb://${SCRIPT_PATH}/${MODULE_FOLDER}/${ZIP_FILE}"
    if [ $? -ne 0 ]; then
        echo "Python script upload failed!"
        exit 6
    else
        echo "Python script upload finished."
    fi

    rm -f "${SCRIPT_PATH}/${MODULE_FOLDER}/${ZIP_FILE}"
}

function delete() {
    echo "Stack deletion starts..."
    aws cloudformation delete-stack \
    --stack-name "${STACK_NAME}"
    if [ $? -ne 0 ]; then
        echo "Stack deletion failed!"
        exit 1
    fi

    aws cloudformation wait stack-delete-complete \
    --stack-name "${STACK_NAME}"
        if [ $? -ne 0 ]; then
        echo "Stack deletion failed!"
        exit 2
    else
        echo "Stack deletion finished."
    fi
}


case "$1" in
     create)
          create;;
     update)
          update;;
     test_python)
          test_python;;
     upload_python)
          upload_python;;
     delete)
          delete;;
     *)
          echo "Usage: $0 (create|update|upload_python|test_python|delete)"
          ;;
esac