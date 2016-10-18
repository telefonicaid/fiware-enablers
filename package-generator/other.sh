[ -z "$OS_USERNAME" ] && echo "Need variable OS_USERNAME" && exit 1;
[ -z "$OS_TENANT_ID" ] && echo "Need variable OS_TENANT_ID" && exit 1;
[ -z "$OS_PASSWORD" ] && echo "Need variable OS_PASSWORD" && exit 1;

python package-generator.py -u ${OS_USERNAME} -g False -t ${OS_TENANT_ID} -p ${OS_PASSWORD}
python migrate-templates.py -u ${OS_USERNAME} -t ${OS_TENANT_ID} -p ${OS_PASSWORD}
