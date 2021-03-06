#!/usr/bin/env python3

import os
import sys
MYPATH = os.path.dirname(os.path.abspath(__file__))
SOCKET_CLIENT_DIR_PATH = os.path.join(MYPATH, 'tools/')
API_DIR_PATH = os.path.join(MYPATH, 'tools/MicrOSDevEnv/')
APP_DIR = os.path.join(MYPATH, 'apps')
sys.path.append(API_DIR_PATH)
sys.path.append(SOCKET_CLIENT_DIR_PATH)
sys.path.append(APP_DIR)
import argparse
import MicrOSDevEnv
import socketClient
import LocalMachine

def arg_parse():
    parser = argparse.ArgumentParser(prog="MicrOS dev toolkit - deploy, connect, update, etc.", \
                                            description="CMDline wrapper for {}\n and for {}".format( \
                                            os.path.join(API_DIR_PATH, 'MicrOSDevEnv.py'), \
                                            os.path.join(SOCKET_CLIENT_DIR_PATH, 'socketClient.py')))

    base_group = parser.add_argument_group("Base commands")
    base_group.add_argument("-m", "--make", action="store_true", help="Erase & Deploy & Precompile (MicrOS) & Install (MicrOS)")
    base_group.add_argument("-r", "--update", action="store_true", help="Update/redeploy connected (usb) MicrOS. \
                                                                    - node config will be restored")
    base_group.add_argument("-c", "--connect", action="store_true", help="Connect via socketclinet")
    base_group.add_argument("-p", "--connect_parameters", type=str, help="Parameters for connection in non-interactivve mode.")
    base_group.add_argument("-a", "--applications", type=str, help="List/Execute frontend applications. [list]")
    base_group.add_argument("-stat", "--node_status", action="store_true", help="Show all available MicrOS devices status data.")

    dev_group = parser.add_argument_group("Development & Deployment & Connection")
    dev_group.add_argument("-e", "--erase", action="store_true", help="Erase device")
    dev_group.add_argument("-d", "--deploy", action="store_true", help="Deploy micropython")
    dev_group.add_argument("-i", "--install", action="store_true", help="Install MicrOS on micropython")
    dev_group.add_argument("-l", "--list_devs_n_bins", action="store_true", help="List connected devices & micropython binaries.")
    dev_group.add_argument("-cc", "--cross_compile_micros", action="store_true", help="Cross Compile MicrOS system [py -> mpy]")
    dev_group.add_argument("-v", "--version", action="store_true", help="Get micrOS version - repo + connected device.")
    dev_group.add_argument("-ls", "--node_ls", action="store_true", help="List micrOS node filesystem content.")
    dev_group.add_argument("-u", "--connect_via_usb", action="store_true", help="Connect via serial port - usb")
    dev_group.add_argument("-b", "--backup_node_config", action="store_true", help="Backup usb connected node config.")
    dev_group.add_argument("-f", "--force_update", action="store_true", help="Force mode for -r/--update")
    dev_group.add_argument("-s", "--search_devices", action="store_true", help="Search devices on connected wifi network.")

    toolkit_group = parser.add_argument_group("Toolkit development")
    toolkit_group.add_argument("--dummy", action="store_true", help="Skip subshell executions - for API logic test.")

    args = parser.parse_args()

    if args.force_update:
        args.update = True

    return args


def list_devs_n_bins(api_obj):
    dev_list = api_obj.micros_devices
    bin_list = api_obj.micropython_bins_list
    print("Devices:")
    for dev in dev_list:
        print("\t{}".format(dev))
    print("Micropython binaries:")
    for bin_ in bin_list:
        print("\t{}".format(bin_))


def make(api_obj):
    api_obj.deploy_micros()


def erase(api_obj):
    api_obj.erase_dev()


def deploy(api_obj):
    api_obj.deploy_micropython_dev()


def install(api_obj):
    api_obj.put_micros_to_dev()


def connect(args=None):
    if args is not None and len(args) != 0:
        socketClient.run(arg_list=args.split(' '))
    else:
        socketClient.run(arg_list=[])


def node_status():
    socketClient.run(arg_list=['--stat'])


def search_devices():
    socketClient.ConnectionData.filter_MicrOS_devices()


def precompile_micrOS(api_obj):
    api_obj.precompile_micros()


def connect_via_usb(api_obj):
    api_obj.connect_dev()


def get_MicrOS_version(api_obj):
    print(api_obj.get_micrOS_version())


def update_micrOS_on_node(api_obj, force=False):
    api_obj.update_micros_via_usb(force=force)


def node_ls(api_obj):
    api_obj.list_micros_filesystem()


def backup_node_config(api_obj):
    api_obj.backup_node_config()


def applications(app):
    app_list = [app for app in LocalMachine.FileHandler.list_dir(APP_DIR) if app.endswith('.py') and not app.startswith('Template')]
    if app.lower() == 'list' or app.lower() == 'help' or app.lower() == '-':
        for index, app_content in enumerate(app_list):
            print("\t[{index}] - {appc}".format(index=index, appc=app_content))
        index = input("[QUESTION] Select Appllication by index: ")
        try:
            index = int(index)
            app_name = app_list[index].replace('_app.py', '')
        except:
            app_name = None
        if app_name is not None:
            __execute_app(app_name)
    elif app in [app_name.replace('_app.py', '') for app_name in app_list]:
        print("[ RUN ] {}".format(app))
        __execute_app(app)
    else:
        print("[ APP ] {} was not found.".format(app))

def __execute_app(app_name, app_postfix='_app'):
    app_name = "{}{}".format(app_name, app_postfix)
    print("[APP] import {}".format(app_name))
    exec("import {}".format(app_name))
    print("[APP] {}.app()".format(app_name))
    return_value = eval("{}.app()".format(app_name))
    if return_value is not None:
        print(return_value)

if __name__ == "__main__":
    cmd_args = arg_parse()

    # Socket interface module
    if cmd_args.applications:
        applications(cmd_args.applications)
        sys.exit(0)

    if cmd_args.connect:
        connect(args=cmd_args.connect_parameters)
        sys.exit(0)

    if cmd_args.search_devices:
        search_devices()
        sys.exit(0)

    # Create API object ()
    if cmd_args.dummy:
        api_obj = MicrOSDevEnv.MicrOSDevTool(dummy_exec=True)
    else:
        api_obj = MicrOSDevEnv.MicrOSDevTool()

    # Get all connected node status
    if cmd_args.node_status:
        node_status()

    # Commands
    if cmd_args.list_devs_n_bins:
        list_devs_n_bins(api_obj)

    if cmd_args.make:
        make(api_obj)

    if cmd_args.erase:
        erase(api_obj)

    if cmd_args.deploy:
        deploy(api_obj)

    if cmd_args.install:
        install(api_obj)

    if cmd_args.cross_compile_micros:
        precompile_micrOS(api_obj)

    if cmd_args.version:
        get_MicrOS_version(api_obj)

    if cmd_args.update:
        update_micrOS_on_node(api_obj, force=cmd_args.force_update)

    if cmd_args.node_ls:
        node_ls(api_obj)

    if cmd_args.backup_node_config:
        backup_node_config(api_obj)

    if cmd_args.connect_via_usb:
        connect_via_usb(api_obj)

    sys.exit(0)

