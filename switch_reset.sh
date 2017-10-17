#!/bin/bash

FAIL=0

verizon_switches=(
	'10.9.31.60'
	'10.9.31.61'
	'10.9.31.62'
	'10.9.31.63'
	'10.9.31.64'
	'10.9.31.65'
	'10.9.31.66'
	'10.9.31.67'
	'10.9.31.68'
)

ansible_switches=(
	'10.110.0.160'
	'10.110.0.161'
	'10.110.0.162'
	'10.110.0.163'
	'10.110.0.164'
	'10.110.0.165'
)

gui_switches=(
	'10.110.0.81'
	'10.110.0.82'
	'10.110.0.83'
	'10.110.0.84'
	'10.110.0.85'
	'10.110.0.86'
)

PS3='Which setup do you want to reset? Please enter your choice: '
options=("Ansible" "GUI" "Verizon" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Ansible")
            switches=("${ansible_switches[@]}")
            break
            ;;
        "GUI")
            switches=("${gui_switches[@]}")
            break
            ;;
        "Verizon")
            switches=("${verizon_switches[@]}")
            break
            ;;
        "Quit")
	    exit 0
            ;;
        *) echo invalid option;;
    esac
done
read -p "Are you sure you want to reset $opt setup? [y|n] = " -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
	exit 0
fi

echo "==========================================="
echo "Please wait resetting all the switches..."
echo "==========================================="

for ip in ${switches[@]}; do
        echo "----------------------------------"
        echo "Switch : $ip"
        echo "----------------------------------"
        sshpass -p 'test123' ssh -q -oStrictHostKeyChecking=no network-admin@$ip -- --quiet role-modify name network-admin shell
        sshpass -p 'test123' ssh -q -oStrictHostKeyChecking=no network-admin@$ip -- --quiet role-modify name network-admin sudo
        echo "test123" | sshpass -p test123 ssh -q -oStrictHostKeyChecking=no network-admin@$ip -- --quiet "shell sudo -S -- sh -c 'nvos-reset.ksh -y -z -d && service svc-nvOSd restart'" &
done

for job in `jobs -p`
do
    wait $job || let "FAIL+=1"
done

echo "==========================================="
if [ "$FAIL" == "0" ]; then
	echo "All switches are successfully resetted :)"
else
	echo "Some issue. Please try manually !"
fi
echo "==========================================="

exit 0

