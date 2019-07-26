from __future__ import print_function
import subprocess
import argparse
import errno
import time
import sys

ignore_err_list = [errno.EEXIST]

##################
# ARGUMENT PARSING
##################

parser = argparse.ArgumentParser(description='Toggle vRouter NICs')
parser.add_argument(
    '-v', '--vrouter',
    help='vrouter name of which nics will be toggled',
    required=True
)
parser.add_argument(
    '-a', '--action',
    help='disable|enable',
    required=True
)
parser.add_argument(
    '--show-only',
    help='will show commands it will run',
    action='store_true',
    required=False
)
args = vars(parser.parse_args())

show_only = args["show_only"]
g_vrname = args["vrouter"]
action = args["action"]
if action != "disable" and action != "enable":
    print("Invalid action, it can either be disable or enable")
    exit(0)


################
# UTIL FUNCTIONS
################

def run_cmd(cmd, ignore_err=False):
    m_cmd = "cli --quiet --no-login-prompt --user network-admin:test123 " + cmd
    if show_only and "-show" not in cmd:
        print("### " + cmd)
        return
    try:
        proc = subprocess.Popen(m_cmd, shell=True, stdout=subprocess.PIPE)
        output = proc.communicate()[0]
        if not ignore_err and \
           proc.returncode and \
           proc.returncode not in ignore_err_list:
            print("Failed running cmd %s" % m_cmd)
            print("Retrying in 5 seconds....")
            sys.stdout.flush()
            time.sleep(5)
            proc = subprocess.Popen(m_cmd, shell=True, stdout=subprocess.PIPE)
            output = proc.communicate()[0]
            if proc.returncode:
                print("Failed again... Giving up !")
                exit(1)
        return output.strip().split('\n')
    except:
        print("Failed running cmd %s" % m_cmd)
        exit(0)


def sleep(sec):
    if not show_only:
        time.sleep(sec)


def _print(msg, end="nl", must_show=False):
    if not msg: 
        print("")
    elif must_show or not show_only:
        if end == "nl":
            print(msg)
        else:
            print(msg, end='')
    else:
        pass
################

existing_vrouters = []
vrouter_info = run_cmd("vrouter-show format name parsable-delim ,")
for vinfo in vrouter_info:
    if not vinfo:
        break
    existing_vrouters.append(vinfo)

if g_vrname not in existing_vrouters:
    _print("vrouter not found")
    exit(0)

intf_info = run_cmd("vrouter-interface-show vrouter-name %s"
                   "format nic parsable-delim ," % (g_vrname))
for intf in intf_info:
    if not intf:
        _print("No vrouter interfaces found")
        exit(0)
    _, nic = intf.split(',')
    _print("vRouter:%s, NIC:%s, Action:%s" % (g_vrname, nic, action), end="")
    sys.stdout.flush()
    if action == "disable":
        run_cmd("vrouter-interface-modify vrouter-name %s nic %s nic-disable" % (g_vrname, nic))
    else:
        run_cmd("vrouter-interface-modify vrouter-name %s nic %s nic-enable" % (g_vrname, nic))
    _print("Done")
    sys.stdout.flush()
    sleep(1)
