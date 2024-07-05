import socket
import os
import struct
import time
import select

ICMP_ECHO_REQUEST = 8

def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(id, sequence):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, sequence)
    data = struct.pack('d', time.time())
    my_checksum = checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, my_checksum, id, sequence)
    return header + data

def do_one_ping(dest_addr, id, sequence, timeout):
    icmp = socket.getprotobyname('icmp')
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error as e:
        print(f"Socket error: {e}")
        return None

    packet = create_packet(id, sequence)
    try:
        my_socket.sendto(packet, (dest_addr, 1))
        print(f"Packet sent to {dest_addr}")
    except socket.error as e:
        print(f"Send error: {e}")
        return None

    start_time = time.time()
    ready = select.select([my_socket], [], [], timeout)
    if ready[0] == []:
        print("Timeout waiting for reply")
        return None

    time_received = time.time()
    rec_packet, addr = my_socket.recvfrom(1024)
    print(f"Received packet from {addr}")

    # 打印接收到的数据包内容
    print(f"Received packet: {rec_packet}")

    icmp_header = rec_packet[20:28]
    type, code, checksum, packet_id, sequence = struct.unpack('bbHHh', icmp_header)
    if packet_id == id:
        bytes_in_double = struct.calcsize('d')
        time_sent = struct.unpack('d', rec_packet[28:28 + bytes_in_double])[0]
        return time_received - time_sent
    return None

def ping(host, timeout=1, count=4):
    dest = socket.gethostbyname(host)
    print(f'Pinging {dest} using Python:')
    id = os.getpid() & 0xFFFF
    min_rtt = float('inf')
    max_rtt = 0
    sum_rtt = 0
    sum_rtt_sq = 0
    received = 0
    for i in range(count):
        delay = do_one_ping(dest, id, i, timeout)
        if delay is None:
            print("Request timed out.")
        else:
            delay = delay * 1000
            print(f'Reply from {dest}: time={delay:.2f}ms')
            if delay < min_rtt:
                min_rtt = delay
            if delay > max_rtt:
                max_rtt = delay
            sum_rtt += delay
            sum_rtt_sq += delay * delay
            received += 1
        time.sleep(1)
    if received > 0:
        mean_rtt = sum_rtt / received
        variance = (sum_rtt_sq / received) - (mean_rtt * mean_rtt)
        stddev = variance ** 0.5
        print(f"\n--- {host} ping statistics ---")
        print(f"{count} packets transmitted, {received} received, {100.0 * (count - received) / count:.1f}% packet loss")
        print(f"rtt min/avg/max/mdev = {min_rtt:.2f}/{mean_rtt:.2f}/{max_rtt:.2f}/{stddev:.2f} ms")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <hostname>")
    else:
        ping(sys.argv[1])
