#! /usr/local/bin/python3
import sys
import subprocess
import time
import random


fixed_message_p1 = "0|Test "
fixed_message_p2 = "|PAN-OS|common=event-format-test|end|TRAFFIC|1|rt=$common=event-formatformatted-receive_time deviceExternalId=0002D01655 src=1.1.1.1 dst=2.2.2.2 sourceTranslatedAddress=1.1.1.1 destinationTranslatedAddress=3.3.3.3 cs1Label=Rule cs1=InternetDNS "
cisco_message = "Inbound TCP connection denied from 183.60.23.164/58098 to 131.107.193.171/23 flags SYN  on interface inet"


def send_cef_message_remote(ip, port, start_millis, message_to_send, is_cef, rfc5424):
    message = message_to_send + " Message=" + str(start_millis) + " Random =" + str(
        random.randint(0, 50000)) if is_cef is True else message_to_send
    if rfc5424 is False:
        command_tokens = ["logger", "-p", "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-d", "-n", str(ip)]
    else:
        command_tokens = ["logger", "--rfc5424", "-p",  "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-d", "-n", str(ip)]
    logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = logger.communicate()
    if e is None:
        return
    else:
        print("Error could not send cef message")


def send_cef_message_local(port, start_millis, message_to_send, is_cef, rfc5424):
    message = message_to_send + " Message=" + str(start_millis) + " Random =" + str(
        random.randint(0, 50000)) if is_cef is True else message_to_send
    if rfc5424 is False:
        command_tokens = ["logger", "-p", "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-n", "127.0.0.1"]
    else:
        command_tokens = ["logger", "--rfc5424", "-p",  "local4.warn", "-t", "CEF:" if is_cef is True else "%ASA-2-106001:", message, "-P", str(port), "-n", "127.0.0.1"]
    logger = subprocess.Popen(command_tokens, stdout=subprocess.PIPE)
    o, e = logger.communicate()
    if e is None:
        return
    else:
        print("Error could not send cef message")


def stream_message(ip, port, message_per_second, time_in_second, message_to_send, is_cef, rfc_5424):
    for curr_second in range(0, int(time_in_second)):
        start_millis = int(round(time.time() * 1000))
        print("Message per second: " + str(message_per_second))
        for curr_message in range(0, int(message_per_second)):
            if "127.0.0.1" in ip:
                send_cef_message_local(port, start_millis, message_to_send, is_cef=is_cef, rfc5424=rfc_5424)
            else:
                send_cef_message_remote(ip, port, start_millis, message_to_send, is_cef=is_cef, rfc5424=rfc_5424)
        end_millis = int(round(time.time() * 1000))
        time_send_took = end_millis - start_millis
        if time_send_took < 1000:
            time_to_sleep = float(1000 - time_send_took) / 1000
            time.sleep(time_to_sleep)
            print("stream")


def distribute_message(ip, port, amount, messages_per_second, message_to_send, is_cef):
    # time in seconds
    delta = 1000 / messages_per_second
    for index in range(0, amount):
        start_millis = int(round(time.time() * 1000))
        send_cef_message_remote(ip, port, start_millis, message_to_send, is_cef=is_cef)
        end_millis = int(round(time.time() * 1000))
        diff_millis = end_millis - start_millis
        sleep_time_millis = delta - diff_millis
        if sleep_time_millis > 0:
            print("sleeping for :" + str(sleep_time_millis))
            time.sleep(sleep_time_millis/1000)
            print("slept")


def main():
    start_millis = int(round(time.time() * 1000))
    if len(sys.argv) < 7:
        print("The script is expecting 4 arguments:")
        print("1) destination ip")
        print("2) destination port")
        print("3) amount of messages in second")
        print("4) amount of seconds")
        print("5) test index")
        print("6) CEF/CISCO")
        print("7) Optional - rfc5424")

        return
    else:
        ip = sys.argv[1]
        port = sys.argv[2]
        messages_per_second = sys.argv[3]
        amount_of_seconds = sys.argv[4]
        test_index = sys.argv[5]
        is_cef = True if "CEF" in sys.argv[6] else False

        if len(sys.argv) >= 7:
            rfc_5424 = True
        else:
            rfc_5424 = False
        message_to_send = (fixed_message_p1 + test_index + fixed_message_p2) if is_cef is True else cisco_message
        # distribute_message(ip, port, int(messages_per_second) * int(amount_of_seconds), int(messages_per_second), message_to_send)
        stream_message(ip, port, messages_per_second, amount_of_seconds, message_to_send, is_cef=is_cef, rfc_5424=rfc_5424)
        print("Done - " + str(int(messages_per_second) * int(amount_of_seconds)))
    end_millis = int(round(time.time() * 1000))
    print("Time[seconds]: " + str((end_millis-start_millis)/1000))

main()
