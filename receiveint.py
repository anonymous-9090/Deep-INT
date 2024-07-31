import socket
import struct
import json
import time
import uuid
from datetime import datetime
import pymysql
import select

DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '123'
DB_NAME = 'network_data'
TABLE_NAME = 'network_packets'
PORT = 2222
# Define the lengths of the headers
SR_HDR_LEN = 64

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def create_table():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            device_no INT,
            port_type VARCHAR(50),
            global_timestamp BIGINT,
            qdepth INT,
            byte_count BIGINT,
            udp_port INT,
            timestamp DOUBLE,  -- Changed to DOUBLE to store floating-point timestamps
            packet_id VARCHAR(50),
            PRIMARY KEY (device_no, port_type)
        );
        """
        cursor.execute(sql)
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error while creating table: {e}")
    finally:
        cursor.close()
        connection.close()

def insert_data_to_db(device_data, shared_data):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        # Insert data
        sql = f"""
        INSERT INTO {TABLE_NAME} (
            device_no, port_type, global_timestamp, qdepth, byte_count, udp_port, timestamp, packet_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            global_timestamp = VALUES(global_timestamp),
            qdepth = VALUES(qdepth),
            byte_count = VALUES(byte_count),
            udp_port = VALUES(udp_port),
            timestamp = VALUES(timestamp),
            packet_id = VALUES(packet_id)
        """
        # Create unique port_type for ingress and egress ports
        ingress_port_type = f"in{device_data['ingress_port']}"
        egress_port_type = f"out{device_data['egress_port']}"

        # Obtain current time as a floating-point Unix timestamp
        current_time = time.time()

        # Insert ingress data
        cursor.execute(sql, (
            device_data['device_no'],
            ingress_port_type,
            device_data['ingress_global_timestamp'],
            device_data['enq_qdepth'],
            device_data['ingress_byte_count'],
            shared_data['udp_port'],
            current_time,
            shared_data['packet_id']
        ))

        # Insert egress data
        cursor.execute(sql, (
            device_data['device_no'],
            egress_port_type,
            device_data['egress_global_timestamp'],
            device_data['deq_qdepth'],
            device_data['egress_byte_count'],
            shared_data['udp_port'],
            current_time,
            shared_data['packet_id']
        ))

        connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error while inserting to MySQL: {e}")
    finally:
        cursor.close()
        connection.close()

def read_bitmaps(file_path):
    with open(file_path, 'r') as file:
        bitmaps = [line.strip() for line in file.readlines()]
    print(f"Read bitmaps: {bitmaps}") 
    return bitmaps

def calculate_int_hdr_lengths(bitmaps):
    field_lengths = [8, 16, 16, 48, 48, 24, 24, 32, 32]
    int_hdr_lengths = []

    for bitmap in bitmaps:
        length = 8  # device_no
        for i, bit in enumerate(reversed(bitmap)):
            if bit == '1':
                length += field_lengths[i + 1]
        int_hdr_lengths.append(length)
    print(f"Calculated INT header lengths: {int_hdr_lengths}")
    return int_hdr_lengths

def parse_sr_header(data):
    if len(data) < SR_HDR_LEN:
        print(f"Error: Data length {len(data)} is less than SR header length {SR_HDR_LEN}")
        return None
    sr_header = struct.unpack('!16I', data[:SR_HDR_LEN])
    print(f"Parsed SR header: {sr_header}")
    return {
        "routingList": sr_header[0]
    }

def parse_int_headers(data, int_hdr_lengths, bitmaps):
    int_headers = []
    offset = SR_HDR_LEN

    for hdr_index, hdr_length in enumerate(int_hdr_lengths):
        if len(data) * 8 < offset * 8 + hdr_length:
            print(f"Error: Data length {len(data)} is less than expected length {offset * 8 + hdr_length} bits")
            continue

        int_header_data = data[offset:]
        bit_pos = 0

        def extract_bits(data, start, length):
            value = 0
            for i in range(length):
                byte_index = (start + i) // 8
                bit_index = (start + i) % 8
                bit_value = (data[byte_index] >> (7 - bit_index)) & 1
                value = (value << 1) | bit_value
            return value

        int_header = {}
        field_names = [
            "device_no", "ingress_port", "egress_port",
            "ingress_global_timestamp", "egress_global_timestamp",
            "enq_qdepth", "deq_qdepth",
            "ingress_byte_count", "egress_byte_count"
        ]
        field_lengths = [8, 16, 16, 48, 48, 24, 24, 32, 32]

        int_header["device_no"] = extract_bits(int_header_data, bit_pos, 8)
        print(f"Parsed device_no: {int_header['device_no']} at bit position {bit_pos}")
        bit_pos += 8

        bitmap = bitmaps[hdr_index % len(bitmaps)]
        for i, field in enumerate(field_names[1:], start=1):
            if bitmap[-i] == '1':
                field_length = field_lengths[i]
                int_header[field] = extract_bits(int_header_data, bit_pos, field_length)
                print(f"Parsed {field}: {int_header[field]} at bit position {bit_pos}")
                bit_pos += field_length
            else:
                int_header[field] = None
                print(f"Skipped {field}, set to 0")

        int_headers.append(int_header)
        offset += hdr_length // 8
    print(f"Parsed INT headers: {int_headers}")
    return int_headers

def save_to_file(data, filename='output.txt'):
    try:
        with open(filename, 'a') as file:
            file.write(json.dumps(data) + '\n')
        print(f"Saved data to {filename}")
    except Exception as e:
        print(f"Failed to save data to {filename}: {e}")

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))

    print(f"Waiting for packets on port {PORT}")

    bitmaps = read_bitmaps('bitmap.txt')
    int_hdr_lengths = calculate_int_hdr_lengths(bitmaps)

    while True:
        readable, _, _ = select.select([sock], [], [], 10)
        if not readable:
            print("No data received in 5 seconds, closing socket.")
            break
        data, addr = sock.recvfrom(65535)
        print(f"Received {len(data)} bytes from {addr}")
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        dt_object = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S.%f')
        epoch_time = dt_object.timestamp()
        print(f"Received {len(data)} bytes from {addr} at {epoch_time}")

        sr_header = parse_sr_header(data)
        if sr_header is None:
            continue

        int_headers = parse_int_headers(data, int_hdr_lengths, bitmaps)

        packet_data = {
            "sr_header": sr_header,
            "int_headers": int_headers,
            "udp_port": PORT,
            "timestamp": time.time(),
            "packet_id": str(uuid.uuid4())
        }

        # Save the packet data to the output file
        save_to_file(packet_data)
        try:
            shared_data = {
                'udp_port': packet_data['udp_port'],
                'timestamp': packet_data['timestamp'],
                'packet_id': packet_data['packet_id']
            }
            for device in packet_data['int_headers']:
                insert_data_to_db(device, shared_data)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
    if sock:
        sock.close()



if __name__ == "__main__":
    main()
