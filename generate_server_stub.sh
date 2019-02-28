#!/usr/bin/env bash
#
# author: PFigs

set -o nounset
set -o errexit
set -o errtrace

trap 'echo "Aborting due to errexit on line $LINENO. Exit code: $?" >&2' ERR
#trap _finish EXIT


DEFAULT_IFS="${IFS}"
SAFER_IFS=$'\n\t'
IFS="${SAFER_IFS}"

_ME=$(basename "${0}")



function _defaults
{
    GENERATE_IN="docker"
    LANGUAGE_SELECT="py3"
    TARGET_LANGUAGE="-l python-flask"
    TARGET_LANGUAGE_FLAG="-D supportPython3=true"
    TARGET_LANGUAGE_OUTPUT="-o /local/out/python3"
}

function _print_help
{
  cat <<HEREDOC
Server stub generator

Generates server stub code based on the swagger api contract. The code
is generated based with swagger codegen cli.


Usage:
  ${_ME} [<arguments>]
  ${_ME} -h | --help
  ${_ME} --language python2 | python3 | py2 | py3

Options:
  -h --help   Show this screen
  --language  Specify server stub generation language (default: ${LANGUAGE_SELECT})
HEREDOC
}

function _parse
{
    # Gather commands
    while (( "${#}" ))
    do
        case "${1}" in
            --language)
            LANGUAGE_SELECT="$2"
            shift # past argument
            shift # past value
            ;;
            *|-*|--*=) # unsupported flags
            echo "Unknown ${1}"
            exit 1
            ;;
        esac
    done
}

function _generate_stub
{

    if [ "${LANGUAGE_SELECT}" == "py2" ] || [ "${LANGUAGE_SELECT}" == "python2" ]
    then

       TARGET_LANGUAGE="python-flask"
       TARGET_LANGUAGE_FLAG="supportPython2=true"
       TARGET_LANGUAGE_OUTPUT="/local/server_stub/python2"

    elif [ "${LANGUAGE_SELECT}" == "py3" ] || [ "${LANGUAGE_SELECT}" == "python3" ]
    then

       TARGET_LANGUAGE="python-flask"
       TARGET_LANGUAGE_FLAG="supportPython3=true"
       TARGET_LANGUAGE_OUTPUT="/local/server_stub/python3"
    fi

    echo "generation in ${GENERATE_IN} with ${TARGET_LANGUAGE} ${TARGET_LANGUAGE_FLAG} ${TARGET_LANGUAGE_OUTPUT}"

    if [ "${GENERATE_IN}" == "docker" ]
    then
        sudo docker run --rm \
               --user $(id -u):$(id -g) \
               -v $(pwd):/local \
               swaggerapi/swagger-codegen-cli generate \
               -i /local/docs/api_contract.yaml \
               -l ${TARGET_LANGUAGE} \
               -D ${TARGET_LANGUAGE_FLAG} \
               -o ${TARGET_LANGUAGE_OUTPUT}

    elif [[ "${GENERATE_IN}" == "native" ]]
    then
        echo "native support not available"

    else
        echo "genaration not support in ${GENERATE_IN}"
    fi
}

#docker run --rm -v ${PWD}:/local \
#swaggerapi/swagger-codegen-cli generate \
#-i /local/docs/api_contract.yaml \
#-l python-flask \
#-D supportPython2=true \
#-o /local/out/python

# main execution loop
_main()
{
    _defaults

    if [[ "${1:-}" =~ ^-h|--help$   ]]
    then
        _print_help
        exit 1
    fi

    _parse "$@"
    _generate_stub

    echo "done"
}

_main "$@"
